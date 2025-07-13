from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from model.Base import Base


class Habito(Base):
    __tablename__ = 'habito'

    id_habito = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    frecuencia = Column(String(150), nullable=False)
    categoria = Column(String(100), nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    id_categoria = Column(Integer, ForeignKey('categorias.id_categoria', ondelete='CASCADE'))

    # Relación con Categoria
    categoria_rel = relationship("Categoria", back_populates="habitos")

    def __repr__(self):
        return f"<Habitos(id_habito={self.id_habito}, nombre='{self.nombre}', categoria='{self.categoria}')>"