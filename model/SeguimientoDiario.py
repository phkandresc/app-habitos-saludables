from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Date, BigInteger

from model.Base import Base

class SeguimientoDiario(Base):
    __tablename__ = 'seguimiento_diario'

    fecha = Column(Date, primary_key=True)
    id_habito = Column(BigInteger, ForeignKey('habito.id_habito', ondelete='CASCADE'), primary_key=True)
    id_usuario = Column(BigInteger, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True)
    estado = Column(String(50), nullable=False)

    habito_rel = relationship("Habito", back_populates="seguimientos")
    usuario_rel = relationship("Usuario", back_populates="seguimientos")

    def __repr__(self):
        return (f"<SeguimientoDiario(fecha={self.fecha}, id_habito={self.id_habito}, "
                f"id_usuario={self.id_usuario}, estado='{self.estado}')>")