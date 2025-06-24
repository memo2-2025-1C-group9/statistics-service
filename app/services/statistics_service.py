from fastapi import HTTPException
from app.schemas.statistics_schemas import (
    UserStatisticsEvent,
    CourseStatisticsEvent,
    ExportFilters,
)
from app.services.courses_service import get_course_users
from sqlalchemy.orm import Session
from app.repositories.statistics_repository import (
    find_statistics_by_user_and_assessment_id,
    update_statistics,
    create_statistics,
    get_average_grade,
    get_completion_stats,
    get_course_statistics,
    get_user_course_statistics,
    get_all_statistics_with_filters,
)
import pandas as pd
import io
from datetime import datetime


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
        raise HTTPException(
            status_code=404,
            detail="No se encontró una estadística existente para este usuario y tarea/examen.",
        )


async def process_course_event(db: Session, event: CourseStatisticsEvent):
    # Obtener usuarios del curso
    user_list = await get_course_users(event.course_id)

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
                course_id=event.course_id,
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


async def get_course_detailed_statistics(
    db: Session, course_id: str, start_date=None, end_date=None
):
    avg_grade = get_average_grade(
        db, course_id=course_id, start_date=start_date, end_date=end_date
    )

    # Obtener estadisticas de finalizacion
    total_assignments, completed_assignments = get_completion_stats(
        db, course_id=course_id, start_date=start_date, end_date=end_date
    )

    completion_rate = (
        (completed_assignments / total_assignments * 100)
        if total_assignments > 0
        else 0
    )
    statistics = get_course_statistics(db, course_id, start_date, end_date)
    return {
        "promedio_calificaciones": round(avg_grade, 2),
        "tasa_finalizacion": round(completion_rate, 2),
        "total_asignaciones": total_assignments,
        "asignaciones_completadas": completed_assignments,
        "course_id": course_id,
        "logs": [
            {
                "id": stat.id,
                "user_id": stat.user_id,
                "course_id": stat.course_id,
                "titulo": stat.titulo,
                "tipo": stat.tipo,
                "entregado": stat.entregado,
                "calificacion": stat.calificacion,
                "assessment_id": stat.assessment_id,
                "fecha": stat.date.isoformat() if stat.date else None,
            }
            for stat in statistics
        ],
    }


async def get_user_detailed_statistics(
    db: Session, user_id: int, course_id: str, start_date=None, end_date=None
):
    avg_grade = get_average_grade(
        db,
        user_id=user_id,
        course_id=course_id,
        start_date=start_date,
        end_date=end_date,
    )

    total_assignments, completed_assignments = get_completion_stats(
        db,
        user_id=user_id,
        course_id=course_id,
        start_date=start_date,
        end_date=end_date,
    )
    completion_rate = (
        (completed_assignments / total_assignments * 100)
        if total_assignments > 0
        else 0
    )
    statistics = get_user_course_statistics(
        db, user_id, course_id, start_date, end_date
    )
    return {
        "promedio_calificaciones": round(avg_grade, 2),
        "tasa_finalizacion": round(completion_rate, 2),
        "total_asignaciones": total_assignments,
        "asignaciones_completadas": completed_assignments,
        "course_id": course_id,
        "logs": [
            {
                "id": stat.id,
                "user_id": stat.user_id,
                "course_id": stat.course_id,
                "titulo": stat.titulo,
                "tipo": stat.tipo,
                "entregado": stat.entregado,
                "calificacion": stat.calificacion,
                "assessment_id": stat.assessment_id,
                "fecha": stat.date.isoformat(),
            }
            for stat in statistics
        ],
    }


async def export_statistics_to_excel(db: Session, filters: ExportFilters):
    statistics = get_all_statistics_with_filters(
        db,
        user_id=filters.user_id,
        course_id=filters.course_id,
        start_date=filters.start_date,
        end_date=filters.end_date,
    )

    if not statistics:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron estadísticas con los filtros especificados",
        )

    # Convertir a DataFrame
    data = []
    for stat in statistics:
        data.append(
            {
                "ID": stat.id,
                "ID Usuario": stat.user_id,
                "ID Curso": stat.course_id,
                "Título": stat.titulo,
                "Tipo": stat.tipo,
                "Entregado": "Sí" if stat.entregado else "No",
                "Calificación": stat.calificacion
                if stat.calificacion is not None
                else "Sin calificar",
                "ID Evaluación": stat.assessment_id,
                "Fecha": stat.date.strftime("%Y-%m-%d %H:%M:%S")
                if stat.date
                else "Sin fecha",
            }
        )

    df = pd.DataFrame(data)

    # Crear archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Estadísticas", index=False)

        # Ajustar ancho de columnas
        worksheet = writer.sheets["Estadísticas"]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)

    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"estadisticas_{timestamp}.xlsx"

    return output, filename
