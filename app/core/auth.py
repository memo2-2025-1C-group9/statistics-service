import os
import httpx
import logging
from typing import Optional
from functools import lru_cache
from dotenv import load_dotenv
from app.core.config import settings

logger = logging.getLogger(__name__)

load_dotenv()


class ServiceAuth:
    def __init__(self):
        self.base_url = settings.AUTH_SERVICE_URL
        self.access_token: Optional[str] = None
        self.service_username = os.getenv("SERVICE_USERNAME")
        self.service_password = os.getenv("SERVICE_PASSWORD")
        if not self.service_username:
            logger.error("SERVICE_USERNAME environment variable is not set")
            raise ValueError("SERVICE_USERNAME environment variable is required")

        if not self.service_password:
            logger.error("SERVICE_PASSWORD environment variable is not set")
            raise ValueError("SERVICE_PASSWORD environment variable is required")

    async def initialize(self) -> None:
        if not self.access_token:
            await self.login()

    async def login(self) -> Optional[str]:
        try:
            async with httpx.AsyncClient() as client:
                logger.info("Intentando autenticar servicio...")
                logger.debug(f"URL: {self.base_url}/api/v1/token/service")
                logger.debug(f"Username: {self.service_username}")

                response = await client.post(
                    f"{self.base_url}/api/v1/token/service",
                    data={
                        "username": self.service_username,
                        "password": self.service_password,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                logger.debug(
                    f"Respuesta del servicio: Status={response.status_code}, Body={response.text}"
                )

                if response.status_code == 200:
                    self.access_token = response.json()["access_token"]
                    logger.info("Servicio autenticado exitosamente")
                    return self.access_token
                else:
                    logger.error(
                        f"Error en la autenticación del servicio. Status: {response.status_code}"
                    )
                    logger.error(f"URL: {self.base_url}/token/service")
                    logger.error(f"Detalle del error: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error al intentar autenticar el servicio: {str(e)}")
            logger.error(f"URL: {self.base_url}/token/service")
            return None

    def get_token(self) -> Optional[str]:
        return self.access_token


@lru_cache()
def get_service_auth() -> ServiceAuth:
    return ServiceAuth()
