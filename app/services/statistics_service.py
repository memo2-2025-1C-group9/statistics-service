from app.schemas.statistics_schemas import UserStatisticsEvent, CourseStatisticsEvent
from app.services.courses_service import get_course_users
from sqlalchemy.orm import Session
from app.repositories.statistics_repository import (
    find_statistics_by_user_and_assessment_id,
    update_statistics,
    create_statistics,
)


async def process_user_event(db: Session, event: UserStatisticsEvent):
    # Buscar si ya existe una entrada para este usuario y tarea/examen
    existing_stat = find_statistics_by_user_and_assessment_id(
        db,
        user_id=event.id_user,
        assessment_id=event.assessment_id,
        tipo=event.notification_type,
    )

    if existing_stat:
        # Actualizar estadística existente
        if event.event == "Entregado":
            update_statistics(db, existing_stat, entregado=True)
        elif event.event == "Calificado":
            # Si es calificado es porque ya se entregó
            update_statistics(
                db, existing_stat, entregado=True, calificacion=event.data.nota
            )
    else:
        # Crear nueva estadística
        # Ver los distintos casos que me pueden llegar aca
        # Siempre deberia existir en este punto, un usuario no puede crear la tarea o examen
        create_statistics(
            db,
            user_id=event.id_user,
            assessment_id=event.assessment_id,
            titulo=event.data.titulo,
            tipo=event.notification_type,
            entregado=True,
            calificacion=event.data.nota,  # Este puede estar o no
        )


async def process_course_event(db: Session, event: CourseStatisticsEvent):
    # Obtener usuarios del curso
    user_list = await get_course_users(event.id_course)

    for id_user in user_list:
        existing_stat = find_statistics_by_user_and_assessment_id(
            db,
            user_id=id_user,
            assessment_id=event.assessment_id,
            tipo=event.notification_type,
        )

        if existing_stat:
            update_statistics(
                db, existing_stat, titulo=event.data.titulo
            )
        else:
            create_statistics(
                db,
                user_id=id_user,
                assessment_id=event.assessment_id,
                titulo=event.data.titulo,
                tipo=event.notification_type,
                entregado=False,
            )
