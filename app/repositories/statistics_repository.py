from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.statistics_model import Statistics
from typing import Optional


def find_statistics_by_user_and_assessment_id(
    db: Session, user_id: int, assessment_id: str, tipo: str
) -> Optional[Statistics]:
    return (
        db.query(Statistics)
        .filter(
            Statistics.user_id == user_id,
            Statistics.assessment_id == assessment_id,
            Statistics.tipo == tipo,
        )
        .first()
    )


def update_statistics(
    db: Session,
    statistics: Statistics,
    titulo: str = None,
    entregado: bool = None,
    calificacion: float = None,
) -> Statistics:
    if titulo is not None:
        statistics.titulo = titulo
    if entregado is not None:
        statistics.entregado = entregado
    if calificacion is not None:
        statistics.calificacion = calificacion
    db.commit()
    db.refresh(statistics)
    return statistics


def create_statistics(
    db: Session,
    user_id: int,
    assessment_id: str,
    titulo: str,
    tipo: str,
    entregado: bool,
    calificacion: float = None,
    course_id: str = None,
) -> Statistics:
    statistics = Statistics(
        user_id=user_id,
        assessment_id=assessment_id,
        titulo=titulo,
        tipo=tipo,
        entregado=entregado,
        calificacion=calificacion,
        course_id=course_id,
    )
    db.add(statistics)
    db.commit()
    db.refresh(statistics)
    return statistics


def get_average_grade(
    db: Session,
    user_id: Optional[int] = None,
    course_id: Optional[str] = None,
    start_date=None,
    end_date=None,
):
    base_query = db.query(func.avg(Statistics.calificacion)).filter(
        Statistics.calificacion.isnot(None)
    )

    if user_id is not None:
        base_query = base_query.filter(Statistics.user_id == user_id)
    if course_id is not None:
        base_query = base_query.filter(Statistics.course_id == course_id)

    if start_date:
        base_query = base_query.filter(Statistics.date >= start_date)
    if end_date:
        base_query = base_query.filter(Statistics.date <= end_date)

    return base_query.scalar() or 0.0


def get_completion_stats(
    db: Session,
    user_id: Optional[int] = None,
    course_id: Optional[str] = None,
    start_date=None,
    end_date=None,
):
    base_query = db.query(Statistics)

    if user_id is not None:
        base_query = base_query.filter(Statistics.user_id == user_id)
    if course_id is not None:
        base_query = base_query.filter(Statistics.course_id == course_id)

    if start_date:
        base_query = base_query.filter(Statistics.date >= start_date)
    if end_date:
        base_query = base_query.filter(Statistics.date <= end_date)

    total = base_query.count()
    completed = base_query.filter(Statistics.entregado == True).count()

    return total, completed


def get_course_statistics(db: Session, course_id: str, start_date=None, end_date=None):
    query = db.query(Statistics).filter(Statistics.course_id == course_id)
    
    if start_date:
        query = query.filter(Statistics.date >= start_date)
    if end_date:
        query = query.filter(Statistics.date <= end_date)
    
    return query.order_by(Statistics.date.desc()).all()


def get_user_course_statistics(
    db: Session, user_id: int, course_id: str, start_date=None, end_date=None
):
    query = db.query(Statistics).filter(
        Statistics.user_id == user_id,
        Statistics.course_id == course_id,
    )

    if start_date:
        query = query.filter(Statistics.date >= start_date)
    if end_date:
        query = query.filter(Statistics.date <= end_date)
    
    return query.order_by(Statistics.date.desc()).all()
