from sqlalchemy import create_engine
from model.base import Base

DATABASE_URL = "sqlite:///habitos_saludables.db"  # Ajusta según tu DB

engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.drop_all(engine)  # Solo para desarrollo
    Base.metadata.create_all(engine)
    print("Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_db()