from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from db.Connection import DatabaseConnection
from model.Nivel import Nivel
from model.AsignacionNivel import AsignacionNivel
from model.Usuario import Usuario
import logging

logger = logging.getLogger(__name__)

class NivelRepository:
    """Repositorio para la gestión de niveles y asignaciones de nivel."""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_nivel(self, nivel_data: dict) -> Optional[Nivel]:
        """Crear un nuevo nivel."""
        try:
            with self.db.get_session() as session:
                nivel = Nivel(**nivel_data)
                session.add(nivel)
                session.flush()
                session.expunge(nivel)
                logger.info(f"Nivel creado: {nivel.id_nivel}")
                return nivel
        except SQLAlchemyError as e:
            logger.error(f"Error creando nivel: {e}")
            return None

    def obtener_todos_niveles(self) -> List[Nivel]:
        """Obtener todos los niveles ordenados por puntos requeridos."""
        try:
            with self.db.get_session() as session:
                niveles = session.query(Nivel).order_by(Nivel.puntos_requeridos.asc()).all()
                for nivel in niveles:
                    session.expunge(nivel)
                logger.info(f"Obtenidos {len(niveles)} niveles")
                return niveles
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo todos los niveles: {e}")
            return []

    def obtener_nivel_por_id(self, id_nivel: int) -> Optional[Nivel]:
        """Obtener un nivel por su ID."""
        try:
            with self.db.get_session() as session:
                nivel = session.query(Nivel).filter(Nivel.id_nivel == id_nivel).first()
                if nivel:
                    session.expunge(nivel)
                return nivel
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo nivel {id_nivel}: {e}")
            return None

    def obtener_nivel_por_puntos(self, puntos: int) -> Optional[Nivel]:
        """Obtener el nivel correspondiente a una cantidad de puntos."""
        try:
            with self.db.get_session() as session:
                # Buscar el nivel más alto que el usuario puede alcanzar con sus puntos
                nivel = session.query(Nivel).filter(
                    Nivel.puntos_requeridos <= puntos
                ).order_by(Nivel.puntos_requeridos.desc()).first()

                if nivel:
                    session.expunge(nivel)
                return nivel
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo nivel para {puntos} puntos: {e}")
            return None

    def asignar_nivel_a_usuario(self, id_usuario: int, id_nivel: int) -> bool:
        """Asignar un nivel a un usuario."""
        try:
            with self.db.get_session() as session:
                # Verificar si ya existe una asignación
                asignacion_existente = session.query(AsignacionNivel).filter_by(
                    id_usuario=id_usuario
                ).first()

                if asignacion_existente:
                    # Actualizar la asignación existente
                    asignacion_existente.id_nivel = id_nivel
                    logger.info(f"Nivel actualizado para usuario {id_usuario}: nivel {id_nivel}")
                else:
                    # Crear nueva asignación
                    nueva_asignacion = AsignacionNivel(
                        id_usuario=id_usuario,
                        id_nivel=id_nivel
                    )
                    session.add(nueva_asignacion)
                    logger.info(f"Nivel asignado a usuario {id_usuario}: nivel {id_nivel}")

                return True
        except SQLAlchemyError as e:
            logger.error(f"Error asignando nivel {id_nivel} a usuario {id_usuario}: {e}")
            return False

    def obtener_nivel_usuario(self, id_usuario: int) -> Optional[Nivel]:
        """Obtener el nivel asignado a un usuario."""
        try:
            with self.db.get_session() as session:
                asignacion = session.query(AsignacionNivel).filter_by(
                    id_usuario=id_usuario
                ).first()

                if asignacion and asignacion.id_nivel:
                    nivel = session.query(Nivel).filter_by(
                        id_nivel=asignacion.id_nivel
                    ).first()
                    if nivel:
                        session.expunge(nivel)
                    return nivel
                return None
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo nivel de usuario {id_usuario}: {e}")
            return None

    def actualizar_nivel_usuario_por_puntos(self, id_usuario: int, puntos_totales: int) -> bool:
        """Actualizar el nivel de un usuario basado en sus puntos totales."""
        try:
            # Obtener el nivel correspondiente a los puntos
            nivel_correspondiente = self.obtener_nivel_por_puntos(puntos_totales)

            if nivel_correspondiente:
                return self.asignar_nivel_a_usuario(id_usuario, nivel_correspondiente.id_nivel)
            else:
                logger.warning(f"No se encontró nivel correspondiente para {puntos_totales} puntos")
                return False
        except Exception as e:
            logger.error(f"Error actualizando nivel de usuario {id_usuario} con {puntos_totales} puntos: {e}")
            return False

    def obtener_usuarios_por_nivel(self, id_nivel: int) -> List[Dict[str, Any]]:
        """Obtener todos los usuarios que tienen un nivel específico."""
        try:
            with self.db.get_session() as session:
                resultado = session.query(
                    Usuario.id_usuario,
                    Usuario.nombre_usuario,
                    Usuario.nombre,
                    Usuario.apellido
                ).join(
                    AsignacionNivel, Usuario.id_usuario == AsignacionNivel.id_usuario
                ).filter(
                    AsignacionNivel.id_nivel == id_nivel
                ).all()

                usuarios = []
                for id_usuario, nombre_usuario, nombre, apellido in resultado:
                    usuarios.append({
                        'id_usuario': id_usuario,
                        'nombre_usuario': nombre_usuario,
                        'nombre_completo': f"{nombre} {apellido}"
                    })

                logger.info(f"Obtenidos {len(usuarios)} usuarios para nivel {id_nivel}")
                return usuarios

        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo usuarios para nivel {id_nivel}: {e}")
            return []

    def eliminar_asignacion_usuario(self, id_usuario: int) -> bool:
        """Eliminar la asignación de nivel de un usuario."""
        try:
            with self.db.get_session() as session:
                asignacion = session.query(AsignacionNivel).filter_by(
                    id_usuario=id_usuario
                ).first()

                if asignacion:
                    session.delete(asignacion)
                    logger.info(f"Asignación de nivel eliminada para usuario {id_usuario}")
                    return True
                else:
                    logger.warning(f"No se encontró asignación de nivel para usuario {id_usuario}")
                    return False
        except SQLAlchemyError as e:
            logger.error(f"Error eliminando asignación de nivel para usuario {id_usuario}: {e}")
            return False
