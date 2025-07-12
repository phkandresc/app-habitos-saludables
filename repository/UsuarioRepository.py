from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from model.Usuario import Usuario
from model.Perfil_Usuario import Perfil_Usuario
from typing import List, Optional
from datetime import date
#   from db.connection import get_db_session


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
        usuario = self.obtener_usuario_por_id(id_usuario)
        if usuario:
            for key, value in usuario_data.items():
                setattr(usuario, key, value)
            self.db.commit()
            self.db.refresh(usuario)
        return usuario

    def eliminar_usuario(self, id_usuario: int) -> bool:
        """Eliminar usuario"""
        usuario = self.obtener_usuario_por_id(id_usuario)
        if usuario:
            self.db.delete(usuario)
            self.db.commit()
            return True
        return False

    def autenticar_usuario(self, nombre_usuario: str, contrasenia: str) -> Optional[Usuario]:
        """Autenticar usuario por nombre y contraseña"""
        try:
            print(f"Intentando autenticar con: {nombre_usuario} {contrasenia}")
            usuario = self.db.query(Usuario) \
                .options(joinedload(Usuario.perfil)) \
                .filter(
                func.lower(Usuario.nombre_usuario) == func.lower(nombre_usuario.strip()),
                Usuario.contrasenia == contrasenia.strip()
            )\
            .first()

            if usuario:
                print(f"Autenticación exitosa para: {usuario.nombre_usuario}")
                if usuario.perfil:
                    print(f"Perfil encontrado: Peso={usuario.perfil.peso}")
                else:
                    print("El usuario no tiene perfil asociado")
            else:
                print("Fallo en autenticación - Credenciales no coinciden")
                # Debug: Mostrar todos los usuarios
                all_users = self.db.query(Usuario.nombre_usuario, Usuario.contrasenia).all()
                print("Usuarios en la base de datos:")
                for u in all_users:
                    print(f"Usuario: {u.nombre_usuario}, Contraseña: {u.contrasenia}")
            return usuario
        except Exception as e:
            print(f"Error al autenticar usuario: {e}")
            return None


        """try:
            usuario = self.db.query(Usuario) \
                .options(joinedload(Usuario.perfil)) \
                .filter(
                func.lower(Usuario.nombre_usuario) == nombre_usuario.lower(),
                Usuario.contrasenia == contrasenia
            ).first()
            return usuario
        except Exception as e:
            print(f"Error al autenticar usuario: {e}")
            return None"""





        """return self.db.query(Usuario).filter(
            Usuario.nombre == nombre_usuario,
            Usuario.contrasenia == contrasenia
        ).first()"""