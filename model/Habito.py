from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Categoria(Base):
    __tablename__ = 'categorias'

    id_categoria = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    # Relaciones
    habitos = relationship("Habito", back_populates="categoria_obj")


class Habito(Base):
    __tablename__ = 'habito'

    id_habito = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    frecuencia = Column(String, nullable=False)
    categoria = Column(String, nullable=False)  # Campo string existente
    objetivo = Column(String, nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    id_categoria = Column(Integer, ForeignKey('categorias.id_categoria'))

    # Relaciones
    categoria_obj = relationship("Categoria", back_populates="habitos")
    seguimientos = relationship("SeguimientoDiario", back_populates="habito")