from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class AsignacionNivel(Base):
    __tablename__ = 'asignacion_nivel'

    id_usuario = Column(Integer,ForeignKey('usuarios.id_usuario'),primary_key=True)
    id_nivel = Column( Integer,ForeignKey('nivel.id_nivel'),primary_key=True)

    # Relaciones (opcionales si necesitas navegar desde la tabla de unión)
    usuario = relationship("Usuario", back_populates="asignaciones_nivel", overlaps="niveles,usuarios")
    nivel = relationship("Nivel", back_populates="asignaciones_usuario", overlaps="niveles,usuarios")