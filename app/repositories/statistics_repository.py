from sqlalchemy.orm import Session
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
    entregado: bool = None,
    calificacion: float = None,
    titulo: str = None,
) -> Statistics:
    if entregado is not None:
        statistics.entregado = entregado
    if calificacion is not None:
        statistics.calificacion = calificacion
    if titulo is not None:
        statistics.titulo = titulo
    db.commit()
    return statistics


def create_statistics(
    db: Session,
    user_id: int,
    assessment_id: str,
    titulo: str,
    tipo: str,
    entregado: bool,
    calificacion: Optional[float] = None,
) -> Statistics:
    new_stat = Statistics(
        user_id=user_id,
        assessment_id=assessment_id,
        titulo=titulo,
        tipo=tipo,
        entregado=entregado,
        calificacion=calificacion,
    )
    db.add(new_stat)
    db.commit()
    return new_stat
