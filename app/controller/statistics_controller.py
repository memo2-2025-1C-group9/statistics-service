from sqlalchemy.orm import Session
from app.schemas.statistics_schemas import UserStatisticsEvent, CourseStatisticsEvent
from app.services.statistics_service import (
    process_user_event,
    process_course_event,
    get_global_statistics,
    get_course_detailed_statistics,
    get_user_detailed_statistics,
)


def handle_save_user_statistics(db: Session, event: UserStatisticsEvent):
    return process_user_event(db, event)


async def handle_save_course_statistics(db: Session, event: CourseStatisticsEvent):
    return await process_course_event(db, event)


async def handle_get_global_statistics(db: Session):
    return await get_global_statistics(db)


async def handle_get_course_detailed_statistics(db: Session, course_id: str):
    return await get_course_detailed_statistics(db, course_id)


async def handle_get_user_detailed_statistics(
    db: Session, user_id: int, course_id: str
):
    return await get_user_detailed_statistics(db, user_id, course_id)
