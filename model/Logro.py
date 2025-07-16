from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from model.Base import Base

class Logro(Base):
    __tablename__ = 'logros'

    id_logro = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    puntos = Column(Integer, nullable=False)
    descripcion = Column(String(255), nullable=False)

    # Relación con Usuario (a través de Desbloquea)
    usuarios = relationship(
        "Usuario",
        secondary="desbloquea",
        back_populates="logros"
    )

    def __repr__(self):
        return f"<Logro(id_logro={self.id_logro}, nombre='{self.nombre}', puntos={self.puntos})>"
