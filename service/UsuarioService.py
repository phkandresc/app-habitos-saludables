from repository.UsuarioRepository import UsuarioRepository
#from db.connection import get_db
from datetime import date
from typing import Optional


class UsuarioService:
    """Servicio con lógica de negocio para usuarios"""

    def __init__(self, db_session):
        self.usuario_repo = UsuarioRepository(db_session)

    def registrar_usuario(self, nombre: str, apellido: str, direccion: str,
                          contrasenia: str, fecha_nacimiento: date, sexo: str):
        """Lógica de negocio para registrar usuario"""

        # Validaciones de negocio
        if self._calcular_edad(fecha_nacimiento) < 13:
            raise ValueError("El usuario debe ser mayor de 13 años")

        if len(contrasenia) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")

        # Crear usuario
        usuario_data = {
            "nombre": nombre.title(),  # Capitalizar nombre
            "apellido": apellido.title(),
            "direccion": direccion,
            "contrasenia": self._hash_password(contrasenia),  # Hash de contraseña
            "fecha_nacimiento": fecha_nacimiento,
            "sexo": sexo.upper()
        }

        return self.usuario_repo.create(usuario_data)

    def _calcular_edad(self, fecha_nacimiento: date) -> int:
        """Calcular edad a partir de fecha de nacimiento"""
        today = date.today()
        return today.year - fecha_nacimiento.year - (
                (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )

    def _hash_password(self, password: str) -> str:
        """Hash de contraseña (implementar con bcrypt)"""
        return f"hashed_{password}"