from sqlalchemy import Column, BigInteger, String, Date, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from model.Base import Base
import logging

logger = logging.getLogger(__name__)


class IncorporaComunidad(Base):
    """Modelo para la tabla incorpora_comunidad que gestiona la pertenencia de usuarios a comunidades"""

    __tablename__ = 'incorpora_comunidad'

    # Columnas
    id_usuario = Column(BigInteger, ForeignKey('usuarios.id_usuario', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    id_comunidad = Column(BigInteger, ForeignKey('comunidad.id_comunidad', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    estado = Column(String(50), nullable=False)
    fecha_union = Column(Date, nullable=False)

    # Clave primaria compuesta
    __table_args__ = (
        PrimaryKeyConstraint('id_usuario', 'id_comunidad'),
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="comunidades_incorporadas")
    comunidad = relationship("Comunidad", back_populates="miembros_incorporados")

    def __init__(self, id_usuario=None, id_comunidad=None, estado=None, fecha_union=None):
        """
        Constructor para IncorporaComunidad

        Args:
            id_usuario (int): ID del usuario
            id_comunidad (int): ID de la comunidad
            estado (str): Estado de la incorporación (ej: 'activo', 'pendiente', 'bloqueado')
            fecha_union (date): Fecha en que se unió a la comunidad
        """
        self.id_usuario = id_usuario
        self.id_comunidad = id_comunidad
        self.estado = estado
        self.fecha_union = fecha_union

    def __repr__(self):
        """Representación string del objeto"""
        return (f"<IncorporaComunidad(id_usuario={self.id_usuario}, "
                f"id_comunidad={self.id_comunidad}, estado='{self.estado}', "
                f"fecha_union={self.fecha_union})>")

    def __str__(self):
        """Representación string amigable del objeto"""
        return f"Usuario {self.id_usuario} en Comunidad {self.id_comunidad} - Estado: {self.estado}"

    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'id_usuario': self.id_usuario,
            'id_comunidad': self.id_comunidad,
            'estado': self.estado,
            'fecha_union': self.fecha_union.isoformat() if self.fecha_union else None
        }

    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario"""
        from datetime import datetime

        fecha_union = None
        if data.get('fecha_union'):
            if isinstance(data['fecha_union'], str):
                fecha_union = datetime.strptime(data['fecha_union'], '%Y-%m-%d').date()
            else:
                fecha_union = data['fecha_union']

        return IncorporaComunidad(
            id_usuario=data.get('id_usuario'),
            id_comunidad=data.get('id_comunidad'),
            estado=data.get('estado'),
            fecha_union=fecha_union
        )

    def es_activo(self):
        """Verifica si el estado de incorporación está activo"""
        return self.estado.lower() == 'activo'

    def es_pendiente(self):
        """Verifica si el estado de incorporación está pendiente"""
        return self.estado.lower() == 'pendiente'

    def es_bloqueado(self):
        """Verifica si el estado de incorporación está bloqueado"""
        return self.estado.lower() == 'bloqueado'

    def activar(self):
        """Activa la incorporación"""
        self.estado = 'activo'
        logger.info(f"Usuario {self.id_usuario} activado en comunidad {self.id_comunidad}")

    def desactivar(self):
        """Desactiva la incorporación"""
        self.estado = 'inactivo'
        logger.info(f"Usuario {self.id_usuario} desactivado en comunidad {self.id_comunidad}")

    def bloquear(self):
        """Bloquea la incorporación"""
        self.estado = 'bloqueado'
        logger.info(f"Usuario {self.id_usuario} bloqueado en comunidad {self.id_comunidad}")
