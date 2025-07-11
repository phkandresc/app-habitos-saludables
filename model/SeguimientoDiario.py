from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class SeguimientoDiario(Base):
    __tablename__ = 'seguimiento_diario'