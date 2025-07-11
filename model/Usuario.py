from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base


class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    contrasenia = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String, nullable=False)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    #id_per_usuario = Column(Integer, ForeignKey('perfil_usuario.id_usuario'))

    # Relaciones
    perfil = relationship("Perfil_Usuario", back_populates="usuario", uselist=False)
    habitos = relationship("Habito", back_populates="usuario")
    comunidades = relationship("Comunidad", secondary="incorpora_comunidad", back_populates="usuarios")
    niveles = relationship("Nivel", secondary="asignacion_nivel", back_populates="usuarios")
    logros = relationship("Logro", secondary="desbloquea", back_populates="usuarios")
    rankings = relationship("Ranking", secondary="posee_ranking", back_populates="usuarios")
    seguimientos = relationship("SeguimientoDiario", back_populates="usuario")

    # Relaciones
    #perfil = relationship("PerfilUsuario", back_populates="usuario", uselist=False)
    #seguimientos = relationship("SeguimientoDiario", back_populates="usuario")
    #asignaciones_nivel = relationship("AsignacionNivel", back_populates="usuario")
    #logros = relationship("Logro", secondary="desbloquea", back_populates="usuarios")
    #participaciones = relationship("Participacion", back_populates="usuario")
    #comunidades = relationship("Comunidad", secondary="incorpora_comunidad", back_populates="usuarios")
    #rankings = relationship("Ranking", secondary="posee_ranking", back_populates="usuarios")