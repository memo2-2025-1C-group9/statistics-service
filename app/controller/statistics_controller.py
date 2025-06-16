from app.schemas.statistics_schemas import UserStatisticsEvent, CourseStatisticsEvent
from app.services.statistics_service import (
    process_user_event,
    process_course_event,
    get_global_statistics,
    get_user_statistics,
)
from sqlalchemy.orm import Session


def handle_save_user_statistics(db: Session, event: UserStatisticsEvent):
    return process_user_event(db, event)


async def handle_save_course_statistics(db: Session, event: CourseStatisticsEvent):
    return await process_course_event(db, event)


async def handle_get_global_statistics(db: Session):
    return await get_global_statistics(db)


async def handle_get_user_statistics(db: Session, user_id: int, course_id: int):
    return await get_user_statistics(db, user_id, course_id)
