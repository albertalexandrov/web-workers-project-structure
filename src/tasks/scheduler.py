from taskiq.schedule_sources import LabelScheduleSource
from taskiq_faststream import StreamScheduler

from app.settings import TZ
from app.tasks.constants import ChannelRedisEnum
from app.tasks.tasks import taskiq_broker

taskiq_broker.task(
    message={},
    channel=ChannelRedisEnum.DEACTIVATED.value,
    schedule=[{"cron": "1 0 1 * *", "cron_offset": TZ, "time": None}],
)

taskiq_broker.task(
    message={},
    channel=ChannelRedisEnum.EMAIL_ROUTING.value,
    schedule=[{"cron": "0 1 * * *", "cron_offset": TZ, "time": None}],
)

taskiq_broker.task(
    message={},
    channel=ChannelRedisEnum.RESEND_PROPOSAL.value,
    # Каждые 120 минут.
    schedule=[{"cron": "0 */2 * * *", "cron_offset": TZ, "time": None}],
)

taskiq_broker.task(
    message={},
    channel=ChannelRedisEnum.DOWNLOAD_PROPOSAL_FILES.value,
    schedule=[{"cron": "1 * * * *", "cron_offset": TZ, "time": None}],
)

taskiq_broker.task(
    message={},
    channel=ChannelRedisEnum.DELETE_EXPIRED_ACE_FILES.value,
    schedule=[{"cron": "0 1 * * *", "cron_offset": TZ, "time": None}],
)

scheduler = StreamScheduler(
    broker=taskiq_broker,
    sources=[LabelScheduleSource(taskiq_broker)],
)
