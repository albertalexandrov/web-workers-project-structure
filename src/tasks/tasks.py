from fastapi.templating import Jinja2Templates
from keycloak_fastapi_partners.auth.connection import UserStore
from partners_utils.faststream.redis import publish_many
from partners_utils.mails import send_mail
from taskiq_faststream import BrokerWrapper

from app.constants import ADDRESS_PROGRAMS_LIST_URL_FROM_ORIGIN
from app.db.connection import DBConnector
from app.db.filters.ace import ProposalExportFilter
from app.db.repositories.ace import (
    AceFileRepository,
    AceProductRepository,
    AceRepository,
    AceTypeRepository,
    AttachmentRepository,
    ProductRepository,
    ProposalRepository,
    RequestRepository,
    StateRepository,
)
from app.services.integrations.ace import AceClient
from app.settings import settings
from app.storage import AceS3Storage
from app.tasks.brokers import redis_broker
from app.tasks.constants import ChannelRedisEnum
from app.tasks.logging import logger
from app.utils.notifications import notify_about_proposal_via_bell

templates = Jinja2Templates(directory="app/mail_templates")
mail_export_proposals = templates.get_template("export_proposals.html")


@redis_broker.subscriber(ChannelRedisEnum.DEACTIVATED.value)
async def task_deactivate_requests() -> None:
    """
    Периодическая задача на деактивацию запросов на ДТО.
    Запускается раз в месяц, первого числа.
    """
    logger.info("Начинается деактивация запросов на ДТО.")
    async with DBConnector.get_session() as session:
        repository = RequestRepository(session)
        await repository.deactivate_requests()
    logger.info("Деактивация запросов на ДТО завершена.")


@redis_broker.subscriber(ChannelRedisEnum.EMAIL_ROUTING.value)
async def task_email_routing() -> None:
    """
    Периодическая задача на проверку пользователей по признаку активности.
    Запускается раз в день.
    """
    logger.info("Начинается проверку пользователей по признаку активности.")
    from app.services.integrations.services import EmailRoutingService

    async with DBConnector.get_session() as session:
        cheker = EmailRoutingService(session=session)
        await cheker.run()
    logger.info("Проверка закончена.")


@redis_broker.subscriber(ChannelRedisEnum.RESEND_PROPOSAL.value)
async def task_resend_proposal(message) -> None:
    """
    Периодическая задача на переотправку необработанных заявок.
    Запускается раз в 120 минут.

    Принимает следующие параметры через message от брокера:
      - raise_exception: Указывает, будет ли вызвано исключение
                         в resend_unprocessed_proposals в случае провала повторной
                         отправки заявки.
    """
    from app.services.ace import ProposalService

    raise_exception = message.get("raise_exception", False)

    logger.info("Начинается проверка необработанных заявок.")
    async with DBConnector.get_session() as session:
        proposal_service = ProposalService(
            request_repository=RequestRepository(session),
            state_repository=StateRepository(session),
            proposal_repository=ProposalRepository(session),
            ace_type_repository=AceTypeRepository(session),
            ace_repository=AceRepository(session),
            product_repository=ProductRepository(session),
            ace_product_repository=AceProductRepository(session),
        )
        await proposal_service.resend_unprocessed_proposals(raise_exception=raise_exception)
    logger.info("Проверка необработанных заявок закончена.")


@redis_broker.subscriber(ChannelRedisEnum.DOWNLOAD_PROPOSAL_FILES.value)
async def download_files_dto() -> None:
    """
    Периодическая задача скачивания файла адресной программы
    Запускается в первую минуту каждого часа
    Как может случиться так, что файл не будет загружен с первого раза?
    Такое может произойти, если, например, сервис ДТО не был доступен
    """
    logger.info("Начинается загрузка файлов адресных программ.")
    async with DBConnector.get_session() as session:
        proposal_repository = ProposalRepository(session)
        proposal_ids = await proposal_repository.get_proposal_ids_to_download_file_from_ace()
        await publish_many(
            broker=redis_broker,
            messages=proposal_ids,
            channel=str(ChannelRedisEnum.DOWNLOAD_PROPOSAL_FILE.value),
            is_closed=False,
        )
    logger.info(
        f"Задача загрузки адресных программ завершена. "
        f"Всего было отправлено в загрузку {len(proposal_ids)} адресных программ"
    )


