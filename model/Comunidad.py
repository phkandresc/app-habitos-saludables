from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from model.Base import Base
import logging

logger = logging.getLogger(__name__)


class Comunidad(Base):
    """Modelo para la tabla comunidad"""

    __tablename__ = 'comunidad'

    # Columnas
    id_comunidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    id_creador = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='SET DEFAULT'))

    # Relaciones
    usuario_creador = relationship("Usuario", back_populates="comunidades_creadas", foreign_keys=[id_creador])
    categorias_comunidad = relationship("ComunidadCategoria", back_populates="comunidad")

    def __repr__(self):
        """Representación string del objeto"""
        return (f"<Comunidad(id_comunidad={self.id_comunidad}, nombre='{self.nombre}', "
                f"id_creador={self.id_creador})>")

