from app.schemas.statistics_schemas import UserStatisticsEvent, CourseStatisticsEvent
from app.services.statistics_service import process_user_event, process_course_event
from sqlalchemy.orm import Session


def handle_save_user_statistics(db: Session, event: UserStatisticsEvent):
    return process_user_event(db, event)


async def handle_save_course_statistics(db: Session, event: CourseStatisticsEvent):
    return process_course_event(db, event)
