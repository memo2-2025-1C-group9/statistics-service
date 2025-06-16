from fastapi import FastAPI
from app.routes.statistics_routes import router as statistics_router
from app.db.base import Base
from app.db.session import engine
import logging
import traceback
from contextlib import asynccontextmanager
from app.core.auth import get_service_auth
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa los servicios necesarios al arrancar la aplicación"""
    if settings.ENVIRONMENT != "test":
        try:
            service_auth = get_service_auth()
            await service_auth.initialize()
            logging.info("Servicio de autenticación inicializado")
        except Exception as e:
            logging.error(f"Error al inicializar servicio de autenticación: {str(e)}")
            logging.error(traceback.format_exc())

        try:
            Base.metadata.create_all(bind=engine)
            logging.info("Tablas creadas correctamente en la base de datos")
        except Exception as e:
            logging.error(f"Error al crear tablas en la base de datos: {str(e)}")
            logging.error(traceback.format_exc())
    yield


app = FastAPI(lifespan=lifespan)


# TODO: Logging
# TODO: Errores RFC
# TODO: MANEJAR EXCEPCIONES

app.include_router(statistics_router)


@app.get("/health")
def get_health():
    return {"status": "ok"}
