from fastapi import FastAPI, HTTPException, Request
from app.routes.statistics_routes import router as statistics_router
from app.db.base import Base
from app.db.session import engine
import logging
import traceback
from contextlib import asynccontextmanager
from app.core.auth import get_service_auth
from app.core.config import settings
from app.utils.problem_details import problem_detail_response


logging.getLogger("httpcore").setLevel(logging.INFO)


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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Determinar el título basado en el código de status
    title = "Error de Servidor"
    if exc.status_code == 401:
        title = "No Autorizado"
    elif exc.status_code == 403:
        title = "Prohibido"
    elif exc.status_code == 404:
        title = "No Encontrado"
    elif exc.status_code == 400:
        title = "Solicitud Incorrecta"
    elif exc.status_code == 422:
        title = "Error de Validación"
    elif exc.status_code < 500:
        title = "Error de Cliente"

    logging.error(
        f"HTTPException manejada: {exc.detail} (status: {exc.status_code}, url: {request.url})"
    )

    headers = exc.headers or {}

    headers["Content-Type"] = "application/problem+json"

    headers["Access-Control-Allow-Origin"] = "*"

    return problem_detail_response(
        status_code=exc.status_code,
        title=title,
        detail=exc.detail,
        instance=str(request.url),
        headers=headers,
    )


app.include_router(statistics_router)


@app.get("/health")
def get_health():
    return {"status": "ok"}
