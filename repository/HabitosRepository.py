from sqlalchemy.orm import Session
from model.Habitos import Habitos


class HabitosRepository:
    """Repositorio para operaciones de base de datos de habito"""

    def __init__(self, db: Session):
        self.db = db

    def crear_habito(self, habito: Habitos) -> Habitos:
        """Crear habito en BD"""
        #habito = Habitos(**habito_data)
        self.db.add(habito)
        self.db.commit()
        self.db.refresh(habito)
        return habito