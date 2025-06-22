from pydantic import BaseModel
from typing import Literal, Optional


class StatisticsEventData(BaseModel):
    titulo: Optional[str] = None
    nota: Optional[float] = None
    entregado: bool = False


class UserStatisticsEvent(BaseModel):
    id_user: int
    assessment_id: str
    notification_type: Literal["Examen", "Tarea"]
    event: Literal["Entregado", "Calificado"]
    data: StatisticsEventData

    class Config:
        json_schema_extra = {
            "example": {
                "id_user": 1,
                "assessment_id": "tarea-456",
                "notification_type": "Tarea",
                "event": "Entregado",
                "data": {"titulo": "Tarea 1", "entregado": True, "nota": None},
            }
        }


class CourseStatisticsEvent(BaseModel):
    assessment_id: str
    course_id: str
    notification_type: Literal["Examen", "Tarea"]
    event: Literal["Nuevo", "Actualizado"]
    data: StatisticsEventData

    class Config:
        json_schema_extra = {
            "example": {
                "course_id": "curso-123",
                "assessment_id": "tarea-456",
                "notification_type": "Tarea",
                "event": "Nuevo",
                "data": {"titulo": "Tarea 1", "entregado": False, "nota": None},
            }
        }
