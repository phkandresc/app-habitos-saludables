from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from model.Base import Base
import logging

logger = logging.getLogger(__name__)


class ComunidadCategoria(Base):
    """Modelo para la tabla de relación comunidad_categoria"""

    __tablename__ = 'comunidad_categoria'

    # Columnas
    id_comunidad = Column(Integer, ForeignKey('comunidad.id_comunidad'), nullable=False)
    id_categoria = Column(Integer, ForeignKey('categorias.id_categoria'), nullable=False)

    # Clave primaria compuesta
    __table_args__ = (
        PrimaryKeyConstraint('id_comunidad', 'id_categoria'),
    )

    # Relaciones
    comunidad = relationship("Comunidad", back_populates="categorias_comunidad")
    categoria = relationship("Categoria", back_populates="comunidades_categoria")

    def __repr__(self):
        """Representación string del objeto"""
        return (f"<ComunidadCategoria(id_comunidad={self.id_comunidad}, "
                f"id_categoria={self.id_categoria})>")