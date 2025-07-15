# model/Categoria.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from model.Base import Base


class Categoria(Base):
    __tablename__ = 'categorias'

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

    # Relación inversa con Habitos
    habitos = relationship("Habito", back_populates="categoria_rel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Categoria(id_categoria={self.id_categoria}, nombre='{self.nombre}')>"