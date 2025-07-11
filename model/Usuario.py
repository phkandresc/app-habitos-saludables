from sqlalchemy import (Column, Integer, String, Date, Text)
from sqlalchemy.orm import relationship
from .Base import Base


class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    direccion = Column(String(50), nullable=False)
    contrasenia = Column(String(20), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(2), nullable=False)
    nombre_usuario = Column(Text, unique=True)

    # Relaciones
    #perfil = relationship("PerfilUsuario", back_populates="usuario", uselist=False)
    #seguimientos = relationship("SeguimientoDiario", back_populates="usuario")
    #asignaciones_nivel = relationship("AsignacionNivel", back_populates="usuario")
    #logros = relationship("Logro", secondary="desbloquea", back_populates="usuarios")
    #participaciones = relationship("Participacion", back_populates="usuario")
    #comunidades = relationship("Comunidad", secondary="incorpora_comunidad", back_populates="usuarios")
    #rankings = relationship("Ranking", secondary="posee_ranking", back_populates="usuarios")

    def __repr__(self):
        return f"<Usuario(id_usuario={self.id_usuario}, nombre='{self.nombre}', apellido='{self.apellido}')>"