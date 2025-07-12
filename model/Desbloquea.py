
from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Desbloquea(Base):
    __tablename__ = 'desbloquea'

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    id_logro = Column(Integer, ForeignKey('logros.id_logro'), primary_key=True)
    fecha_desbloqueo = Column(Date, nullable=False)

    usuario = relationship("Usuario", back_populates="desbloqueos", overlaps="logros,usuarios")
    logro = relationship("Logro", back_populates="desbloqueos_usuario", overlaps="logros,usuarios")