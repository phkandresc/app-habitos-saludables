# db/Connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from dotenv import load_dotenv
import os
import logging
from typing import Optional

import importlib
import pkgutil
import model

from model.Base import Base

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.import_all_models()
        if self._engine is None:
            self._initialize_connection()

    def import_all_models(self):
        package = model
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            if module_name not in ("Base", "__init__"):
                importlib.import_module(f"model.{module_name}")

    def _initialize_connection(self):
        """Inicializa la conexión con validación"""
        try:
            # Variables de entorno con validación
            user = os.getenv("user")
            password = os.getenv("password")
            host = os.getenv("host", "localhost")
            port = os.getenv("port", "5432")
            dbname = os.getenv("dbname")

            # Validar parámetros requeridos
            if not all([user, password, dbname]):
                raise ValueError("Missing required database environment variables")

            database_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

            # Engine con configuración optimizada
            self._engine = create_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
                connect_args={"connect_timeout": 30}
            )

            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )

            # Test connection
            self._test_connection()
            logger.info("Database connection initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    def _test_connection(self):
        """Prueba la conexión con timeout"""
        try:
            with self._engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Context manager para sesiones seguras con mejor manejo de errores"""
        if self._session_factory is None:
            raise RuntimeError("Database connection not initialized")

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error in database session: {e}")
            raise
        finally:
            session.close()

    def get_engine(self):
        """Retorna el engine con validación"""
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        return self._engine

    def create_tables(self):
        """Crea todas las tablas definidas en los modelos"""

        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def close(self):
        """Cierra conexiones de manera segura"""
        if self._engine:
            try:
                self._engine.dispose()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self._engine = None
                self._session_factory = None

# Instancia global opcional
db_connection = DatabaseConnection()