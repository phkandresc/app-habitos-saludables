from sqlalchemy.orm import Session
from model.Comunidad import Comunidad


class ComunidadRepository:
    """Repositorio para operaciones de base de datos de comuniadad"""

    def __init__(self, db: Session):
        self.db = db

    def crear_comuniadad(self, comuniadad_data: dict) -> Comunidad:
        """Crear comuniadad en BD"""
        comuniadad = Comunidad(**comuniadad_data)
        self.db.add(comuniadad)
        self.db.commit()
        self.db.refresh(comuniadad)
        return comuniadad