from .Base import Base
from sqlalchemy import (Column, Integer, String, Date,ForeignKey)

class Comunidad(Base):
    __tablename__ = 'comunidad'

    id_comunidad = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    creador = Column(String, nullable=False)
    categorias = Column(String, nullable=False)

