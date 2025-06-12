from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    titulo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # "Examen" o "Tarea"
    entregado = Column(Boolean, default=False)
    calificacion = Column(Float, nullable=True)
