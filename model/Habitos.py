from sqlalchemy import (Column, Integer, String, Date,ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Habitos(Base):
    __tablename__ = 'habito'

    id_habito = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    frecuencia = Column(String(150), nullable=False)
    categoria = Column(String(100), nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    id_categoria = Column(Integer, ForeignKey('categorias.id_categoria'))

    # Relación con Categoria
    categorias = relationship("Categoria", backref="habitos")