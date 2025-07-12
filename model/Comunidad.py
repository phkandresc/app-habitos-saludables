from sqlalchemy.orm import relationship

from .base import Base
from sqlalchemy import (Column, Integer, String, Date,ForeignKey)

class Comunidad(Base):
    __tablename__ = 'comunidad'

    id_comunidad = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    creador = Column(String(50), nullable=False)
    categorias = Column(String(30), nullable=False)

    # Relaciones
    usuarios_asociados = relationship("IncorporaComunidad", back_populates="comunidad")

