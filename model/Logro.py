from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Logro(Base):
    __tablename__ = 'logros'

    id_logro = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    puntos = Column(Integer, nullable=False)
    descripcion = Column(String(500))

    desbloqueos_usuario = relationship("Desbloquea", back_populates="logro", overlaps="logros")
    usuarios = relationship(
        "Usuario",
        secondary="desbloquea",
        back_populates="logros",
        overlaps="desbloqueos,desbloqueos_usuario"
    )

    recompensas = relationship(
        "Recompensa",
        back_populates="logro",
        cascade="all, delete-orphan",
        overlaps="logro"
    )

