import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.dependencies import get_db
from app.repositories.statistics_repository import create_statistics
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_statistics(db_session):
    """
    Fixture que crea datos de ejemplo en la base de datos
    """
    # Crear estadísticas para el curso "curso1"
    create_statistics(
        db_session,
        user_id=1,
        assessment_id="tarea1",
        titulo="Tarea 1",
        tipo="Tarea",
        entregado=True,
        calificacion=8.5,
        course_id="curso1",
        date=datetime(2023, 10, 1),
    )
    create_statistics(
        db_session,
        user_id=1,
        assessment_id="tarea2",
        titulo="Tarea 2",
        tipo="Tarea",
        entregado=True,
        calificacion=9.0,
        course_id="curso1",
        date=datetime(2023, 10, 5),
    )
    create_statistics(
        db_session,
        user_id=1,
        assessment_id="examen1",
        titulo="Examen 1",
        tipo="Examen",
        entregado=True,
        calificacion=7.5,
        course_id="curso1",
        date=datetime(2023, 10, 10),
    )
    create_statistics(
        db_session,
        user_id=1,
        assessment_id="tarea3",
        titulo="Tarea 3",
        tipo="Tarea",
        entregado=False,
        course_id="curso1",
        date=datetime(2023, 10, 15),
    )

    # Crear estadísticas para otro usuario en el mismo curso
    create_statistics(
        db_session,
        user_id=2,
        assessment_id="tarea1",
        titulo="Tarea 1",
        tipo="Tarea",
        entregado=True,
        calificacion=7.0,
        course_id="curso1",
        date=datetime(2023, 10, 20),
    )

    # Crear estadísticas para otro curso
    create_statistics(
        db_session,
        user_id=1,
        assessment_id="tarea1",
        titulo="Tarea 1",
        tipo="Tarea",
        entregado=True,
        calificacion=8.0,
        course_id="curso2",
        date=datetime(2023, 11, 1),
    )


def test_get_global_statistics_success(client: TestClient, sample_statistics):
    response = client.get("/statistics/global")
    assert response.status_code == 200

    data = response.json()
    assert "promedio_calificaciones" in data
    assert "tasa_finalizacion" in data
    assert "total_asignaciones" in data
    assert "asignaciones_completadas" in data

    assert data["total_asignaciones"] == 6  # Total de asignaciones creadas
    assert data["asignaciones_completadas"] == 5  # 5 entregadas, 1 no entregada
    assert data["tasa_finalizacion"] == pytest.approx(83.33, 0.01)  # 5/6 * 100
    assert data["promedio_calificaciones"] == pytest.approx(
        8.0, 0.01
    )  # Promedio de todas las calificaciones


def test_get_global_statistics_empty_database(client: TestClient):
    response = client.get("/statistics/global")
    assert response.status_code == 200

    data = response.json()
    assert data["total_asignaciones"] == 0
    assert data["asignaciones_completadas"] == 0
    assert data["tasa_finalizacion"] == 0
    assert data["promedio_calificaciones"] == 0


def test_get_user_statistics_success(client: TestClient, sample_statistics):
    response = client.get("/statistics/user/curso1/1")
    assert response.status_code == 200

    data = response.json()
    assert "promedio_calificaciones" in data
    assert "tasa_finalizacion" in data
    assert "total_asignaciones" in data
    assert "asignaciones_completadas" in data
    assert "course_id" in data

    # Verificar valores especificos para el usuario 1 en curso1
    assert data["total_asignaciones"] == 4  # 4 asignaciones en curso1
    assert data["asignaciones_completadas"] == 3  # 3 entregadas, 1 no entregada
    assert data["tasa_finalizacion"] == pytest.approx(75.0, 0.01)  # 3/4 * 100
    assert data["promedio_calificaciones"] == pytest.approx(
        8.33, 0.01
    )  # Promedio de las 3 calificaciones
    assert data["course_id"] == "curso1"


def test_get_user_statistics_user_not_found(client: TestClient, sample_statistics):
    response = client.get("/statistics/user/curso1/999")
    assert response.status_code == 200

    data = response.json()
    assert data["total_asignaciones"] == 0
    assert data["asignaciones_completadas"] == 0
    assert data["tasa_finalizacion"] == 0
    assert data["promedio_calificaciones"] == 0


def test_get_user_statistics_course_not_found(client: TestClient, sample_statistics):
    response = client.get("/statistics/user/curso_inexistente/1")
    assert response.status_code == 200

    data = response.json()
    assert data["total_asignaciones"] == 0
    assert data["asignaciones_completadas"] == 0
    assert data["tasa_finalizacion"] == 0
    assert data["promedio_calificaciones"] == 0


def test_get_user_statistics_different_course(client: TestClient, sample_statistics):
    response = client.get("/statistics/user/curso2/1")
    assert response.status_code == 200

    data = response.json()
    assert data["total_asignaciones"] == 1  # 1 asignacion en curso2
    assert data["asignaciones_completadas"] == 1  # 1 entregada
    assert data["tasa_finalizacion"] == 100.0  # 1/1 * 100
    assert data["promedio_calificaciones"] == 8.0  # Calificacion de la unica tarea
    assert data["course_id"] == "curso2"


def test_get_user_statistics_with_start_date(client: TestClient, sample_statistics):
    response = client.get("/statistics/user/curso1/1?start_date=2023-10-10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 2
    assert data["total_asignaciones"] == 2
    assert data["asignaciones_completadas"] == 1
    assert data["tasa_finalizacion"] == 50.0
    assert data["promedio_calificaciones"] == pytest.approx(7.5, 0.01)  # Examen 1



def test_get_user_statistics_with_end_date(client: TestClient, sample_statistics):
    response = client.get("/statistics/user/curso1/1?end_date=2023-10-11")
    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 3
    assert data["total_asignaciones"] == 3
    assert data["asignaciones_completadas"] == 3
    assert data["tasa_finalizacion"] == 100.0
    assert data["promedio_calificaciones"] == pytest.approx(8.33, 0.01)  # Examen 1


def test_get_user_statistics_with_date_range(client: TestClient, sample_statistics):
    response = client.get(
        "/statistics/user/curso1/1?start_date=2023-10-05&end_date=2023-10-12"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 2
    assert data["total_asignaciones"] == 2
    assert data["asignaciones_completadas"] == 2
    assert data["tasa_finalizacion"] == 100.0
    assert data["promedio_calificaciones"] == pytest.approx(8.25, 0.01)  # Tarea 2 y Examen 1
