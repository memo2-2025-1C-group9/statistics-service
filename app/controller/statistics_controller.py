from sqlalchemy.orm import Session
from app.schemas.statistics_schemas import (
    UserStatisticsEvent,
    CourseStatisticsEvent,
    ExportFilters,
)
from app.services.statistics_service import (
    process_user_event,
    process_course_event,
    get_global_statistics,
    get_course_detailed_statistics,
    get_user_detailed_statistics,
    export_statistics_to_excel,
)


def handle_save_user_statistics(db: Session, event: UserStatisticsEvent):
    return process_user_event(db, event)


async def handle_save_course_statistics(db: Session, event: CourseStatisticsEvent):
    return await process_course_event(db, event)


async def handle_get_global_statistics(db: Session):
    return await get_global_statistics(db)


async def handle_get_course_detailed_statistics(
    db: Session, course_id: str, start_date=None, end_date=None
):
    return await get_course_detailed_statistics(db, course_id, start_date, end_date)


async def handle_get_user_detailed_statistics(
    db: Session, user_id: int, course_id: str, start_date=None, end_date=None
):
    return await get_user_detailed_statistics(
        db, user_id, course_id, start_date, end_date
    )


async def handle_export_statistics_to_excel(db: Session, filters: ExportFilters):
    return await export_statistics_to_excel(db, filters)
