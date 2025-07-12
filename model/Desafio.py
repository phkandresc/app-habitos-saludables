from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Desafio(Base):
    __tablename__ = 'desafio'

    id_desafio = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)

    # Relación con participantes (usuarios)
    participantes = relationship(
        "Participacion",
        back_populates="desafio",
        cascade="all, delete-orphan"
    )