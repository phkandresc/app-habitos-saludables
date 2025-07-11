from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class Ranking(Base):
    __tablename__ = 'ranking'