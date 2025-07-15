# Archivo: tests/test_comunidad_repository.py
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from repository.ComunidadRepository import ComunidadRepository
from model.Comunidad import Comunidad
from model.ComunidadCategoria import ComunidadCategoria


@pytest.fixture
def mock_db_connection():
    """Mock para la conexión a la base de datos"""
    with patch('repository.ComunidadRepository.DatabaseConnection') as mock_db:
        yield mock_db.return_value


@pytest.fixture
def comunidad_repository(mock_db_connection):
    """Instancia del repositorio con la conexión mockeada"""
    return ComunidadRepository()


def test_crear_comunidad_exitoso(comunidad_repository, mock_db_connection):
    """Prueba para crear una comunidad exitosamente"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.add = MagicMock()
    mock_session.flush = MagicMock()
    mock_session.expunge = MagicMock()

    comunidad_data = {'nombre': 'Comunidad Test', 'id_creador': 1}
    comunidad = comunidad_repository.crear_comunidad(comunidad_data)

    assert comunidad is not None
    assert comunidad.nombre == 'Comunidad Test'
    assert comunidad.id_creador == 1
    mock_session.add.assert_called_once()


def test_crear_comunidad_error_sqlalchemy(comunidad_repository, mock_db_connection):
    """Prueba para manejar errores de SQLAlchemy al crear comunidad"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.add.side_effect = SQLAlchemyError()

    comunidad_data = {'nombre': 'Comunidad Test', 'id_creador': 1}
    comunidad = comunidad_repository.crear_comunidad(comunidad_data)

    assert comunidad is None


def test_obtener_comunidad_por_id_exitoso(comunidad_repository, mock_db_connection):
    """Prueba para obtener una comunidad por ID exitosamente"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.first.return_value = Comunidad(
        id_comunidad=1, nombre='Comunidad Test', id_creador=1
    )

    comunidad = comunidad_repository.obtener_comunidad_por_id(1)

    assert comunidad is not None
    assert comunidad.id_comunidad == 1
    assert comunidad.nombre == 'Comunidad Test'


def test_obtener_comunidad_por_id_no_encontrada(comunidad_repository, mock_db_connection):
    """Prueba para manejar comunidad no encontrada por ID"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.first.return_value = None

    comunidad = comunidad_repository.obtener_comunidad_por_id(999)

    assert comunidad is None


def test_agregar_categoria_a_comunidad_exitoso(comunidad_repository, mock_db_connection):
    """Prueba para agregar una categoría a una comunidad exitosamente"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.add = MagicMock()

    resultado = comunidad_repository.agregar_categoria_a_comunidad(1, 2)

    assert resultado is True
    mock_session.add.assert_called_once()


def test_agregar_categoria_a_comunidad_ya_existente(comunidad_repository, mock_db_connection):
    """Prueba para manejar categoría ya existente en comunidad"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.first.return_value = ComunidadCategoria(
        id_comunidad=1, id_categoria=2
    )

    resultado = comunidad_repository.agregar_categoria_a_comunidad(1, 2)

    assert resultado is False


def test_remover_categoria_de_comunidad_exitoso(comunidad_repository, mock_db_connection):
    """Prueba para remover una categoría de una comunidad exitosamente"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.delete.return_value = 1

    resultado = comunidad_repository.remover_categoria_de_comunidad(1, 2)

    assert resultado is True


def test_remover_categoria_de_comunidad_no_encontrada(comunidad_repository, mock_db_connection):
    """Prueba para manejar categoría no encontrada en comunidad"""
    mock_session = mock_db_connection.get_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.delete.return_value = 0

    resultado = comunidad_repository.remover_categoria_de_comunidad(1, 2)

    assert resultado is False