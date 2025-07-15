from sqlalchemy import Column, Integer, BigInteger, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from model.Base import Base

class Habito(Base):
    __tablename__ = 'habito'

    id_habito = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    frecuencia = Column(String(150), nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    id_categoria = Column(Integer, ForeignKey('categorias.id_categoria', ondelete='CASCADE'))
    id_usuario = Column(BigInteger, ForeignKey('usuarios.id_usuario'), nullable=False)

    categoria_rel = relationship("Categoria", back_populates="habitos", lazy="select")
    usuario_rel = relationship("Usuario", back_populates="habitos")
    seguimientos = relationship("SeguimientoDiario", back_populates="habito_rel", lazy="dynamic")

    def __repr__(self):
        return (f"<Habito(id_habito={self.id_habito}, nombre='{self.nombre}', "
                f"id_categoria={self.id_categoria}, id_usuario={self.id_usuario})>")