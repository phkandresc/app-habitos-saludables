from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Ranking(Base):
    __tablename__ = 'ranking'

    id_ranking = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500))

    # Relación a PoseeRanking (tabla intermedia)
    posee_usuarios = relationship("PoseeRanking", back_populates="ranking", overlaps="usuarios")

    # Relación many-to-many (opcional solo lectura)
    usuarios = relationship("Usuario", secondary="posee_ranking", back_populates="rankings", viewonly=True, overlaps="posee_usuarios")