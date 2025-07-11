from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class AsignacionNivel(Base):
    __tablename__ = 'asignacion_nivel'