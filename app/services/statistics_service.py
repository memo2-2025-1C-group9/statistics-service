from app.schemas.statistics_schemas import UserStatisticsEvent, CourseStatisticsEvent
from app.services.courses_service import get_course_users
from sqlalchemy.orm import Session
from app.repositories.statistics_repository import (
    find_statistics_by_user_and_title,
    update_statistics,
    create_statistics,
)


async def process_user_event(db: Session, event: UserStatisticsEvent):
    # Buscar si ya existe una entrada para este usuario y tarea/examen
    existing_stat = find_statistics_by_user_and_title(
        db,
        user_id=event.id_user,
        titulo=event.data.titulo,
        tipo=event.notification_type,
    )

    if existing_stat:
        # Actualizar estadística existente
        if event.event == "Entregado":
            update_statistics(db, existing_stat, entregado=True)
        elif event.event == "Calificado":
            update_statistics(db, existing_stat, calificacion=event.data.nota)
    else:
        # Crear nueva estadística
        # Ver los distintos casos que me pueden llegar aca
        create_statistics(
            db,
            user_id=event.id_user,
            titulo=event.data.titulo,
            tipo=event.notification_type,
            entregado=event.data.entregado,
            calificacion=event.data.nota,
        )


async def process_course_event(db: Session, event: CourseStatisticsEvent):
    # Obtener usuarios del curso
    user_list = await get_course_users(event.id_course)

    # TODO: Crear estadísticas para cada estudiante
