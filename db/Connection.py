# db/Connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables
load_dotenv()

# Base para los modelos ORM
Base = declarative_base()

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._initialize_connection()

    def _initialize_connection(self):
        """Inicializa la conexión lazy"""
        try:
            # Variables de entorno consistentes
            user = os.getenv("user")
            password = os.getenv("password")
            host = os.getenv("host")
            port = os.getenv("port")
            dbname = os.getenv("dbname")

            database_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

            # Engine con configuración de producción
            self._engine = create_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )

            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )

            # Test connection
            self._test_connection()
            print("Database connection successful!")

        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise

    def _test_connection(self):
        """Prueba la conexión"""
        with self._engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    @contextmanager
    def get_session(self):
        """Context manager para sesiones seguras"""
        if self._session_factory is None:
            raise Exception("Database not initialized")

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def get_engine(self):
        """Retorna el engine"""
        if self._engine is None:
            raise Exception("Database not initialized")
        return self._engine

    def close(self):
        """Cierra conexiones"""
        if self._engine:
            self._engine.dispose()