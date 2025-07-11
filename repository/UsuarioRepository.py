from sqlalchemy.orm import Session, joinedload
from model.Usuario import Usuario
from model.Perfil_Usuario import Perfil_Usuario
from typing import List, Optional
from datetime import date
from db.connection import get_db_session


class UsuarioRepository:
    """Repositorio para operaciones de base de datos de Usuario"""

    def __init__(self, db: Session):
        self.db = db

    def crear_usuario(self, usuario_data: dict) -> Usuario:
        """Crear usuario en BD"""
        usuario = Usuario(**usuario_data)
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def obtener_usuarioPorID(self, id_usuario: int) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        return self.db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    def obtener_todos_usuarios(self) -> List[Usuario]:
        """Obtener todos los usuarios"""
        return self.db.query(Usuario).all()

    def actualizar_usuario(self, id_usuario: int, usuario_data: dict) -> Optional[Usuario]:
        """Actualizar usuario"""
        usuario = self.get_by_id(id_usuario)
        if usuario:
            for key, value in usuario_data.items():
                setattr(usuario, key, value)
            self.db.commit()
            self.db.refresh(usuario)
        return usuario

    def eliminar_usuario(self, id_usuario: int) -> bool:
        """Eliminar usuario"""
        usuario = self.get_by_id(id_usuario)
        if usuario:
            self.db.delete(usuario)
            self.db.commit()
            return True
        return False

    def autenticar_usuario(self, nombre_usuario: str, contrasenia: str) -> Optional[Usuario]:
        """Autenticar usuario por nombre y contraseña"""
        try:
            usuario = self.db.query(Usuario) \
                .options(joinedload(Usuario.perfil)) \
                .filter(
                Usuario.nombre_usuario == nombre_usuario,
                Usuario.contrasenia == contrasenia
            ).first()
            return usuario
        except Exception as e:
            print(f"Error al autenticar usuario: {e}")
            return None





        """return self.db.query(Usuario).filter(
            Usuario.nombre == nombre_usuario,
            Usuario.contrasenia == contrasenia
        ).first()"""