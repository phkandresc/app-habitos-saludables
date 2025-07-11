from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class IncorporaComunidad(Base):
    __tablename__ = 'incorpora_comunidad'