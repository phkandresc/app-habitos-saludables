from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from model.Base import Base

class Nivel(Base):
    __tablename__ = 'nivel'

    id_nivel = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    puntos_requeridos = Column(Integer, nullable=True)
    puntos_totales = Column(Integer, nullable=True)

    # Relaciones
    asignaciones = relationship("AsignacionNivel", back_populates="nivel")

    def __repr__(self):
        return f"<Nivel(id_nivel={self.id_nivel}, nombre='{self.nombre}', puntos_requeridos={self.puntos_requeridos}, puntos_totales={self.puntos_totales})>"
