from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import List, Optional
import logging

from db.Connection import DatabaseConnection
from model.Comunidad import Comunidad
from model.ComunidadCategoria import ComunidadCategoria

# Configurar logging
logger = logging.getLogger(__name__)


class ComunidadRepository:
    """Repositorio para operaciones de base de datos de Comunidad"""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_comunidad(self, comunidad_data: dict) -> Optional[Comunidad]:
        """Crear comunidad en BD"""
        try:
            self._validar_datos_comunidad(comunidad_data)

            with self.db.get_session() as session:
                comunidad = Comunidad(**comunidad_data)
                session.add(comunidad)
                session.flush()
                session.expunge(comunidad)
                logger.info(f"Comunidad creada exitosamente: {comunidad.id_comunidad}")
                return comunidad

        except ValueError as e:
            logger.error(f"Datos inválidos para crear comunidad: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error de BD creando comunidad: {e}")
            return None

    def obtener_comunidad_por_id(self, id_comunidad: int) -> Optional[Comunidad]:
        """Obtener comunidad por ID"""
        if not self._validar_id(id_comunidad):
            return None

        try:
            with self.db.get_session() as session:
                comunidad = session.query(Comunidad).filter(
                    Comunidad.id_comunidad == id_comunidad
                ).first()

                if comunidad:
                    session.expunge(comunidad)
                    return comunidad
                return None

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo comunidad {id_comunidad}: {e}")
            return None

    def obtener_comunidades_por_creador(self, id_creador: int) -> List[Comunidad]:
        """Obtener todas las comunidades creadas por un usuario"""
        if not self._validar_id(id_creador):
            return []

        try:
            with self.db.get_session() as session:
                comunidades = session.query(Comunidad).filter(
                    Comunidad.id_creador == id_creador
                ).order_by(Comunidad.nombre).all()

                for comunidad in comunidades:
                    session.expunge(comunidad)
                return comunidades

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo comunidades del creador {id_creador}: {e}")
            return []

    def obtener_comunidades_por_categoria(self, id_categoria: int) -> List[Comunidad]:
        """Obtener comunidades por categoría"""
        if not self._validar_id(id_categoria):
            return []

        try:
            with self.db.get_session() as session:
                comunidades = session.query(Comunidad).join(
                    ComunidadCategoria
                ).filter(
                    ComunidadCategoria.id_categoria == id_categoria
                ).order_by(Comunidad.nombre).all()

                for comunidad in comunidades:
                    session.expunge(comunidad)
                return comunidades

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo comunidades por categoría {id_categoria}: {e}")
            return []

    def obtener_todas_comunidades(self) -> List[Comunidad]:
        """Obtener todas las comunidades"""
        try:
            with self.db.get_session() as session:
                comunidades = session.query(Comunidad).order_by(Comunidad.nombre).all()

                for comunidad in comunidades:
                    session.expunge(comunidad)
                return comunidades

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo todas las comunidades: {e}")
            return []

    def actualizar_comunidad(self, id_comunidad: int, comunidad_data: dict) -> Optional[Comunidad]:
        """Actualizar comunidad"""
        if not self._validar_id(id_comunidad):
            return None

        try:
            self._validar_datos_comunidad_actualizacion(comunidad_data)

            with self.db.get_session() as session:
                comunidad = session.query(Comunidad).filter(
                    Comunidad.id_comunidad == id_comunidad
                ).first()

                if not comunidad:
                    logger.warning(f"Comunidad {id_comunidad} no encontrada para actualizar")
                    return None

                # Actualizar solo campos válidos
                for key, value in comunidad_data.items():
                    if hasattr(comunidad, key) and key != 'id_comunidad':
                        setattr(comunidad, key, value)

                session.flush()
                session.expunge(comunidad)
                logger.info(f"Comunidad {id_comunidad} actualizada exitosamente")
                return comunidad

        except ValueError as e:
            logger.error(f"Datos inválidos para actualizar comunidad {id_comunidad}: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error actualizando comunidad {id_comunidad}: {e}")
            return None

    def eliminar_comunidad(self, id_comunidad: int) -> bool:
        """Eliminar comunidad y sus relaciones de categorías"""
        if not self._validar_id(id_comunidad):
            return False

        try:
            with self.db.get_session() as session:
                # Eliminar relaciones con categorías primero
                session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad
                ).delete()

                # Eliminar la comunidad
                comunidad_eliminada = session.query(Comunidad).filter(
                    Comunidad.id_comunidad == id_comunidad
                ).delete()

                if comunidad_eliminada:
                    logger.info(f"Comunidad {id_comunidad} eliminada exitosamente")
                    return True

                logger.warning(f"Comunidad {id_comunidad} no encontrada para eliminar")
                return False

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando comunidad {id_comunidad}: {e}")
            return False

    def buscar_comunidades_por_nombre(self, nombre: str) -> List[Comunidad]:
        """Buscar comunidades por nombre (búsqueda parcial)"""
        if not nombre or len(nombre.strip()) == 0:
            return []

        try:
            with self.db.get_session() as session:
                comunidades = session.query(Comunidad).filter(
                    Comunidad.nombre.ilike(f"%{nombre}%")
                ).order_by(Comunidad.nombre).all()

                for comunidad in comunidades:
                    session.expunge(comunidad)
                return comunidades

        except SQLAlchemyError as e:
            logger.error(f"Error buscando comunidades por nombre '{nombre}': {e}")
            return []

    def agregar_categoria_a_comunidad(self, id_comunidad: int, id_categoria: int) -> bool:
        """Agregar categoría a una comunidad"""
        if not self._validar_id(id_comunidad) or not self._validar_id(id_categoria):
            return False

        try:
            with self.db.get_session() as session:
                # Verificar que no existe ya la relación
                existe = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad,
                    ComunidadCategoria.id_categoria == id_categoria
                ).first()

                if existe:
                    logger.warning(f"La comunidad {id_comunidad} ya tiene la categoría {id_categoria}")
                    return False

                nueva_relacion = ComunidadCategoria(
                    id_comunidad=id_comunidad,
                    id_categoria=id_categoria
                )
                session.add(nueva_relacion)
                logger.info(f"Categoría {id_categoria} agregada a comunidad {id_comunidad}")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Error agregando categoría {id_categoria} a comunidad {id_comunidad}: {e}")
            return False

    def remover_categoria_de_comunidad(self, id_comunidad: int, id_categoria: int) -> bool:
        """Remover categoría de una comunidad"""
        if not self._validar_id(id_comunidad) or not self._validar_id(id_categoria):
            return False

        try:
            with self.db.get_session() as session:
                relacion_eliminada = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad,
                    ComunidadCategoria.id_categoria == id_categoria
                ).delete()

                if relacion_eliminada:
                    logger.info(f"Categoría {id_categoria} removida de comunidad {id_comunidad}")
                    return True

                logger.warning(f"No se encontró relación entre comunidad {id_comunidad} y categoría {id_categoria}")
                return False

        except SQLAlchemyError as e:
            logger.error(f"Error removiendo categoría {id_categoria} de comunidad {id_comunidad}: {e}")
            return False

    def obtener_categorias_de_comunidad(self, id_comunidad: int) -> List[int]:
        """Obtener IDs de categorías de una comunidad"""
        if not self._validar_id(id_comunidad):
            return []

        try:
            with self.db.get_session() as session:
                categorias = session.query(ComunidadCategoria.id_categoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad
                ).all()

                return [categoria[0] for categoria in categorias]

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo categorías de comunidad {id_comunidad}: {e}")
            return []

    # Métodos privados de validación
    def _validar_id(self, id_valor: int) -> bool:
        """Validar que el ID sea válido"""
        return isinstance(id_valor, int) and id_valor > 0

    def _validar_datos_comunidad(self, comunidad_data: dict) -> None:
        """Validar datos para crear comunidad"""
        campos_requeridos = ['nombre']
        for campo in campos_requeridos:
            if campo not in comunidad_data or not comunidad_data[campo]:
                raise ValueError(f"Campo requerido '{campo}' faltante o vacío")

        if len(comunidad_data.get('nombre', '')) > 50:
            raise ValueError("El nombre de la comunidad no puede exceder 50 caracteres")

        if 'id_creador' in comunidad_data and not self._validar_id(comunidad_data['id_creador']):
            raise ValueError("El id_creador debe ser un entero positivo válido")

    def _validar_datos_comunidad_actualizacion(self, comunidad_data: dict) -> None:
        """Validar datos para actualizar comunidad"""
        if 'nombre' in comunidad_data and len(comunidad_data['nombre']) > 50:
            raise ValueError("El nombre de la comunidad no puede exceder 50 caracteres")

        if 'id_creador' in comunidad_data and not self._validar_id(comunidad_data['id_creador']):
            raise ValueError("El id_creador debe ser un entero positivo válido")