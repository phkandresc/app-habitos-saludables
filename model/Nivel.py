from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Nivel(Base):
    __tablename__ = 'nivel'

    id_nivel = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    puntos_requeridos = Column(Integer, nullable=False)
    puntos_totales = Column(Integer, nullable=False)

    # Relación a clase intermedia
    asignaciones_usuario = relationship("AsignacionNivel", back_populates="nivel", overlaps="niveles,usuarios")

    # Relación many-to-many (solo lectura)
    usuarios = relationship("Usuario", secondary="asignacion_nivel", back_populates="niveles", viewonly=True)