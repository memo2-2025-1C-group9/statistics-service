from fastapi import HTTPException
from app.core.config import settings
import httpx
import logging


async def get_course_users(course_id: str):
    """
    Obtiene los datos del curso con el courses service y devuelve el listado de user_id del curso.
    """
    # Llamar al auth service para validar el token
    async with httpx.AsyncClient() as client:
        try:
            logging.info(
                f"Obteniendo usuarios del curso {course_id} desde {settings.COURSES_SERVICE_URL}/courses/{course_id}"
            )

            response = await client.get(
                f"{settings.COURSES_SERVICE_URL}/courses/{course_id}",
            )

            if response.status_code == 200:
                logging.info("Curso obtenido exitosamente")
                course_data = response.json()
                users_list = course_data.get("enrolled_users")
                return users_list
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al obtener los usuarios del curso: {response.text}",
            )

        except httpx.RequestError as e:
            logging.error(f"Error al conectar con el servicio de cursos: {str(e)}")
            logging.error(f"URL: {settings.COURSES_SERVICE_URL}/courses/{course_id}")
            raise HTTPException(
                status_code=500,
                detail="Error al conectar con el servicio de usuarios",
            )
