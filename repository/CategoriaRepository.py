from sqlalchemy.exc import SQLAlchemyError
from db.Connection import DatabaseConnection
from model.Categorias import Categoria
from typing import List, Optional

class CategoriasRepository:
    """Repositorio para operaciones de base de datos de Categoria"""

    def __init__(self):
        self.db = DatabaseConnection()

    def crear_categoria(self, categoria_data: dict) -> Optional[Categoria]:
        """Crear categoría en BD"""
        try:
            with self.db.get_session() as session:
                categoria = Categoria(**categoria_data)
                session.add(categoria)
                session.flush()  # Para obtener el ID antes del commit
                session.expunge(categoria)
                return categoria
        except SQLAlchemyError as e:
            print(f"Error creando categoría: {e}")
            return None

    def obtener_categoria_por_id(self, id_categoria: int) -> Optional[Categoria]:
        """Obtener categoría por ID"""
        try:
            with self.db.get_session() as session:
                categoria = session.query(Categoria).filter(
                    Categoria.id_categoria == id_categoria
                ).first()
                if categoria:
                    session.expunge(categoria)
                    return categoria
                return None
        except SQLAlchemyError as e:
            print(f"Error obteniendo categoría: {e}")
            return None

    def obtener_categoria_por_nombre(self, nombre: str) -> Optional[Categoria]:
        """Obtener categoría por nombre"""
        try:
            with self.db.get_session() as session:
                categoria = session.query(Categoria).filter(
                    Categoria.nombre == nombre
                ).first()
                if categoria:
                    session.expunge(categoria)
                    return categoria
                return None
        except SQLAlchemyError as e:
            print(f"Error obteniendo categoría por nombre: {e}")
            return None

    def obtener_todas_categorias(self) -> List[Categoria]:
        """Obtener todas las categorías"""
        try:
            with self.db.get_session() as session:
                categorias = session.query(Categoria).order_by(Categoria.nombre).all()
                for categoria in categorias:
                    session.expunge(categoria)
                return categorias
        except SQLAlchemyError as e:
            print(f"Error obteniendo categorías: {e}")
            return []

    def actualizar_categoria(self, id_categoria: int, categoria_data: dict) -> Optional[Categoria]:
        """Actualizar categoría"""
        try:
            with self.db.get_session() as session:
                categoria = session.query(Categoria).filter(
                    Categoria.id_categoria == id_categoria
                ).first()
                if categoria:
                    for key, value in categoria_data.items():
                        if hasattr(categoria, key):
                            setattr(categoria, key, value)
                    session.flush()
                    session.expunge(categoria)
                    return categoria
                return None
        except SQLAlchemyError as e:
            print(f"Error actualizando categoría: {e}")
            return None

    def eliminar_categoria(self, id_categoria: int) -> bool:
        """Eliminar categoría"""
        try:
            with self.db.get_session() as session:
                categoria = session.query(Categoria).filter(
                    Categoria.id_categoria == id_categoria
                ).first()
                if categoria:
                    session.delete(categoria)
                    return True
                return False
        except SQLAlchemyError as e:
            print(f"Error eliminando categoría: {e}")
            return False

    def existe_categoria(self, nombre: str) -> bool:
        """Verificar si existe una categoría con el nombre dado"""
        try:
            with self.db.get_session() as session:
                existe = session.query(Categoria).filter(
                    Categoria.nombre == nombre
                ).first() is not None
                return existe
        except SQLAlchemyError as e:
            print(f"Error verificando existencia de categoría: {e}")
            return False

    def contar_categorias(self) -> int:
        """Contar el total de categorías"""
        try:
            with self.db.get_session() as session:
                count = session.query(Categoria).count()
                return count
        except SQLAlchemyError as e:
            print(f"Error contando categorías: {e}")
            return 0