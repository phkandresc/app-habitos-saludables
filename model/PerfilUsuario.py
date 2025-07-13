from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from model.Base import Base

class PerfilUsuario(Base):
    __tablename__ = 'perfil_usuario'

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    peso = Column(Float, nullable=True)
    altura = Column(Float, nullable=True)
    edad = Column(Integer, nullable=True)
    ocupacion = Column(String(50), nullable=True)

    usuario = relationship("Usuario", back_populates="perfil", lazy="select")

    def __repr__(self):
        return f"<PerfilUsuario(id_usuario={self.id_usuario}, edad={self.edad}, ocupacion='{self.ocupacion}')>"