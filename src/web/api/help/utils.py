from candidates_for_external_lib.utils.time import utcnow
from models import Section, Subsection
from models.help import ReferenceInfoStatus


def is_published_instance(new_status: str, instance: Section | Subsection) -> bool:
    already_published = not new_status and instance.status == ReferenceInfoStatus.published
    will_be_published = new_status == ReferenceInfoStatus.published
    return already_published or will_be_published


def subsection_has_content(subsection: Subsection) -> bool:
    articles_content = subsection.article_content
    if not articles_content:
        return False
    return any(content.has_content for content in articles_content)


def is_single_subsection(subsection: Subsection) -> bool:
    return len(subsection.section.subsections) == 1


def delete_section(section: Section) -> None:
    deleted_at = utcnow()
    section.update(deleted_at=deleted_at, status=ReferenceInfoStatus.unpublished)
    for ss in section.subsections:
        ss.update(status=ReferenceInfoStatus.unpublished, deleted_at=deleted_at)
