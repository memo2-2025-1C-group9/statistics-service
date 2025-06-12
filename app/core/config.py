from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )

    ENVIRONMENT: str
    HOST: str
    PORT: int

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    PGSSLMODE: str = "require"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.PGSSLMODE}"

    AUTH_SERVICE_URL: str
    COURSES_SERVICE_URL: str

    SERVICE_USERNAME: str
    SERVICE_PASSWORD: str


try:
    settings = Settings()
    logger.debug("Configuración cargada exitosamente")
    logger.debug(f"HOST: {settings.HOST}")
    logger.debug(f"PORT: {settings.PORT}")
    logger.debug(f"ENVIRONMENT: {settings.ENVIRONMENT}")

except Exception as e:
    logger.error(f"Error al cargar la configuración: {str(e)}")
    raise
