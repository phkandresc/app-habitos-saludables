# repository/HabitosRepository.py
from model.Habito import Habito

class HabitosRepository:
    def __init__(self, session):
        self.session = session

    def crear_habito(self, habito):
        self.session.add(habito)
        self.session.commit()
        return habito

    def obtener_habito_por_id(self, id_habito):
        return self.session.query(Habito).filter_by(id_habito=id_habito).first()

    def obtener_habitos_por_usuario(self, id_usuario):
        return self.session.query(Habito).filter_by(id_usuario=id_usuario).all()

    def actualizar_habito(self, id_habito, **kwargs):
        habito = self.obtener_habito_por_id(id_habito)
        if habito:
            for key, value in kwargs.items():
                setattr(habito, key, value)
            self.session.commit()
        return habito

    def eliminar_habito(self, id_habito):
        habito = self.obtener_habito_por_id(id_habito)
        if habito:
            self.session.delete(habito)
            self.session.commit()
        return habito