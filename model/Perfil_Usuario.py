from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy import (Column, Integer, String, Date, ForeignKey, Float)


class Perfil_Usuario(Base):
    __tablename__ = 'perfil_usuario'

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    peso = Column(Float, nullable=False)
    altura = Column(Float, nullable=False)
    edad = Column(Integer, nullable=False)
    ocupacion = Column(String(50), nullable=False)

    # Relación uno-a-uno con Usuario
    usuario = relationship("Usuario", back_populates="perfil")