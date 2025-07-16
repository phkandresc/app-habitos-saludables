from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from db.Connection import DatabaseConnection
from model.Logro import Logro
from model.Desbloquea import Desbloquea
import logging

logger = logging.getLogger(__name__)

class LogroRepository:
    """Repositorio para la gestión de logros."""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_logro(self, logro_data: dict) -> Optional[Logro]:
        """Crear un nuevo logro."""
        try:
            with self.db.get_session() as session:
                logro = Logro(**logro_data)
                session.add(logro)
                session.flush()
                session.expunge(logro)
                logger.info(f"Logro creado: {logro.id_logro}")
                return logro
        except SQLAlchemyError as e:
            logger.error(f"Error creando logro: {e}")
            return None

    def asociar_logro_a_usuario(self, id_usuario: int, id_logro: int) -> bool:
        """Asociar un logro a un usuario (desbloquea)."""
        try:
            with self.db.get_session() as session:
                # Verificar que no existe ya la relación
                existe = session.query(Desbloquea).filter_by(
                    id_usuario=id_usuario,
                    id_logro=id_logro
                ).first()

                if existe:
                    logger.warning(f"Usuario {id_usuario} ya desbloqueó el logro {id_logro}")
                    return False

                relacion = Desbloquea(id_usuario=id_usuario, id_logro=id_logro)
                session.add(relacion)
                logger.info(f"Usuario {id_usuario} desbloqueó logro {id_logro}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error asociando logro {id_logro} a usuario {id_usuario}: {e}")
            return False

    def obtener_logros_por_usuario(self, id_usuario: int) -> List[Logro]:
        """Obtener logros desbloqueados por un usuario."""
        try:
            with self.db.get_session() as session:
                logros = session.query(Logro).join(Desbloquea).filter(
                    Desbloquea.id_usuario == id_usuario
                ).all()
                for logro in logros:
                    session.expunge(logro)
                return logros
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo logros para usuario {id_usuario}: {e}")
            return []
