from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Recompensa(Base):
    __tablename__ = 'recompensa'