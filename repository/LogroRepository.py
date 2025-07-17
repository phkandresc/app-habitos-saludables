from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from db.Connection import DatabaseConnection
from model.Logro import Logro
from model.Desbloquea import Desbloquea
from model.Usuario import Usuario
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

    def obtener_ranking_general(self) -> List[Dict[str, Any]]:
        """Obtener ranking general de usuarios por puntos totales."""
        try:
            with self.db.get_session() as session:
                # Consulta SQL equivalente a la proporcionada
                resultado = session.query(
                    Usuario.id_usuario,
                    Usuario.nombre_usuario,
                    func.coalesce(func.sum(Logro.puntos), 0).label('puntos_totales')
                ).outerjoin(
                    Desbloquea, Usuario.id_usuario == Desbloquea.id_usuario
                ).outerjoin(
                    Logro, Desbloquea.id_logro == Logro.id_logro
                ).group_by(
                    Usuario.id_usuario, Usuario.nombre_usuario
                ).order_by(
                    func.coalesce(func.sum(Logro.puntos), 0).desc()
                ).all()

                # Convertir resultado a lista de diccionarios
                ranking = []
                for i, (id_usuario, nombre_usuario, puntos_totales) in enumerate(resultado):
                    ranking.append({
                        'posicion': i + 1,
                        'id_usuario': id_usuario,
                        'nombre_usuario': nombre_usuario,
                        'puntos_totales': int(puntos_totales or 0)
                    })

                logger.info(f"Ranking general obtenido: {len(ranking)} usuarios")
                return ranking

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo ranking general: {e}")
            return []

    def obtener_puntos_por_id_usuario(self, id_usuario: int) -> int:
        """Obtener puntos totales de un usuario por su ID."""
        try:
            with self.db.get_session() as session:
                puntos_totales = session.query(
                    func.coalesce(func.sum(Logro.puntos), 0)
                ).join(
                    Desbloquea, Desbloquea.id_logro == Logro.id_logro
                ).filter(
                    Desbloquea.id_usuario == id_usuario
                ).scalar()

                return int(puntos_totales or 0)

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo puntos para usuario {id_usuario}: {e}")
            return 0