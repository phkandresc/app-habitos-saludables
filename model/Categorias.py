from sqlalchemy import Column, Integer, String
from .base import Base

class Categoria(Base):
    __tablename__ = 'categorias'

    id_categoria = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)