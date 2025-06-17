from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from app.db.base import Base
from datetime import datetime


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    course_id = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # "Examen" o "Tarea"
    entregado = Column(Boolean, default=False)
    calificacion = Column(Float, nullable=True)
    assessment_id = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
