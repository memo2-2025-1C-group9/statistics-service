from app.schemas.statistics_schemas import UserStatisticsEvent, CourseStatisticsEvent
from app.services.courses_service import get_course_users
from sqlalchemy.orm import Session
from app.repositories.statistics_repository import (
    find_statistics_by_user_and_assessment_id,
    update_statistics,
    create_statistics,
    get_average_grade,
    get_completion_stats,
)
from typing import Dict


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
        create_statistics(
            db,
            user_id=event.id_user,
            assessment_id=event.assessment_id,
            titulo=event.data.titulo,
            tipo=event.notification_type,
            entregado=True,
            calificacion=event.data.nota,
            course_id=event.course_id,
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
            update_statistics(db, existing_stat, titulo=event.data.titulo)
        else:
            create_statistics(
                db,
                user_id=id_user,
                assessment_id=event.assessment_id,
                titulo=event.data.titulo,
                tipo=event.notification_type,
                entregado=False,
                course_id=event.id_course,
            )


async def get_global_statistics(db: Session):
    # Obtener promedio de calificaciones
    avg_grade = get_average_grade(db)

    # Obtener estadisticas de finalizacion
    total_assignments, completed_assignments = get_completion_stats(db)

    completion_rate = (
        (completed_assignments / total_assignments * 100)
        if total_assignments > 0
        else 0
    )

    return {
        "promedio_calificaciones": round(avg_grade, 2),
        "tasa_finalizacion": round(completion_rate, 2),
        "total_asignaciones": total_assignments,
        "asignaciones_completadas": completed_assignments,
    }


async def get_user_statistics(db: Session, user_id: int, course_id: str):
    # Obtener promedio de calificaciones del usuario
    avg_grade = get_average_grade(db, user_id=user_id, course_id=course_id)

    # Obtener estadisticas de finalizacion
    total_assignments, completed_assignments = get_completion_stats(
        db, user_id=user_id, course_id=course_id
    )

    completion_rate = (
        (completed_assignments / total_assignments * 100)
        if total_assignments > 0
        else 0
    )

    return {
        "promedio_calificaciones": round(avg_grade, 2),
        "tasa_finalizacion": round(completion_rate, 2),
        "total_asignaciones": total_assignments,
        "asignaciones_completadas": completed_assignments,
        "course_id": course_id,
    }
