from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Recompensa(Base):
    __tablename__ = 'recompensa'

    id_recompensa = Column(Integer, primary_key=True)
    id_logro = Column(Integer, ForeignKey('logros.id_logro'), nullable=False)
    fecha_recompensa = Column(Date, nullable=False)

    # Relaciones
    logro = relationship("Logro", back_populates="recompensas", overlaps="recompensas")