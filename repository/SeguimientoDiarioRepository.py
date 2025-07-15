from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func, desc
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
import logging

from db.Connection import DatabaseConnection
from model.SeguimientoDiario import SeguimientoDiario
from model.Habito import Habito

# Configurar logging
logger = logging.getLogger(__name__)


class SeguimientoDiarioRepository:
    """Repositorio para operaciones de base de datos de SeguimientoDiario"""

    # Constantes de estados válidos
    ESTADOS_VALIDOS = {"pendiente", "completado"}

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_seguimiento(self, seguimiento_data: dict) -> Optional[SeguimientoDiario]:
        """Crear seguimiento diario en BD"""
        try:
            self._validar_datos_seguimiento(seguimiento_data)

            with self.db.get_session() as session:
                seguimiento = SeguimientoDiario(**seguimiento_data)
                session.add(seguimiento)
                session.flush()
                session.expunge(seguimiento)
                logger.info(f"Seguimiento creado exitosamente para hábito {seguimiento.id_habito} en fecha {seguimiento.fecha}")
                return seguimiento

        except ValueError as e:
            logger.error(f"Datos inválidos para crear seguimiento: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error de BD creando seguimiento: {e}")
            return None

    def obtener_seguimiento_por_clave(self, id_usuario: int, id_habito: int, fecha: date) -> Optional[SeguimientoDiario]:
        """Obtener seguimiento por clave primaria compuesta"""
        if not self._validar_ids_y_fecha(id_usuario, id_habito, fecha):
            return None

        try:
            with self.db.get_session() as session:
                seguimiento = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha == fecha
                    )
                ).first()

                if seguimiento:
                    session.expunge(seguimiento)
                    return seguimiento
                return None

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo seguimiento para usuario {id_usuario}, hábito {id_habito}, fecha {fecha}: {e}")
            return None

    def obtener_seguimientos_por_usuario(self, id_usuario: int, fecha_inicio: Optional[date] = None,
                                       fecha_fin: Optional[date] = None) -> List[SeguimientoDiario]:
        """Obtener todos los seguimientos de un usuario en un rango de fechas"""
        if not self._validar_id(id_usuario):
            return []

        try:
            with self.db.get_session() as session:
                query = session.query(SeguimientoDiario).filter(
                    SeguimientoDiario.id_usuario == id_usuario
                )

                if fecha_inicio and fecha_fin:
                    query = query.filter(
                        SeguimientoDiario.fecha.between(fecha_inicio, fecha_fin)
                    )
                elif fecha_inicio:
                    query = query.filter(SeguimientoDiario.fecha >= fecha_inicio)
                elif fecha_fin:
                    query = query.filter(SeguimientoDiario.fecha <= fecha_fin)

                seguimientos = query.order_by(desc(SeguimientoDiario.fecha)).all()

                for seguimiento in seguimientos:
                    session.expunge(seguimiento)
                return seguimientos

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo seguimientos del usuario {id_usuario}: {e}")
            return []

    def obtener_seguimientos_por_habito(self, id_habito: int, fecha_inicio: Optional[date] = None,
                                      fecha_fin: Optional[date] = None) -> List[SeguimientoDiario]:
        """Obtener todos los seguimientos de un hábito en un rango de fechas"""
        if not self._validar_id(id_habito):
            return []

        try:
            with self.db.get_session() as session:
                query = session.query(SeguimientoDiario).filter(
                    SeguimientoDiario.id_habito == id_habito
                )

                if fecha_inicio and fecha_fin:
                    query = query.filter(
                        SeguimientoDiario.fecha.between(fecha_inicio, fecha_fin)
                    )
                elif fecha_inicio:
                    query = query.filter(SeguimientoDiario.fecha >= fecha_inicio)
                elif fecha_fin:
                    query = query.filter(SeguimientoDiario.fecha <= fecha_fin)

                seguimientos = query.order_by(desc(SeguimientoDiario.fecha)).all()

                for seguimiento in seguimientos:
                    session.expunge(seguimiento)
                return seguimientos

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo seguimientos del hábito {id_habito}: {e}")
            return []

    def obtener_seguimientos_por_fecha(self, fecha: date, id_usuario: Optional[int] = None) -> List[SeguimientoDiario]:
        """Obtener seguimientos para una fecha específica, opcionalmente filtrado por usuario"""
        if not isinstance(fecha, date):
            logger.error("La fecha debe ser un objeto date válido")
            return []

        try:
            with self.db.get_session() as session:
                query = session.query(SeguimientoDiario).filter(
                    SeguimientoDiario.fecha == fecha
                )

                if id_usuario and self._validar_id(id_usuario):
                    query = query.filter(SeguimientoDiario.id_usuario == id_usuario)

                seguimientos = query.all()

                for seguimiento in seguimientos:
                    session.expunge(seguimiento)
                return seguimientos

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo seguimientos para fecha {fecha}: {e}")
            return []

    def actualizar_seguimiento(self, id_usuario: int, id_habito: int, fecha: date,
                             seguimiento_data: dict) -> Optional[SeguimientoDiario]:
        """Actualizar seguimiento existente"""
        if not self._validar_ids_y_fecha(id_usuario, id_habito, fecha):
            return None

        try:
            self._validar_datos_actualizacion(seguimiento_data)

            with self.db.get_session() as session:
                seguimiento = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha == fecha
                    )
                ).first()

                if not seguimiento:
                    logger.warning(f"Seguimiento no encontrado para usuario {id_usuario}, hábito {id_habito}, fecha {fecha}")
                    return None

                # Actualizar solo campos válidos
                for key, value in seguimiento_data.items():
                    if hasattr(seguimiento, key) and key not in ['id_usuario', 'id_habito', 'fecha']:
                        setattr(seguimiento, key, value)

                session.flush()
                session.expunge(seguimiento)
                logger.info(f"Seguimiento actualizado para usuario {id_usuario}, hábito {id_habito}, fecha {fecha}")
                return seguimiento

        except ValueError as e:
            logger.error(f"Datos inválidos para actualizar seguimiento: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error actualizando seguimiento: {e}")
            return None

    def actualizar_estado(self, id_usuario: int, id_habito: int, fecha: date, nuevo_estado: str) -> bool:
        """Actualizar solo el estado de un seguimiento"""
        if not self._validar_ids_fecha_y_estado(id_usuario, id_habito, fecha, nuevo_estado):
            return False

        try:
            with self.db.get_session() as session:
                seguimiento = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha == fecha
                    )
                ).first()

                if seguimiento:
                    seguimiento.estado = nuevo_estado
                    logger.info(f"Estado actualizado a '{nuevo_estado}' para usuario {id_usuario}, hábito {id_habito}, fecha {fecha}")
                    return True
                else:
                    logger.warning(f"Seguimiento no encontrado para actualizar estado")
                    return False

        except SQLAlchemyError as e:
            logger.error(f"Error actualizando estado del seguimiento: {e}")
            return False

    def crear_o_actualizar_seguimiento(self, seguimiento_data: dict) -> Optional[SeguimientoDiario]:
        """Crear seguimiento si no existe, o actualizar si ya existe"""
        try:
            self._validar_datos_seguimiento(seguimiento_data)

            id_usuario = seguimiento_data['id_usuario']
            id_habito = seguimiento_data['id_habito']
            fecha = seguimiento_data['fecha']

            with self.db.get_session() as session:
                seguimiento = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha == fecha
                    )
                ).first()

                if seguimiento:
                    # Actualizar seguimiento existente
                    for key, value in seguimiento_data.items():
                        if hasattr(seguimiento, key):
                            setattr(seguimiento, key, value)
                    logger.info(f"Seguimiento actualizado para usuario {id_usuario}, hábito {id_habito}, fecha {fecha}")
                else:
                    # Crear nuevo seguimiento
                    seguimiento = SeguimientoDiario(**seguimiento_data)
                    session.add(seguimiento)
                    logger.info(f"Nuevo seguimiento creado para usuario {id_usuario}, hábito {id_habito}, fecha {fecha}")

                session.flush()
                session.expunge(seguimiento)
                return seguimiento

        except ValueError as e:
            logger.error(f"Datos inválidos para crear/actualizar seguimiento: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error de BD creando/actualizando seguimiento: {e}")
            return None

    def eliminar_seguimiento(self, id_usuario: int, id_habito: int, fecha: date) -> bool:
        """Eliminar seguimiento específico"""
        if not self._validar_ids_y_fecha(id_usuario, id_habito, fecha):
            return False

        try:
            with self.db.get_session() as session:
                seguimiento_eliminado = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha == fecha
                    )
                ).delete()

                if seguimiento_eliminado:
                    logger.info(f"Seguimiento eliminado para usuario {id_usuario}, hábito {id_habito}, fecha {fecha}")
                    return True

                logger.warning(f"Seguimiento no encontrado para eliminar")
                return False

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando seguimiento: {e}")
            return False

    def eliminar_seguimientos_por_habito(self, id_habito: int) -> bool:
        """Eliminar todos los seguimientos de un hábito"""
        if not self._validar_id(id_habito):
            return False

        try:
            with self.db.get_session() as session:
                seguimientos_eliminados = session.query(SeguimientoDiario).filter(
                    SeguimientoDiario.id_habito == id_habito
                ).delete()

                logger.info(f"Eliminados {seguimientos_eliminados} seguimientos del hábito {id_habito}")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando seguimientos del hábito {id_habito}: {e}")
            return False

    def eliminar_seguimientos_por_usuario(self, id_usuario: int) -> bool:
        """Eliminar todos los seguimientos de un usuario"""
        if not self._validar_id(id_usuario):
            return False

        try:
            with self.db.get_session() as session:
                seguimientos_eliminados = session.query(SeguimientoDiario).filter(
                    SeguimientoDiario.id_usuario == id_usuario
                ).delete()

                logger.info(f"Eliminados {seguimientos_eliminados} seguimientos del usuario {id_usuario}")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando seguimientos del usuario {id_usuario}: {e}")
            return False

    def obtener_estadisticas_habito(self, id_habito: int, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Obtener estadísticas de un hábito específico en un rango de fechas"""
        if not self._validar_id(id_habito) or fecha_inicio > fecha_fin:
            return {}

        try:
            with self.db.get_session() as session:
                total_seguimientos = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha.between(fecha_inicio, fecha_fin)
                    )
                ).count()

                completados = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha.between(fecha_inicio, fecha_fin),
                        SeguimientoDiario.estado == 'completado'
                    )
                ).count()

                return {
                    'id_habito': id_habito,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'total_seguimientos': total_seguimientos,
                    'completados': completados,
                    'pendientes': total_seguimientos - completados,
                    'porcentaje_completado': (completados / total_seguimientos * 100) if total_seguimientos > 0 else 0
                }

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo estadísticas del hábito {id_habito}: {e}")
            return {}

    def obtener_estadisticas_usuario(self, id_usuario: int, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Obtener estadísticas generales de un usuario en un rango de fechas"""
        if not self._validar_id(id_usuario) or fecha_inicio > fecha_fin:
            return {}

        try:
            with self.db.get_session() as session:
                total_seguimientos = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.fecha.between(fecha_inicio, fecha_fin)
                    )
                ).count()

                completados = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.fecha.between(fecha_inicio, fecha_fin),
                        SeguimientoDiario.estado == 'completado'
                    )
                ).count()

                # Obtener hábitos únicos del usuario
                habitos_unicos = session.query(SeguimientoDiario.id_habito).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.fecha.between(fecha_inicio, fecha_fin)
                    )
                ).distinct().count()

                return {
                    'id_usuario': id_usuario,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'total_seguimientos': total_seguimientos,
                    'completados': completados,
                    'pendientes': total_seguimientos - completados,
                    'porcentaje_completado': (completados / total_seguimientos * 100) if total_seguimientos > 0 else 0,
                    'habitos_activos': habitos_unicos
                }

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo estadísticas del usuario {id_usuario}: {e}")
            return {}

    def obtener_racha_habito(self, id_usuario: int, id_habito: int, fecha_referencia: date = None) -> int:
        """Obtener la racha actual de días completados consecutivos de un hábito"""
        if fecha_referencia is None:
            fecha_referencia = date.today()

        if not self._validar_ids_y_fecha(id_usuario, id_habito, fecha_referencia):
            return 0

        try:
            with self.db.get_session() as session:
                # Obtener seguimientos completados ordenados por fecha descendente
                seguimientos = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.fecha <= fecha_referencia,
                        SeguimientoDiario.estado == 'completado'
                    )
                ).order_by(desc(SeguimientoDiario.fecha)).all()

                if not seguimientos:
                    return 0

                racha = 0
                fecha_actual = fecha_referencia

                for seguimiento in seguimientos:
                    if seguimiento.fecha == fecha_actual:
                        racha += 1
                        fecha_actual -= timedelta(days=1)
                    else:
                        break

                return racha

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo racha del hábito {id_habito}: {e}")
            return 0

    # Métodos privados de validación
    def _validar_id(self, id_valor: int) -> bool:
        """Validar que el ID sea válido"""
        return isinstance(id_valor, int) and id_valor > 0

    def _validar_ids_y_fecha(self, id_usuario: int, id_habito: int, fecha: date) -> bool:
        """Validar IDs y fecha"""
        return (self._validar_id(id_usuario) and
                self._validar_id(id_habito) and
                isinstance(fecha, date))

    def _validar_ids_fecha_y_estado(self, id_usuario: int, id_habito: int, fecha: date, estado: str) -> bool:
        """Validar IDs, fecha y estado"""
        return (self._validar_ids_y_fecha(id_usuario, id_habito, fecha) and
                estado in self.ESTADOS_VALIDOS)

    def _validar_datos_seguimiento(self, seguimiento_data: dict) -> None:
        """Validar datos para crear seguimiento"""
        campos_requeridos = ['id_usuario', 'id_habito', 'fecha', 'estado']
        for campo in campos_requeridos:
            if campo not in seguimiento_data or seguimiento_data[campo] is None:
                raise ValueError(f"Campo requerido '{campo}' faltante o nulo")

        if seguimiento_data['estado'] not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado '{seguimiento_data['estado']}' no válido. Estados válidos: {self.ESTADOS_VALIDOS}")

        if not isinstance(seguimiento_data['fecha'], date):
            raise ValueError("La fecha debe ser un objeto date válido")

    def _validar_datos_actualizacion(self, seguimiento_data: dict) -> None:
        """Validar datos para actualizar seguimiento"""
        if 'estado' in seguimiento_data and seguimiento_data['estado'] not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado '{seguimiento_data['estado']}' no válido. Estados válidos: {self.ESTADOS_VALIDOS}")

        if 'fecha' in seguimiento_data and not isinstance(seguimiento_data['fecha'], date):
            raise ValueError("La fecha debe ser un objeto date válido")