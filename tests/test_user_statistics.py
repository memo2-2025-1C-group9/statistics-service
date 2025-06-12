import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.dependencies import get_db

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
    with patch("app.controller.user_controller.validate_user", new_callable=AsyncMock) as mock:
        mock.return_value = 1  # Valido
        yield mock


def test_save_user_statistics_success(client, mock_validate_user):
    event_data = {
        "id_user": 1,
        "notification_type": "Tarea",
        "event": "Entregado",
        "data": {
            "titulo": "Tarea 1",
            "entregado": True,
            "nota": None
        }
    }
    
    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200

def test_save_user_statistics_unauthorized(client, mock_validate_user):
    event_data = {
        "id_user": 1,
        "notification_type": "Tarea",
        "event": "Entregado",
        "data": {
            "titulo": "Tarea 1",
            "entregado": True,
            "nota": None
        }
    }
    
    mock_validate_user.side_effect = Exception("Invalid token")
    
    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    # Verificar la respuesta TODO: RFC
    assert response.status_code == 401

def test_save_user_statistics_with_grade(client, mock_validate_user):
    event_data = {
        "id_user": 1,
        "notification_type": "Examen",
        "event": "Calificado",
        "data": {
            "titulo": "Examen 1",
            "entregado": True,
            "nota": 8.5
        }
    }
    
    response = client.post(
        "/user-statistics",
        json=event_data,
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Estadística de usuario procesada correctamente"} 