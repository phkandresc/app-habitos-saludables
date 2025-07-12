from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class PoseeRanking(Base):
    __tablename__ = 'posee_ranking'

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    id_ranking = Column(Integer, ForeignKey('ranking.id_ranking'), primary_key=True)

    usuario = relationship("Usuario", back_populates="posee_rankings", overlaps="rankings,usuarios")
    ranking = relationship("Ranking", back_populates="posee_usuarios", overlaps="usuarios")