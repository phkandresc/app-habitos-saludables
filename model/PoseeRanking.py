from sqlalchemy import (Column, Integer, String, Date, ForeignKey)
from sqlalchemy.orm import relationship
from .base import Base

class PoseeRanking(Base):
    __tablename__ = 'posee_ranking'