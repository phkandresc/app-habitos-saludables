from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from datetime import date
from typing import List, Optional, Dict, Any
import logging

from db.Connection import DatabaseConnection
from model.Habito import Habito
from model.SeguimientoDiario import SeguimientoDiario

# Configurar logging
logger = logging.getLogger(__name__)


class HabitosRepository:
    """Repositorio para operaciones de base de datos de Habito"""

    # Constantes de días de la semana
    DIAS_SEMANA = {
        0: "Lunes", 1: "Martes", 2: "Miércoles",
        3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
    }

    ESTADOS_VALIDOS = {"pendiente", "completado", "no_completado"}

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_habito(self, habito_data: dict) -> Optional[Habito]:
        """Crear hábito en BD"""
        try:
            self._validar_datos_habito(habito_data)

            with self.db.get_session() as session:
                habito = Habito(**habito_data)
                session.add(habito)
                session.flush()
                session.expunge(habito)
                logger.info(f"Hábito creado exitosamente: {habito.id_habito}")
                return habito

        except ValueError as e:
            logger.error(f"Datos inválidos para crear hábito: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error de BD creando hábito: {e}")
            return None

    def obtener_habito_por_id(self, id_habito: int) -> Optional[Habito]:
        """Obtener hábito por ID"""
        if not self._validar_id(id_habito):
            return None

        try:
            with self.db.get_session() as session:
                habito = session.query(Habito).filter(
                    Habito.id_habito == id_habito
                ).first()

                if habito:
                    session.expunge(habito)
                    return habito
                return None

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo hábito {id_habito}: {e}")
            return None

    def obtener_habitos_por_usuario(self, id_usuario: int) -> List[Habito]:
        """Obtener todos los hábitos de un usuario"""
        if not self._validar_id(id_usuario):
            return []

        try:
            with self.db.get_session() as session:
                habitos = session.query(Habito).filter(
                    Habito.id_usuario == id_usuario
                ).order_by(Habito.nombre).all()

                for habito in habitos:
                    session.expunge(habito)
                return habitos

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo hábitos del usuario {id_usuario}: {e}")
            return []

    def obtener_habitos_por_categoria(self, id_categoria: int) -> List[Habito]:
        """Obtener hábitos por categoría"""
        if not self._validar_id(id_categoria):
            return []

        try:
            with self.db.get_session() as session:
                habitos = session.query(Habito).filter(
                    Habito.id_categoria == id_categoria
                ).order_by(Habito.nombre).all()

                for habito in habitos:
                    session.expunge(habito)
                return habitos

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo hábitos por categoría {id_categoria}: {e}")
            return []

    def obtener_habitos_por_fecha(self, id_usuario: int, fecha: date) -> List[Dict[str, Any]]:
        """Obtener hábitos del usuario que corresponden a un día específico según su frecuencia"""
        if not self._validar_id(id_usuario) or not isinstance(fecha, date):
            return []

        try:
            with self.db.get_session() as session:
                dia_semana = self._obtener_dia_semana(fecha)

                # Query optimizada para obtener hábitos con su estado
                query = session.query(
                    Habito,
                    SeguimientoDiario.estado
                ).outerjoin(
                    SeguimientoDiario,
                    and_(
                        Habito.id_habito == SeguimientoDiario.id_habito,
                        SeguimientoDiario.fecha == fecha,
                        SeguimientoDiario.id_usuario == id_usuario
                    )
                ).filter(
                    Habito.id_usuario == id_usuario,
                    Habito.frecuencia.contains(dia_semana)
                ).order_by(Habito.nombre)

                resultados = query.all()
                habitos_con_estado = []

                for habito, estado in resultados:
                    session.expunge(habito)
                    habitos_con_estado.append({
                        'habito': habito,
                        'estado': estado or 'pendiente'
                    })

                return habitos_con_estado

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo hábitos por fecha {fecha} del usuario {id_usuario}: {e}")
            return []

    def obtener_habitos_con_estado_por_usuario(self, id_usuario: int, fecha: Optional[date] = None) -> List[
        Dict[str, Any]]:
        """Obtener hábitos de un usuario con su estado para una fecha específica"""
        if fecha is None:
            fecha = date.today()

        return self.obtener_habitos_por_fecha(id_usuario, fecha)


    def actualizar_habito(self, id_habito: int, habito_data: dict) -> Optional[Habito]:
        """Actualizar hábito"""
        if not self._validar_id(id_habito):
            return None

        try:
            self._validar_datos_habito_actualizacion(habito_data)

            with self.db.get_session() as session:
                habito = session.query(Habito).filter(
                    Habito.id_habito == id_habito
                ).first()

                if not habito:
                    logger.warning(f"Hábito {id_habito} no encontrado para actualizar")
                    return None

                # Actualizar solo campos válidos
                for key, value in habito_data.items():
                    if hasattr(habito, key) and key != 'id_habito':
                        setattr(habito, key, value)

                session.flush()
                session.expunge(habito)
                logger.info(f"Hábito {id_habito} actualizado exitosamente")
                return habito

        except ValueError as e:
            logger.error(f"Datos inválidos para actualizar hábito {id_habito}: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error actualizando hábito {id_habito}: {e}")
            return None

    def eliminar_habito(self, id_habito: int) -> bool:
        """Eliminar hábito y sus seguimientos asociados"""
        if not self._validar_id(id_habito):
            return False

        try:
            with self.db.get_session() as session:
                # Eliminar seguimientos asociados primero
                session.query(SeguimientoDiario).filter(
                    SeguimientoDiario.id_habito == id_habito
                ).delete()

                # Eliminar el hábito
                habito_eliminado = session.query(Habito).filter(
                    Habito.id_habito == id_habito
                ).delete()

                if habito_eliminado:
                    logger.info(f"Hábito {id_habito} eliminado exitosamente")
                    return True

                logger.warning(f"Hábito {id_habito} no encontrado para eliminar")
                return False

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando hábito {id_habito}: {e}")
            return False

    def actualizar_estado_habito_fecha(self, id_habito: int, id_usuario: int,
                                       nuevo_estado: str, fecha: date) -> bool:
        """Actualizar o crear el estado de un hábito para una fecha específica"""
        if not self._validar_ids_y_estado(id_habito, id_usuario, nuevo_estado):
            return False

        if not isinstance(fecha, date):
            logger.error("La fecha debe ser un objeto date válido")
            return False

        try:
            with self.db.get_session() as session:
                # Buscar seguimiento existente
                seguimiento = session.query(SeguimientoDiario).filter(
                    and_(
                        SeguimientoDiario.id_habito == id_habito,
                        SeguimientoDiario.id_usuario == id_usuario,
                        SeguimientoDiario.fecha == fecha
                    )
                ).first()

                if seguimiento:
                    seguimiento.estado = nuevo_estado
                    logger.info(f"Estado actualizado para hábito {id_habito} en fecha {fecha}")
                else:
                    nuevo_seguimiento = SeguimientoDiario(
                        fecha=fecha,
                        id_habito=id_habito,
                        id_usuario=id_usuario,
                        estado=nuevo_estado,
                        observaciones='',
                        edad=0
                    )
                    session.add(nuevo_seguimiento)
                    logger.info(f"Nuevo seguimiento creado para hábito {id_habito} en fecha {fecha}")

                return True

        except SQLAlchemyError as e:
            logger.error(f"Error actualizando estado del hábito {id_habito} para fecha {fecha}: {e}")
            return False

    def actualizar_estado_habito(self, id_habito: int, id_usuario: int, nuevo_estado: str) -> bool:
        """Actualizar o crear el estado de un hábito para la fecha actual"""
        return self.actualizar_estado_habito_fecha(id_habito, id_usuario, nuevo_estado, date.today())

    def obtener_estadisticas_usuario(self, id_usuario: int, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Obtener estadísticas de hábitos para un usuario en un rango de fechas"""
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

                return {
                    'total_seguimientos': total_seguimientos,
                    'completados': completados,
                    'porcentaje_completado': (completados / total_seguimientos * 100) if total_seguimientos > 0 else 0
                }

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo estadísticas del usuario {id_usuario}: {e}")
            return {}

    # Métodos privados de validación y utilidad
    def _validar_id(self, id_valor: int) -> bool:
        """Validar que el ID sea válido"""
        return isinstance(id_valor, int) and id_valor > 0

    def _validar_ids_y_estado(self, id_habito: int, id_usuario: int, estado: str) -> bool:
        """Validar IDs y estado"""
        return (self._validar_id(id_habito) and
                self._validar_id(id_usuario) and
                estado in self.ESTADOS_VALIDOS)

    def _validar_datos_habito(self, habito_data: dict) -> None:
        """Validar datos para crear hábito"""
        campos_requeridos = ['nombre', 'id_usuario']
        for campo in campos_requeridos:
            if campo not in habito_data or not habito_data[campo]:
                raise ValueError(f"Campo requerido '{campo}' faltante o vacío")

        if len(habito_data.get('nombre', '')) > 100:
            raise ValueError("El nombre del hábito no puede exceder 100 caracteres")

    def _validar_datos_habito_actualizacion(self, habito_data: dict) -> None:
        """Validar datos para actualizar hábito"""
        if 'nombre' in habito_data and len(habito_data['nombre']) > 100:
            raise ValueError("El nombre del hábito no puede exceder 100 caracteres")

    def _obtener_dia_semana(self, fecha: date) -> str:
        """Obtener el nombre del día de la semana en español"""
        return self.DIAS_SEMANA[fecha.weekday()]