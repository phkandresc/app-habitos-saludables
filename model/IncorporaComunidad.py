from sqlalchemy import (Column, Integer, String, Date, ForeignKey,BigInteger)
from sqlalchemy.orm import relationship
from .base import Base

class IncorporaComunidad(Base):
    __tablename__ = 'incorpora_comunidad'

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    id_comunidad = Column(Integer, ForeignKey('comunidad.id_comunidad'), primary_key=True)
    estado = Column(String(50), nullable=False)
    fecha_union = Column(Date, nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="comunidades_asociadas")
    comunidad = relationship("Comunidad", back_populates="usuarios_asociados")