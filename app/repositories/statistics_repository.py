from sqlalchemy.orm import Session
from app.models.statistics_model import Statistics
from typing import Optional


def find_statistics_by_user_and_title(
    db: Session, user_id: int, titulo: str, tipo: str
) -> Optional[Statistics]:
    return (
        db.query(Statistics)
        .filter(
            Statistics.user_id == user_id,
            Statistics.titulo == titulo,
            Statistics.tipo == tipo,
        )
        .first()
    )


def update_statistics(
    db: Session,
    statistics: Statistics,
    entregado: bool = None,
    calificacion: float = None,
) -> Statistics:
    if entregado is not None:
        statistics.entregado = entregado
    if calificacion is not None:
        statistics.calificacion = calificacion
    db.commit()
    return statistics


def create_statistics(
    db: Session,
    user_id: int,
    titulo: str,
    tipo: str,
    entregado: bool,
    calificacion: Optional[float] = None,
) -> Statistics:
    new_stat = Statistics(
        user_id=user_id,
        titulo=titulo,
        tipo=tipo,
        entregado=entregado,
        calificacion=calificacion,
    )
    db.add(new_stat)
    db.commit()
    return new_stat
