from sqlalchemy import Column, Integer, ForeignKey
from model.Base import Base

class Desbloquea(Base):
    __tablename__ = 'desbloquea'

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    id_logro = Column(Integer, ForeignKey('logros.id_logro'), primary_key=True)

    def __repr__(self):
        return f"<Desbloquea(id_usuario={self.id_usuario}, id_logro={self.id_logro})>"