@redis_broker.subscriber(ChannelRedisEnum.DOWNLOAD_PROPOSAL_FILE.value)
async def download_file_dto(proposal_id: int) -> None:
    """
    Асинхронная таска загрузки файла адресной программы.
    """
    from app.services.ace import AttachmentService

    ace_client = AceClient()
    async with DBConnector.get_session() as session:
        proposal_repository = ProposalRepository(session)
        attachment_repository = AttachmentRepository(session)
        ace_repository = AceRepository(session)
        attachment_service = AttachmentService(
            attachment_repository=attachment_repository, ace_repository=ace_repository
        )
        proposal = await proposal_repository.get_proposal(proposal_id)
        dto_file_id = proposal.dto_file_id
        logger.info(f"Скачивание файла адресной программы заявки Proposal.id={proposal} (dto_file_id={dto_file_id})")
        upload_file = await ace_client.download_proposal_file(dto_file_id)
        attachment = await attachment_service.create_attachment(upload_file)
        logger.info(f"Файл адресной программы заявки Proposal.id={proposal} скачан (вложение id={attachment.id})")
        proposal.file = attachment
    if proposal.dto_file_updated:
        logger.info(f"Уведомляем об обновлении адресной программы заявки Proposal.id={proposal.id}")
        # уведомление в Колокольчик
        headline = "Изменение Адресной программы"
        text = (
            f"По запросу № {proposal.request.dto_id} изменена Адресная программа. "
            f"Посмотреть запрос {ADDRESS_PROGRAMS_LIST_URL_FROM_ORIGIN}"
        )
        emails = await notify_about_proposal_via_bell(proposal, headline, text)
        # уведомление по email
        subject = f"Изменение Адресной программы по запросу № {proposal.request.dto_id}"
        body = (
            f"<p>По запросу № {proposal.request.dto_id} изменена Адресная программа.</p>"
            "<p>Чтобы скачать обновленную Адресную программу:</p>"
            "<p><ol><li>1. На портале Partner перейдите в раздел Запросы на ДТО.</li>"
            "<li>2. На вкладке Адресная программа найдите запрос с помощью фильтра по номеру.</li>"
            "<li>3. В окне запроса нажмите Скачать Адресную программу.</li></ol></p>"
        )
        await send_mail(subject=subject, body=body, is_html=True, recipients=emails)
        emails_str = ", ".join(emails)
        logger.info(
            f"Уведомление в почту об обновлении адресной программы Proposal.id={proposal_id} "
            f"отправлено на email-ы: {emails_str}"
        )


@redis_broker.subscriber(ChannelRedisEnum.NOTIFY_DECISION_ON_PROPOSAL_RECEIVED.value)
async def notify_decision_on_proposal_received(proposal_id: int) -> None:
    """
    Асинхронная таска, которая уведомляет о получении решения по заявке (о получении адресной программы).
    """
    logger.info(f"Старт задачи на уведомление о получении решения по заявке Proposal.id={proposal_id}")
    async with DBConnector.get_session() as session:
        proposal_repository = ProposalRepository(session)
        proposal = await proposal_repository.get_proposal(proposal_id)
        # уведомление в Колокольчик
        headline = "Решение по заявке на размещение ДТО"
        text = (
            f"Получено решение по заявке на размещение "
            f"Дополнительного торгового оборудования № {proposal.request.dto_id}. "
            f"Посмотрите решение на вкладке «Адресная программа» ({ADDRESS_PROGRAMS_LIST_URL_FROM_ORIGIN})"
        )
        emails = await notify_about_proposal_via_bell(proposal, headline, text)
        # уведомление по email
        subject = f"Решение по заявке на размещение Дополнительного торгового оборудования № {proposal.request.dto_id}"
        body = (
            f"Ваша заявка на размещение Дополнительного торгового оборудования № {proposal.request.dto_id} рассмотрена. "
            "Вы можете посмотреть решение по заявке на портале Partner на вкладке "
            f'<a hre="{ADDRESS_PROGRAMS_LIST_URL_FROM_ORIGIN}">«Адресная программа»"</a>'
        )
        await send_mail(subject=subject, body=body, is_html=True, recipients=emails)
        emails_str = ", ".join(emails)
        logger.info(
            f"Уведомление в почту по решению по заявке Proposal.id={proposal_id} отправлено на email-ы: {emails_str}"
        )


@redis_broker.subscriber(ChannelRedisEnum.EXPORT_PROPOSALS.value)
async def task_export_proposals(message) -> None:
    """
    Задача для подготовки Excel файла с заявками и загрузки его в S3.
    """
    from app.services.ace import ProposalsExportExcelService

    user_id = message.get("user_id")
    logger.info(f"Старт задачи по выгрузке заявок в Excel для пользователя {user_id}")
    user = await UserStore.get_by_id(user_id)
    filter_data = message.get("filter_data")

    async with DBConnector.get_session() as session:
        filtering = ProposalExportFilter(
            **{
                "created_from": filter_data["created_at__date__gte"],
                "created_to": filter_data["created_at__date__lte"],
                "state_ids": filter_data["state_id__in"],
            }
        )
        proposal_service = ProposalsExportExcelService(
            ace_file_repository=AceFileRepository(session),
            repository_for_export=ProposalRepository(session),
            storage=AceS3Storage(),
        )
        ace_file = await proposal_service.export_for_task(filtering=filtering, user=user)

    # Уведомление по Email.
    subject = "Заявки на размещение ДТО"
    file_url = settings.origin + ace_file.file_url.replace("/api/internal", "/backend_dto")
    body = mail_export_proposals.render(
        file_link=file_url,
        expire_datetime=ace_file.expire_at.strftime("%d.%m.%Y %H:%M"),
    )
    await send_mail(subject=subject, body=body, is_html=True, recipients=[user.username])
    logger.info(f"Завершена задача по выгрузке заявок в Excel для пользователя {user_id}")


@redis_broker.subscriber(ChannelRedisEnum.DELETE_EXPIRED_ACE_FILES.value)
async def task_delete_expired_ace_files() -> None:
    """
    Задача по удалению просроченных ДТО файлов в S3.
    """
    from app.services.ace import AceFileService

    logger.info("Старт задачи по удалению просроченных ДТО файлов")
    async with DBConnector.get_session() as session:
        ace_file_repository = AceFileRepository(session)
        ace_files = await ace_file_repository.get_expired_ace_files()
        ace_file_service = AceFileService(ace_file_repository=ace_file_repository)
        for ace_file in ace_files:
            await ace_file_service.delete_file(ace_file=ace_file)
    logger.info("Завершена задача по удалению просроченных ДТО файлов")


taskiq_broker = BrokerWrapper(redis_broker)
