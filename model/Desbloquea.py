
from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Desbloquea(Base):
    __tablename__ = 'desbloquea'