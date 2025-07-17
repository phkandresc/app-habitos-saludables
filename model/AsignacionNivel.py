from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from model.Base import Base

class AsignacionNivel(Base):
    __tablename__ = 'asignacion_nivel'

    id_usuario = Column(BigInteger, ForeignKey('usuarios.id_usuario', onupdate='CASCADE', ondelete='CASCADE'),
                       primary_key=True, unique=True, nullable=False)
    id_nivel = Column(BigInteger, ForeignKey('nivel.id_nivel', onupdate='CASCADE', ondelete='CASCADE'),
                     nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="asignacion_nivel")
    nivel = relationship("Nivel", back_populates="asignaciones")

    def __repr__(self):
        return f"<AsignacionNivel(id_usuario={self.id_usuario}, id_nivel={self.id_nivel})>"
