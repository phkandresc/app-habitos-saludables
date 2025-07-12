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

    # Relaciones
    perfil = relationship("Perfil_Usuario", back_populates="usuario", uselist=False)
    habitos = relationship("Habitos", back_populates="usuario")
    comunidades_asociadas = relationship("IncorporaComunidad", back_populates="usuario")
    seguimientos = relationship("SeguimientoDiario", back_populates="usuario",cascade="all, delete-orphan")
    asignaciones_nivel = relationship("AsignacionNivel", back_populates="usuario", overlaps="niveles,usuarios")
    niveles = relationship("Nivel", secondary="asignacion_nivel", back_populates="usuarios", viewonly=True)
    posee_rankings = relationship("PoseeRanking", back_populates="usuario", overlaps="rankings,usuarios")
    rankings = relationship("Ranking", secondary="posee_ranking", back_populates="usuarios", viewonly=True, overlaps="posee_rankings")
    desbloqueos = relationship("Desbloquea", back_populates="usuario", overlaps="logros")
    logros = relationship("Logro", secondary="desbloquea", back_populates="usuarios", overlaps="desbloqueos")
    participaciones = relationship("Participacion",back_populates="usuario",cascade="all, delete-orphan")

