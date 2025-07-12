from sqlalchemy import Column, Integer, String
from .base import Base
from sqlalchemy.orm import relationship

class Categoria(Base):
    __tablename__ = 'categorias'

    id_categoria = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)

    # Relación con Habitos
    habitos = relationship("Habitos", back_populates="categoria_rel")