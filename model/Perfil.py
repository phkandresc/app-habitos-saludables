from sqlalchemy import Column, Integer, String, Double, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class PerfilUsuario(Base):
    __tablename__ = 'perfil_usuario'

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    peso = Column(Double)
    altura = Column(Double)
    edad = Column(Integer)
    ocupacion = Column(String)

    # Relación
    usuario = relationship("Usuario", back_populates="perfil")