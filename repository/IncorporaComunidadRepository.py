from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import date
import logging

from db.Connection import DatabaseConnection
from model.IncorporaComunidad import IncorporaComunidad
from model.Comunidad import Comunidad
from model.Usuario import Usuario

# Configurar logging
logger = logging.getLogger(__name__)


class IncorporaComunidadRepository:
    """Repositorio para operaciones de base de datos de IncorporaComunidad"""

    def __init__(self):
        self.db = DatabaseConnection()

    def incorporar_usuario_a_comunidad(self, incorporacion_data: dict) -> Optional[IncorporaComunidad]:
        """Incorporar usuario a una comunidad"""
        try:
            self._validar_datos_incorporacion(incorporacion_data)

            with self.db.get_session() as session:
                # Verificar que no existe ya la incorporación
                existe = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_usuario == incorporacion_data['id_usuario'],
                    IncorporaComunidad.id_comunidad == incorporacion_data['id_comunidad']
                ).first()

                if existe:
                    logger.warning(f"Usuario {incorporacion_data['id_usuario']} ya está incorporado en comunidad {incorporacion_data['id_comunidad']}")
                    return None

                # Si no se proporciona fecha_union, usar la fecha actual
                if 'fecha_union' not in incorporacion_data:
                    incorporacion_data['fecha_union'] = date.today()

                incorporacion = IncorporaComunidad(**incorporacion_data)
                session.add(incorporacion)
                session.flush()
                session.expunge(incorporacion)
                logger.info(f"Usuario {incorporacion.id_usuario} incorporado exitosamente a comunidad {incorporacion.id_comunidad}")
                return incorporacion

        except ValueError as e:
            logger.error(f"Datos inválidos para incorporar usuario: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error de BD incorporando usuario: {e}")
            return None

    def obtener_incorporacion(self, id_usuario: int, id_comunidad: int) -> Optional[IncorporaComunidad]:
        """Obtener incorporación específica de usuario en comunidad"""
        if not self._validar_id(id_usuario) or not self._validar_id(id_comunidad):
            return None

        try:
            with self.db.get_session() as session:
                incorporacion = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_usuario == id_usuario,
                    IncorporaComunidad.id_comunidad == id_comunidad
                ).first()

                if incorporacion:
                    session.expunge(incorporacion)
                    return incorporacion
                return None

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo incorporación usuario {id_usuario} en comunidad {id_comunidad}: {e}")
            return None

    def obtener_comunidades_de_usuario(self, id_usuario: int, estado: Optional[str] = None) -> List[IncorporaComunidad]:
        """Obtener todas las comunidades de un usuario, opcionalmente filtradas por estado"""
        if not self._validar_id(id_usuario):
            return []

        try:
            with self.db.get_session() as session:
                query = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_usuario == id_usuario
                )

                if estado:
                    query = query.filter(IncorporaComunidad.estado == estado)

                incorporaciones = query.order_by(IncorporaComunidad.fecha_union.desc()).all()

                for incorporacion in incorporaciones:
                    session.expunge(incorporacion)
                return incorporaciones

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo comunidades del usuario {id_usuario}: {e}")
            return []

    def obtener_miembros_de_comunidad(self, id_comunidad: int, estado: Optional[str] = None) -> List[IncorporaComunidad]:
        """Obtener todos los miembros de una comunidad, opcionalmente filtrados por estado"""
        if not self._validar_id(id_comunidad):
            return []

        try:
            with self.db.get_session() as session:
                query = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_comunidad == id_comunidad
                )

                if estado:
                    query = query.filter(IncorporaComunidad.estado == estado)

                incorporaciones = query.order_by(IncorporaComunidad.fecha_union.desc()).all()

                for incorporacion in incorporaciones:
                    session.expunge(incorporacion)
                return incorporaciones

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo miembros de comunidad {id_comunidad}: {e}")
            return []

    def obtener_comunidades_con_detalles_usuario(self, id_usuario: int, estado: Optional[str] = None) -> List[dict]:
        """Obtener comunidades de usuario con detalles de la comunidad"""
        if not self._validar_id(id_usuario):
            return []

        try:
            with self.db.get_session() as session:
                query = session.query(IncorporaComunidad, Comunidad).join(
                    Comunidad, IncorporaComunidad.id_comunidad == Comunidad.id_comunidad
                ).filter(IncorporaComunidad.id_usuario == id_usuario)

                if estado:
                    query = query.filter(IncorporaComunidad.estado == estado)

                resultados = query.order_by(IncorporaComunidad.fecha_union.desc()).all()

                comunidades_detalladas = []
                for incorporacion, comunidad in resultados:
                    session.expunge(incorporacion)
                    session.expunge(comunidad)
                    comunidades_detalladas.append({
                        'incorporacion': incorporacion,
                        'comunidad': comunidad
                    })

                return comunidades_detalladas

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo comunidades con detalles del usuario {id_usuario}: {e}")
            return []

    def contar_miembros_comunidad(self, id_comunidad: int, estado: Optional[str] = None) -> int:
        """Contar miembros de una comunidad por estado"""
        if not self._validar_id(id_comunidad):
            return 0

        try:
            with self.db.get_session() as session:
                query = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_comunidad == id_comunidad
                )

                if estado:
                    query = query.filter(IncorporaComunidad.estado == estado)

                return query.count()

        except SQLAlchemyError as e:
            logger.error(f"Error contando miembros de comunidad {id_comunidad}: {e}")
            return 0

    def actualizar_estado_incorporacion(self, id_usuario: int, id_comunidad: int, nuevo_estado: str) -> bool:
        """Actualizar estado de incorporación"""
        if not self._validar_id(id_usuario) or not self._validar_id(id_comunidad):
            return False

        if not self._validar_estado(nuevo_estado):
            logger.error(f"Estado inválido: {nuevo_estado}")
            return False

        try:
            with self.db.get_session() as session:
                incorporacion = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_usuario == id_usuario,
                    IncorporaComunidad.id_comunidad == id_comunidad
                ).first()

                if not incorporacion:
                    logger.warning(f"Incorporación no encontrada: usuario {id_usuario} en comunidad {id_comunidad}")
                    return False

                incorporacion.estado = nuevo_estado
                session.flush()
                logger.info(f"Estado actualizado para usuario {id_usuario} en comunidad {id_comunidad}: {nuevo_estado}")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Error actualizando estado de incorporación: {e}")
            return False

    def eliminar_incorporacion(self, id_usuario: int, id_comunidad: int) -> bool:
        """Eliminar incorporación de usuario de comunidad"""
        if not self._validar_id(id_usuario) or not self._validar_id(id_comunidad):
            return False

        try:
            with self.db.get_session() as session:
                incorporacion_eliminada = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_usuario == id_usuario,
                    IncorporaComunidad.id_comunidad == id_comunidad
                ).delete()

                if incorporacion_eliminada:
                    logger.info(f"Usuario {id_usuario} eliminado de comunidad {id_comunidad}")
                    return True

                logger.warning(f"Incorporación no encontrada para eliminar: usuario {id_usuario} en comunidad {id_comunidad}")
                return False

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando incorporación: {e}")
            return False

    def verificar_usuario_en_comunidad(self, id_usuario: int, id_comunidad: int, estado: Optional[str] = None) -> bool:
        """Verificar si un usuario está en una comunidad con un estado específico"""
        if not self._validar_id(id_usuario) or not self._validar_id(id_comunidad):
            return False

        try:
            with self.db.get_session() as session:
                query = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_usuario == id_usuario,
                    IncorporaComunidad.id_comunidad == id_comunidad
                )

                if estado:
                    query = query.filter(IncorporaComunidad.estado == estado)

                return query.first() is not None

        except SQLAlchemyError as e:
            logger.error(f"Error verificando usuario en comunidad: {e}")
            return False

    def obtener_incorporaciones_por_fecha(self, fecha_inicio: date, fecha_fin: date) -> List[IncorporaComunidad]:
        """Obtener incorporaciones en un rango de fechas"""
        try:
            with self.db.get_session() as session:
                incorporaciones = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.fecha_union >= fecha_inicio,
                    IncorporaComunidad.fecha_union <= fecha_fin
                ).order_by(IncorporaComunidad.fecha_union.desc()).all()

                for incorporacion in incorporaciones:
                    session.expunge(incorporacion)
                return incorporaciones

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo incorporaciones por fecha: {e}")
            return []

    def obtener_estadisticas_comunidad(self, id_comunidad: int) -> dict:
        """Obtener estadísticas de miembros de una comunidad"""
        if not self._validar_id(id_comunidad):
            return {}

        try:
            with self.db.get_session() as session:
                total = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_comunidad == id_comunidad
                ).count()

                activos = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_comunidad == id_comunidad,
                    IncorporaComunidad.estado == 'activo'
                ).count()

                pendientes = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_comunidad == id_comunidad,
                    IncorporaComunidad.estado == 'pendiente'
                ).count()

                bloqueados = session.query(IncorporaComunidad).filter(
                    IncorporaComunidad.id_comunidad == id_comunidad,
                    IncorporaComunidad.estado == 'bloqueado'
                ).count()

                return {
                    'total_miembros': total,
                    'miembros_activos': activos,
                    'miembros_pendientes': pendientes,
                    'miembros_bloqueados': bloqueados
                }

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo estadísticas de comunidad {id_comunidad}: {e}")
            return {}

    # Métodos privados de validación
    def _validar_id(self, id_valor: int) -> bool:
        """Validar que el ID sea válido"""
        return isinstance(id_valor, int) and id_valor > 0

    def _validar_estado(self, estado: str) -> bool:
        """Validar que el estado sea válido"""
        estados_validos = ['activo', 'pendiente', 'bloqueado', 'inactivo']
        return isinstance(estado, str) and estado.lower() in estados_validos

    def _validar_datos_incorporacion(self, incorporacion_data: dict) -> None:
        """Validar datos para incorporar usuario"""
        campos_requeridos = ['id_usuario', 'id_comunidad', 'estado']
        for campo in campos_requeridos:
            if campo not in incorporacion_data or incorporacion_data[campo] is None:
                raise ValueError(f"Campo requerido '{campo}' faltante o vacío")

        if not self._validar_id(incorporacion_data['id_usuario']):
            raise ValueError("El id_usuario debe ser un entero positivo válido")

        if not self._validar_id(incorporacion_data['id_comunidad']):
            raise ValueError("El id_comunidad debe ser un entero positivo válido")

        if not self._validar_estado(incorporacion_data['estado']):
            raise ValueError("El estado debe ser uno de: activo, pendiente, bloqueado, inactivo")

        if 'fecha_union' in incorporacion_data and incorporacion_data['fecha_union']:
            if not isinstance(incorporacion_data['fecha_union'], date):
                raise ValueError("La fecha_union debe ser un objeto date válido")
