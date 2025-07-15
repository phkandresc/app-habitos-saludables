from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

from db.Connection import DatabaseConnection
from model.ComunidadCategoria import ComunidadCategoria

# Configurar logging
logger = logging.getLogger(__name__)


class ComunidadCategoriaRepository:
    """Repositorio para operaciones de base de datos de ComunidadCategoria"""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_relacion(self, id_comunidad: int, id_categoria: int) -> Optional[ComunidadCategoria]:
        """Crear relación entre comunidad y categoría"""
        try:
            if not self._validar_ids(id_comunidad, id_categoria):
                return None

            with self.db.get_session() as session:
                # Verificar si la relación ya existe
                relacion_existente = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad,
                    ComunidadCategoria.id_categoria == id_categoria
                ).first()

                if relacion_existente:
                    logger.warning(f"Relación ya existe: comunidad {id_comunidad}, categoría {id_categoria}")
                    return relacion_existente

                # Crear nueva relación
                relacion = ComunidadCategoria(
                    id_comunidad=id_comunidad,
                    id_categoria=id_categoria
                )
                
                session.add(relacion)
                session.flush()
                session.expunge(relacion)
                
                logger.info(f"Relación ComunidadCategoria creada: comunidad {id_comunidad}, categoría {id_categoria}")
                return relacion

        except SQLAlchemyError as e:
            logger.error(f"Error de BD creando relación ComunidadCategoria: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado creando relación ComunidadCategoria: {e}")
            return None

    def obtener_categorias_de_comunidad(self, id_comunidad: int) -> List[int]:
        """Obtener IDs de categorías asociadas a una comunidad"""
        if not self._validar_id(id_comunidad):
            return []

        try:
            with self.db.get_session() as session:
                relaciones = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad
                ).all()

                return [relacion.id_categoria for relacion in relaciones]

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo categorías de comunidad {id_comunidad}: {e}")
            return []

    def obtener_comunidades_de_categoria(self, id_categoria: int) -> List[int]:
        """Obtener IDs de comunidades asociadas a una categoría"""
        if not self._validar_id(id_categoria):
            return []

        try:
            with self.db.get_session() as session:
                relaciones = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_categoria == id_categoria
                ).all()

                return [relacion.id_comunidad for relacion in relaciones]

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo comunidades de categoría {id_categoria}: {e}")
            return []

    def eliminar_relacion(self, id_comunidad: int, id_categoria: int) -> bool:
        """Eliminar relación entre comunidad y categoría"""
        try:
            if not self._validar_ids(id_comunidad, id_categoria):
                return False

            with self.db.get_session() as session:
                relacion = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad,
                    ComunidadCategoria.id_categoria == id_categoria
                ).first()

                if relacion:
                    session.delete(relacion)
                    logger.info(f"Relación ComunidadCategoria eliminada: comunidad {id_comunidad}, categoría {id_categoria}")
                    return True
                else:
                    logger.warning(f"Relación no encontrada: comunidad {id_comunidad}, categoría {id_categoria}")
                    return False

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando relación ComunidadCategoria: {e}")
            return False

    def eliminar_todas_relaciones_comunidad(self, id_comunidad: int) -> bool:
        """Eliminar todas las relaciones de una comunidad"""
        try:
            if not self._validar_id(id_comunidad):
                return False

            with self.db.get_session() as session:
                relaciones_eliminadas = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad
                ).delete()

                logger.info(f"Eliminadas {relaciones_eliminadas} relaciones de comunidad {id_comunidad}")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Error eliminando relaciones de comunidad {id_comunidad}: {e}")
            return False

    def verificar_relacion_existe(self, id_comunidad: int, id_categoria: int) -> bool:
        """Verificar si existe relación entre comunidad y categoría"""
        try:
            if not self._validar_ids(id_comunidad, id_categoria):
                return False

            with self.db.get_session() as session:
                relacion = session.query(ComunidadCategoria).filter(
                    ComunidadCategoria.id_comunidad == id_comunidad,
                    ComunidadCategoria.id_categoria == id_categoria
                ).first()

                return relacion is not None

        except SQLAlchemyError as e:
            logger.error(f"Error verificando relación ComunidadCategoria: {e}")
            return False

    def _validar_id(self, id_valor: int) -> bool:
        """Validar que un ID sea válido"""
        return isinstance(id_valor, int) and id_valor > 0

    def _validar_ids(self, id_comunidad: int, id_categoria: int) -> bool:
        """Validar que ambos IDs sean válidos"""
        return self._validar_id(id_comunidad) and self._validar_id(id_categoria)
