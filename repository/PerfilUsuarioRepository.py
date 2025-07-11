from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.Connection import DatabaseConnection
from model.PerfilUsuario import PerfilUsuario  # Asume que tienes este modelo
from typing import List, Optional


class PerfilUsuarioRepository:
    """Repositorio para operaciones de base de datos de PerfilUsuario"""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_perfil(self, perfil_data: dict) -> Optional[PerfilUsuario]:
        """Crear perfil de usuario en BD"""
        try:
            with self.db.get_session() as session:
                perfil = PerfilUsuario(**perfil_data)
                session.add(perfil)
                session.flush()
                # Hacer que el objeto sea independiente de la sesión
                session.expunge(perfil)
                return perfil

        except SQLAlchemyError as e:
            print(f"Error creando perfil: {e}")
            return None

    def obtener_perfil_por_usuario(self, id_usuario: int) -> Optional[PerfilUsuario]:
        """Obtener perfil por ID de usuario"""
        try:
            with self.db.get_session() as session:
                perfil = session.query(PerfilUsuario).filter(
                    PerfilUsuario.id_usuario == id_usuario
                ).first()

                if perfil:
                    # Hacer que el objeto sea independiente de la sesión
                    session.expunge(perfil)
                    return perfil
                return None
        except SQLAlchemyError as e:
            print(f"Error obteniendo perfil: {e}")
            return None

    def obtener_todos_perfiles(self) -> List[PerfilUsuario]:
        """Obtener todos los perfiles"""
        try:
            with self.db.get_session() as session:
                return session.query(PerfilUsuario).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo perfiles: {e}")
            return []

    def actualizar_perfil(self, id_usuario: int, perfil_data: dict) -> Optional[PerfilUsuario]:
        """Actualizar perfil de usuario"""
        try:
            with self.db.get_session() as session:
                perfil = session.query(PerfilUsuario).filter(
                    PerfilUsuario.id_usuario == id_usuario
                ).first()

                if perfil:
                    for key, value in perfil_data.items():
                        if hasattr(perfil, key) and key != 'id_usuario':  # No actualizar PK
                            setattr(perfil, key, value)

                    session.flush()
                    # Hacer que el objeto sea independiente de la sesión
                    session.expunge(perfil)
                    return perfil
                return None

        except SQLAlchemyError as e:
            print(f"Error actualizando perfil: {e}")
            return None

    def eliminar_perfil(self, id_usuario: int) -> bool:
        """Eliminar perfil de usuario"""
        try:
            with self.db.get_session() as session:
                perfil = session.query(PerfilUsuario).filter(
                    PerfilUsuario.id_usuario == id_usuario
                ).first()

                if perfil:
                    session.delete(perfil)
                    return True
                return False

        except SQLAlchemyError as e:
            print(f"Error eliminando perfil: {e}")
            return False

    def perfil_existe(self, id_usuario: int) -> bool:
        """Verificar si existe perfil para un usuario"""
        try:
            with self.db.get_session() as session:
                return session.query(PerfilUsuario).filter(
                    PerfilUsuario.id_usuario == id_usuario
                ).first() is not None

        except SQLAlchemyError as e:
            print(f"Error verificando perfil: {e}")
            return False

    def obtener_perfiles_por_rango_edad(self, edad_min: int, edad_max: int) -> List[PerfilUsuario]:
        """Obtener perfiles por rango de edad"""
        try:
            with self.db.get_session() as session:
                return session.query(PerfilUsuario).filter(
                    PerfilUsuario.edad.between(edad_min, edad_max)
                ).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo perfiles por edad: {e}")
            return []

    def obtener_perfiles_por_ocupacion(self, ocupacion: str) -> List[PerfilUsuario]:
        """Obtener perfiles por ocupación"""
        try:
            with self.db.get_session() as session:
                return session.query(PerfilUsuario).filter(
                    PerfilUsuario.ocupacion.ilike(f"%{ocupacion}%")
                ).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo perfiles por ocupación: {e}")
            return []

    def calcular_imc_usuario(self, id_usuario: int) -> Optional[float]:
        """Calcular IMC del usuario (peso/altura²)"""
        try:
            perfil = self.obtener_perfil_por_usuario(id_usuario)
            if perfil and perfil.peso and perfil.altura:
                # Altura en metros
                altura_m = perfil.altura / 100 if perfil.altura > 10 else perfil.altura
                imc = perfil.peso / (altura_m ** 2)
                return round(imc, 2)
            return None

        except Exception as e:
            print(f"Error calculando IMC: {e}")
            return None

    def obtener_estadisticas_edad(self) -> dict:
        """Obtener estadísticas de edad de todos los perfiles"""
        try:
            with self.db.get_session() as session:
                from sqlalchemy import func

                result = session.query(
                    func.avg(PerfilUsuario.edad).label('promedio'),
                    func.min(PerfilUsuario.edad).label('minimo'),
                    func.max(PerfilUsuario.edad).label('maximo'),
                    func.count(PerfilUsuario.edad).label('total')
                ).filter(PerfilUsuario.edad.isnot(None)).first()

                return {
                    'promedio': round(float(result.promedio), 2) if result.promedio else 0,
                    'minimo': result.minimo or 0,
                    'maximo': result.maximo or 0,
                    'total': result.total or 0
                }

        except SQLAlchemyError as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {'promedio': 0, 'minimo': 0, 'maximo': 0, 'total': 0}