from sqlalchemy import Column, Integer, String, Date, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class SeguimientoDiario(Base):
    __tablename__ = 'seguimiento_diario'

    fecha = Column(Date)
    estado = Column(String, nullable=False)
    observaciones = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    id_usuario = Column(BigInteger, ForeignKey('usuarios.id_usuario'))
    id_habito = Column(BigInteger, ForeignKey('habito.id_habito'))

    # Relaciones
    usuario = relationship("Usuario", back_populates="seguimientos")
    habito = relationship("Habito", back_populates="seguimientos")