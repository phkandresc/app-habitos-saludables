from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.Connection import DatabaseConnection
from model.Habitos import Habitos
from typing import List, Optional, Dict
from datetime import date


class HabitosRepository:
    """Repositorio para operaciones CRUD de Habitos"""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_habito(self, habito_data: Dict) -> Optional[Habitos]:
        """Crear un nuevo hábito"""
        try:
            with self.db.get_session() as session:
                nuevo_habito = Habitos(
                    nombre=habito_data['nombre'],
                    frecuencia=habito_data['frecuencia'],
                    categoria=habito_data['categoria'],
                    fecha_creacion=habito_data.get('fecha_creacion', date.today()),
                    id_categoria=habito_data.get('id_categoria')
                )

                session.add(nuevo_habito)
                session.flush()  # Para obtener el ID antes del commit
                # Hacer que el objeto sea independiente de la sesión
                session.expunge(nuevo_habito)
                return nuevo_habito

        except SQLAlchemyError as e:
            print(f"Error creando hábito: {e}")
            return None

    def obtener_habito_por_id(self, id_habito: int) -> Optional[Habitos]:
        """Obtener hábito por ID"""
        try:
            with self.db.get_session() as session:
                habito = session.query(Habitos).filter(
                    Habitos.id_habito == id_habito
                ).first()

                if habito:
                    # Hacer que el objeto sea independiente de la sesión
                    session.expunge(habito)
                    return habito
                return None
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábito: {e}")
            return None

    def obtener_todos_habitos(self) -> List[Habitos]:
        """Obtener todos los hábitos"""
        try:
            with self.db.get_session() as session:
                return session.query(Habitos).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos: {e}")
            return []

    def obtener_habitos_por_categoria(self, categoria: str) -> List[Habitos]:
        """Obtener hábitos por categoría"""
        try:
            with self.db.get_session() as session:
                return session.query(Habitos).filter(
                    Habitos.categoria.ilike(f"%{categoria}%")
                ).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos por categoría: {e}")
            return []

    def obtener_habitos_por_categoria_id(self, id_categoria: int) -> List[Habitos]:
        """Obtener hábitos por ID de categoría"""
        try:
            with self.db.get_session() as session:
                return session.query(Habitos).filter(
                    Habitos.id_categoria == id_categoria
                ).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos por ID categoría: {e}")
            return []

    def buscar_habitos_por_nombre(self, nombre: str) -> List[Habitos]:
        """Buscar hábitos por nombre (búsqueda parcial)"""
        try:
            with self.db.get_session() as session:
                return session.query(Habitos).filter(
                    Habitos.nombre.ilike(f"%{nombre}%")
                ).all()
        except SQLAlchemyError as e:
            print(f"Error buscando hábitos por nombre: {e}")
            return []

    def actualizar_habito(self, id_habito: int, habito_data: Dict) -> Optional[Habitos]:
        """Actualizar un hábito existente"""
        try:
            with self.db.get_session() as session:
                habito = session.query(Habitos).filter(
                    Habitos.id_habito == id_habito
                ).first()

                if habito:
                    for key, value in habito_data.items():
                        if hasattr(habito, key) and key != 'id_habito':
                            setattr(habito, key, value)

                    session.flush()
                    # Hacer que el objeto sea independiente de la sesión
                    session.expunge(habito)
                    return habito
                return None

        except SQLAlchemyError as e:
            print(f"Error actualizando hábito: {e}")
            return None

    def eliminar_habito(self, id_habito: int) -> bool:
        """Eliminar un hábito"""
        try:
            with self.db.get_session() as session:
                habito = session.query(Habitos).filter(
                    Habitos.id_habito == id_habito
                ).first()

                if habito:
                    session.delete(habito)
                    return True
                return False

        except SQLAlchemyError as e:
            print(f"Error eliminando hábito: {e}")
            return False

    def habito_existe(self, id_habito: int) -> bool:
        """Verificar si existe un hábito"""
        try:
            with self.db.get_session() as session:
                return session.query(Habitos).filter(
                    Habitos.id_habito == id_habito
                ).first() is not None
        except SQLAlchemyError as e:
            print(f"Error verificando existencia del hábito: {e}")
            return False

    def obtener_habitos_por_usuario(self, id_usuario: int) -> List[Habitos]:
        """Obtener hábitos de un usuario específico"""
        try:
            with self.db.get_session() as session:
                return session.query(Habitos).filter(
                    Habitos.id_usuario == id_usuario
                ).all()
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos por usuario: {e}")
            return []

    def obtener_habitos_recientes(self, dias: int = 7) -> List[Habitos]:
        """Obtener hábitos creados en los últimos N días"""
        try:
            from datetime import timedelta

            fecha_limite = date.today() - timedelta(days=dias)

            with self.db.get_session() as session:
                return session.query(Habitos).filter(
                    Habitos.fecha_creacion >= fecha_limite
                ).order_by(Habitos.fecha_creacion.desc()).all()

        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos recientes: {e}")
            return []