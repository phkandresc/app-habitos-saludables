from sqlalchemy import Column, Integer, String, Date
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

    # Relaciones
    #perfil = relationship("PerfilUsuario", back_populates="usuario", uselist=False)
    #seguimientos = relationship("SeguimientoDiario", back_populates="usuario")
    #asignaciones_nivel = relationship("AsignacionNivel", back_populates="usuario")
    #logros = relationship("Logro", secondary="desbloquea", back_populates="usuarios")
    #participaciones = relationship("Participacion", back_populates="usuario")
    #comunidades = relationship("Comunidad", secondary="incorpora_comunidad", back_populates="usuarios")
    #rankings = relationship("Ranking", secondary="posee_ranking", back_populates="usuarios")