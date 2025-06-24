import logging
import traceback
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas.statistics_schemas import (
    UserStatisticsEvent,
    CourseStatisticsEvent,
    ExportFilters,
)
from app.db.dependencies import get_db
from app.controller.statistics_controller import (
    handle_save_user_statistics,
    handle_save_course_statistics,
    handle_get_global_statistics,
    handle_get_course_detailed_statistics,
    handle_get_user_detailed_statistics,
    handle_export_statistics_to_excel,
)
from app.controller.user_controller import handle_validate_user
from datetime import date
import io


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)

router = APIRouter()


# Estos son para registrar los eventos
@router.post("/user-statistics")
async def save_user_statistics(
    token: Annotated[str, Depends(oauth2_scheme)],
    event: UserStatisticsEvent,
    db: Session = Depends(get_db),
):
    try:
        try:
            await handle_validate_user(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        await handle_save_user_statistics(db, event)

        return {
            "success": True,
            "message": "Estadística de usuario procesada correctamente",
        }
    except HTTPException:
        raise

    except Exception as e:
        logging.error(
            f"Exception no manejada al intentar guardar la estadistica para usuario: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


# Estos son para registrar los eventos
@router.post("/course-statistics")
async def save_course_statistics(
    token: Annotated[str, Depends(oauth2_scheme)],
    event: CourseStatisticsEvent,
    db: Session = Depends(get_db),
):
    try:
        try:
            await handle_validate_user(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        await handle_save_course_statistics(db, event)

        return {
            "success": True,
            "message": "Estadísticas de curso procesadas correctamente",
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Exception no manejada al guardar la estadistica para curso: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/statistics/global")
async def get_global_statistics(db: Session = Depends(get_db)):
    try:
        return await handle_get_global_statistics(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Exception no manejada al obtener las estadisticas globales: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/statistics/course/{course_id}")
async def get_course_detailed_statistics(
    course_id: str,
    start_date: date = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    try:
        return await handle_get_course_detailed_statistics(
            db, course_id, start_date, end_date
        )
    except HTTPException as e:
        raise
    except Exception as e:
        logging.error(
            f"Exception no manejada al obtener las estadisticas del curso: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/statistics/user/{course_id}/{user_id}")
async def get_user_detailed_statistics(
    user_id: int,
    course_id: str,
    start_date: date = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    try:
        return await handle_get_user_detailed_statistics(
            db, user_id, course_id, start_date, end_date
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Exception no manejada al obtener las estadisticas del usuario: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.post("/statistics/export-excel")
async def export_statistics_to_excel(
    token: Annotated[str, Depends(oauth2_scheme)],
    filters: ExportFilters,
    db: Session = Depends(get_db),
):
    try:
        try:
            await handle_validate_user(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        output, filename = await handle_export_statistics_to_excel(db, filters)

        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(
            f"Exception no manejada al exportar estadisticas a Excel: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )
