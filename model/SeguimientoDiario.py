from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class SeguimientoDiario(Base):
    __tablename__ = 'seguimiento_diario'
    id_seguimiento = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    estado = Column(String(50), nullable=False)  # Ej: 'completado', 'pendiente', 'fallido'
    observaciones = Column(String(500))
    edad = Column(Integer)  # Podría calcularse en lugar de almacenarse
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    id_habito = Column(Integer, ForeignKey('habito.id_habito'), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="seguimientos")
    habito = relationship("Habitos", back_populates="seguimientos")