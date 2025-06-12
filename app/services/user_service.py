from fastapi import HTTPException
from app.core.config import settings
import httpx
import logging


async def validate_user(token: str):
    """
    Valida al usuario con el auth service y devuelve el id del usuario.
    """
    # Llamar al auth service para validar el token
    async with httpx.AsyncClient() as client:
        try:
            logging.info(f"Validando identidad del usuario con el token: {token}...")

            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/me/",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                logging.info("Token valido")
                user_data = response.json()
                user_id = user_data.get("id")
                return user_id
            raise HTTPException(
                status_code=response.status_code,
                detail="Token inválido o expirado",
            )

        except httpx.RequestError as e:
            logging.error(f"Error al conectar con el servicio de usuarios: {str(e)}")
            logging.error(f"URL: {settings.AUTH_SERVICE_URL}/me/")
            raise HTTPException(
                status_code=500,
                detail="Error al conectar con el servicio de usuarios",
            )
