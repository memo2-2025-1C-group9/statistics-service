import logging
import traceback
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.statistics_schemas import UserStatisticsEvent, CourseStatisticsEvent
from app.db.dependencies import get_db
from app.controller.statistics_controller import (
    handle_save_user_statistics,
    handle_save_course_statistics,
    handle_get_global_statistics,
    handle_get_course_detailed_statistics,
    handle_get_user_detailed_statistics,
)
from app.controller.user_controller import handle_validate_user


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
            "message": "Estadística de usuario procesada correctamente"
        }  # TODO: devolver otra cosa
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
            "message": "Estadísticas de curso procesadas correctamente"
        }  # TODO: devolver otra cosa
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
    db: Session = Depends(get_db),
):
    try:
        return await handle_get_course_detailed_statistics(db, course_id)
    except HTTPException as e:
        raise
    except Exception as e:
        logging.error(
            f"Exception no manejada al obtener las estadisticas del curso: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erroreee interno del servidor",
        )


@router.get("/statistics/user/{course_id}/{user_id}")
async def get_user_detailed_statistics(
    user_id: int,
    course_id: str,
    db: Session = Depends(get_db),
):
    try:
        return await handle_get_user_detailed_statistics(db, user_id, course_id)
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
