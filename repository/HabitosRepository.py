from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.Connection import DatabaseConnection
from model.Habito import Habito  # Cambio: singular y nombre correcto
from typing import List, Optional, Dict
from datetime import date


class HabitosRepository:
    """Repositorio para operaciones CRUD de Habitos"""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_habito(self, habito_data: Dict) -> Optional[Habito]:
        """Crear un nuevo hábito"""
        try:
            with self.db.get_session() as session:
                nuevo_habito = Habito(
                    nombre=habito_data['nombre'],
                    frecuencia=habito_data['frecuencia'],
                    categoria=habito_data['categoria'],
                    fecha_creacion=habito_data.get('fecha_creacion', date.today()),
                    id_categoria=habito_data.get('id_categoria')
                )

                session.add(nuevo_habito)
                session.flush()
                session.expunge(nuevo_habito)
                return nuevo_habito

        except SQLAlchemyError as e:
            print(f"Error creando hábito: {e}")
            return None

    def obtener_habito_por_id(self, id_habito: int) -> Optional[Habito]:
        """Obtener hábito por ID"""
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
            print(f"Error obteniendo hábito: {e}")
            return None

    def obtener_todos_habitos(self) -> List[Habito]:
        """Obtener todos los hábitos"""
        try:
            with self.db.get_session() as session:
                habitos = session.query(Habito).all()
                # Expunge todos los objetos para hacerlos independientes
                for habito in habitos:
                    session.expunge(habito)
                return habitos
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos: {e}")
            return []

    def obtener_habitos_por_categoria(self, categoria: str) -> List[Habito]:
        """Obtener hábitos por categoría"""
        try:
            with self.db.get_session() as session:
                habitos = session.query(Habito).filter(
                    Habito.categoria.ilike(f"%{categoria}%")
                ).all()
                for habito in habitos:
                    session.expunge(habito)
                return habitos
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos por categoría: {e}")
            return []

    def obtener_habitos_por_categoria_id(self, id_categoria: int) -> List[Habito]:
        """Obtener hábitos por ID de categoría"""
        try:
            with self.db.get_session() as session:
                habitos = session.query(Habito).filter(
                    Habito.id_categoria == id_categoria
                ).all()
                for habito in habitos:
                    session.expunge(habito)
                return habitos
        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos por ID categoría: {e}")
            return []

    def buscar_habitos_por_nombre(self, nombre: str) -> List[Habito]:
        """Buscar hábitos por nombre (búsqueda parcial)"""
        try:
            with self.db.get_session() as session:
                habitos = session.query(Habito).filter(
                    Habito.nombre.ilike(f"%{nombre}%")
                ).all()
                for habito in habitos:
                    session.expunge(habito)
                return habitos
        except SQLAlchemyError as e:
            print(f"Error buscando hábitos por nombre: {e}")
            return []

    def actualizar_habito(self, id_habito: int, habito_data: Dict) -> Optional[Habito]:
        """Actualizar un hábito existente"""
        try:
            with self.db.get_session() as session:
                habito = session.query(Habito).filter(
                    Habito.id_habito == id_habito
                ).first()

                if habito:
                    for key, value in habito_data.items():
                        if hasattr(habito, key) and key != 'id_habito':
                            setattr(habito, key, value)

                    session.flush()
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
                habito = session.query(Habito).filter(
                    Habito.id_habito == id_habito
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
                return session.query(Habito).filter(
                    Habito.id_habito == id_habito
                ).first() is not None
        except SQLAlchemyError as e:
            print(f"Error verificando existencia del hábito: {e}")
            return False

    def obtener_habitos_recientes(self, dias: int = 7) -> List[Habito]:
        """Obtener hábitos creados en los últimos N días"""
        try:
            from datetime import timedelta

            fecha_limite = date.today() - timedelta(days=dias)

            with self.db.get_session() as session:
                habitos = session.query(Habito).filter(
                    Habito.fecha_creacion >= fecha_limite
                ).order_by(Habito.fecha_creacion.desc()).all()

                for habito in habitos:
                    session.expunge(habito)
                return habitos

        except SQLAlchemyError as e:
            print(f"Error obteniendo hábitos recientes: {e}")
            return []