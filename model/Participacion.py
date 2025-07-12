from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from .base import Base

class Participacion(Base):
    __tablename__ = 'participacion'

    id_participacion = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    id_desafio = Column(Integer, ForeignKey('desafio.id_desafio'), nullable=False)
    fecha_inscripcion = Column(DateTime, nullable=False)
    estado = Column(String(50), nullable=False, default='activo')
    progreso = Column(Integer, default=0)

    # Relaciones
    usuario = relationship("Usuario", back_populates="participaciones")
    desafio = relationship("Desafio", back_populates="participantes")