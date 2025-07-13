from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from model.Base import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    correo_electronico = Column(String(100), nullable=False)
    contrasenia = Column(String(20), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(2), nullable=False)
    nombre_usuario = Column(Text, nullable=False, unique=True)

    # Usar string en lugar de clase directa
    perfil = relationship("PerfilUsuario", uselist=False, back_populates="usuario", lazy="select")

    def __repr__(self):
        return f"<Usuario(id_usuario={self.id_usuario}, nombre='{self.nombre}', apellido='{self.apellido}')>"