import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.dependencies import get_db
from app.models.statistics_model import Statistics

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
def mock_validate_user():
    with patch(
        "app.controller.user_controller.validate_user", new_callable=AsyncMock
    ) as mock:
        mock.return_value = 1  # Valido
        yield mock


@pytest.fixture(scope="function")
def mock_get_course_users():
    with patch(
        "app.services.statistics_service.get_course_users", new_callable=AsyncMock
    ) as mock:
        mock.return_value = [1, 2, 3]  # Lista de usuarios del curso
        yield mock


def test_save_user_statistics_success(client, mock_validate_user, db_session):
    tarea = Statistics(
        user_id=1,
        course_id="curso-123",
        titulo="Tarea 1",
        tipo="Tarea",
        entregado=True,
        calificacion=None,
        assessment_id="tarea-456",
    )
    db_session.add(tarea)
    db_session.commit()

    event_data = {
        "id_user": 1,
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "Entregado",
        "data": {"entregado": True},
    }

    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 200

    stat = (
        db_session.query(Statistics)
        .filter(
            Statistics.user_id == 1,
            Statistics.titulo == "Tarea 1",
            Statistics.tipo == "Tarea",
        )
        .first()
    )

    assert stat is not None
    assert stat.entregado is True
    assert stat.calificacion is None


def test_save_user_statistics_unauthorized(client, mock_validate_user):
    event_data = {
        "id_user": 1,
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "Entregado",
        "course_id": "curso-123",
        "data": {"titulo": "Tarea 1", "entregado": True, "nota": None},
    }

    mock_validate_user.side_effect = Exception("Invalid token")

    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer invalid_token"},
    )

    # Verificar la respuesta TODO: RFC
    assert response.status_code == 401


def test_save_user_statistics_with_grade(client, mock_validate_user, db_session):
    tarea = Statistics(
        user_id=1,
        course_id="curso-123",
        titulo="Examen 1",
        tipo="Examen",
        entregado=True,
        calificacion=None,
        assessment_id="tarea-456",
    )
    db_session.add(tarea)
    db_session.commit()

    event_data = {
        "id_user": 1,
        "assessment_id": "tarea-456",
        "notification_type": "Examen",
        "event": "Calificado",
        "data": {"entregado": True, "nota": 8.5},
    }

    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 200

    stat = (
        db_session.query(Statistics)
        .filter(
            Statistics.user_id == 1,
            Statistics.titulo == "Examen 1",
            Statistics.tipo == "Examen",
        )
        .first()
    )

    assert stat is not None
    assert stat.entregado is True
    assert stat.calificacion == 8.5


def test_save_user_statistics_invalid_event_type(client, mock_validate_user):
    event_data = {
        "id_user": 1,
        "assessment_id": "tarea-456",
        "notification_type": "InvalidType",
        "event": "Entregado",
        "course_id": "curso-123",
        "data": {"titulo": "Tarea 1", "entregado": True, "nota": None},
    }

    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 422


def test_save_user_statistics_invalid_event(client, mock_validate_user):
    event_data = {
        "id_user": 1,
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "InvalidEvent",
        "course_id": "curso-123",
        "data": {"titulo": "Tarea 1", "entregado": True, "nota": None},
    }

    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 422


# Tests para el endpoint de curso
def test_save_course_statistics_success(
    client, mock_validate_user, mock_get_course_users, db_session
):
    event_data = {
        "id_course": "curso-123",
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "Nuevo",
        "course_id": "curso-123",
        "data": {
            "titulo": "Tarea 1",
        },
    }

    response = client.post(
        "/course-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 200

    stats = (
        db_session.query(Statistics)
        .filter(Statistics.titulo == "Tarea 1", Statistics.tipo == "Tarea")
        .all()
    )

    assert len(stats) == 3
    for stat in stats:
        assert stat.entregado is False
        assert stat.calificacion is None


def test_save_course_statistics_unauthorized(
    client, mock_validate_user, mock_get_course_users
):
    event_data = {
        "id_course": "curso-123",
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "Nuevo",
        "course_id": "curso-123",
        "data": {
            "titulo": "Tarea 1",
        },
    }

    mock_validate_user.side_effect = Exception("Invalid token")

    response = client.post(
        "/course-statistics",
        json=event_data,
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


def test_save_course_statistics_course_service_error(
    client, mock_validate_user, mock_get_course_users
):
    event_data = {
        "id_course": "curso-123",
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "Nuevo",
        "course_id": "curso-123",
        "data": {
            "titulo": "Tarea 1",
        },
    }

    mock_get_course_users.side_effect = Exception("Error al obtener usuarios del curso")

    response = client.post(
        "/course-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 500


def test_save_course_statistics_invalid_event_type(client, mock_validate_user):
    event_data = {
        "id_course": "curso-123",
        "assessment_id": "tarea-456",
        "notification_type": "InvalidType",
        "event": "Nuevo",
        "course_id": "curso-123",
        "data": {
            "titulo": "Tarea 1",
        },
    }

    response = client.post(
        "/course-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 422


def test_save_course_statistics_invalid_event(client, mock_validate_user):
    event_data = {
        "id_course": "curso-123",
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "InvalidEvent",
        "course_id": "curso-123",
        "data": {
            "titulo": "Tarea 1",
        },
    }

    response = client.post(
        "/course-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 422


def test_save_course_statistics_update_succes(
    client, mock_validate_user, mock_get_course_users, db_session
):
    # Simular que la tarea ya existe y se actualiza

    event_data = {
        "id_course": "curso-123",
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "Nuevo",
        "course_id": "curso-123",
        "data": {
            "titulo": "Tarea 1",
        },
    }

    response = client.post(
        "/course-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    event_data = {
        "id_course": "curso-123",
        "assessment_id": "tarea-456",
        "notification_type": "Tarea",
        "event": "Nuevo",
        "course_id": "curso-123",
        "data": {
            "titulo": "Tarea 10",
        },
    }

    response = client.post(
        "/course-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 200

    stats = (
        db_session.query(Statistics)
        .filter(Statistics.titulo == "Tarea 10", Statistics.tipo == "Tarea")
        .all()
    )

    assert len(stats) == 3
    for stat in stats:
        assert stat.entregado is False
        assert stat.calificacion is None

    stats_tarea1 = (
        db_session.query(Statistics)
        .filter(Statistics.titulo == "Tarea 1", Statistics.tipo == "Tarea")
        .all()
    )
    assert len(stats_tarea1) == 0
