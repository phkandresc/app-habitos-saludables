from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.Connection import DatabaseConnection
from model.Usuario import Usuario
from typing import List, Optional


class UsuarioRepository:
    """Repositorio para operaciones de base de datos de Usuario"""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_usuario(self, usuario_data: dict) -> Optional[Usuario]:
        """Crear usuario en BD"""
        try:
            with self.db.get_session() as session:
                usuario = Usuario(**usuario_data)
                session.add(usuario)
                session.flush()  # Para obtener el ID antes del commit
                # Hacer que el objeto sea independiente de la sesión
                session.expunge(usuario)
                # El commit es automático por el context manager
                return usuario

        except SQLAlchemyError as e:
            print(f"Error creando usuario: {e}")
            return None

    def obtener_usuario_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        try:
            with self.db.get_session() as session:
                usuario = session.query(Usuario).filter(
                    Usuario.id_usuario == id_usuario
                ).first()

                if usuario:
                    # Hacer que el objeto sea independiente de la sesión
                    session.expunge(usuario)
                    return usuario
                return None
        except SQLAlchemyError as e:
            print(f"Error obteniendo usuario: {e}")
            return None

    def obtener_todos_usuarios(self) -> List[Usuario]:
        """Obtener todos los usuarios"""
        try:
            with self.db.get_session() as session:
                return session.query(Usuario).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo usuarios: {e}")
            return []

    def actualizar_usuario(self, id_usuario: int, usuario_data: dict) -> Optional[Usuario]:
        """Actualizar usuario"""
        try:
            with self.db.get_session() as session:
                usuario = session.query(Usuario).filter(
                    Usuario.id_usuario == id_usuario
                ).first()

                if usuario:
                    for key, value in usuario_data.items():
                        if hasattr(usuario, key):
                            setattr(usuario, key, value)

                    session.flush()
                    return usuario
                return None

        except SQLAlchemyError as e:
            print(f"Error actualizando usuario: {e}")
            return None

    def eliminar_usuario(self, id_usuario: int) -> bool:
        """Eliminar usuario"""
        try:
            with self.db.get_session() as session:
                usuario = session.query(Usuario).filter(
                    Usuario.id_usuario == id_usuario
                ).first()

                if usuario:
                    session.delete(usuario)
                    return True
                return False

        except SQLAlchemyError as e:
            print(f"Error eliminando usuario: {e}")
            return False

    def autenticar_usuario(self, nombre_usuario: str, contrasenia: str) -> Optional[Usuario]:
        """Autenticar usuario por nombre y contraseña"""
        try:
            with self.db.get_session() as session:
                usuario = session.query(Usuario).filter(
                    Usuario.nombre_usuario == nombre_usuario,
                    Usuario.contrasenia == contrasenia
                ).first()

                if usuario:
                    # Hacer que el objeto sea independiente de la sesión
                    session.expunge(usuario)
                    return usuario
                return None

        except SQLAlchemyError as e:
            print(f"Error autenticando usuario: {e}")
            return None

    def usuario_existe(self, nombre_usuario: str = None, email: str = None) -> bool:
        """Verificar si un usuario existe por nombre o email"""
        try:
            with self.db.get_session() as session:
                query = session.query(Usuario)

                if nombre_usuario:
                    query = query.filter(Usuario.nombre == nombre_usuario)
                elif email:
                    query = query.filter(Usuario.email == email)
                else:
                    return False

                return query.first() is not None

        except SQLAlchemyError as e:
            print(f"Error verificando usuario: {e}")
            return False