import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
from service.UsuarioService import UsuarioService


class TestUsuarioService(unittest.TestCase):
    """Tests para UsuarioService"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.service = UsuarioService()

        # Mock de los repositorios
        self.service.usuario_repo = Mock()
        self.service.perfil_repo = Mock()

        # Datos de prueba
        self.usuario_mock = Mock()
        self.usuario_mock.id_usuario = 1
        self.usuario_mock.nombre = "Juan Pérez"
        self.usuario_mock.email = "juan@test.com"
        self.usuario_mock.password = "123456"

        self.perfil_mock = Mock()
        self.perfil_mock.id_usuario = 1
        self.perfil_mock.peso = 70.0
        self.perfil_mock.altura = 175.0
        self.perfil_mock.edad = 25
        self.perfil_mock.ocupacion = "Ingeniero"

    def test_crear_usuario_completo_solo_usuario(self):
        """Test crear usuario sin perfil"""
        # Arrange
        usuario_data = {"nombre": "Juan", "email": "juan@test.com", "password": "123456"}
        self.service.usuario_repo.crear_usuario.return_value = self.usuario_mock

        # Act
        resultado = self.service.crear_usuario_completo(usuario_data)

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['usuario'], self.usuario_mock)
        self.assertIsNone(resultado['perfil'])
        self.assertEqual(resultado['mensaje'], 'Usuario creado exitosamente')
        self.service.usuario_repo.crear_usuario.assert_called_once_with(usuario_data)

    def test_crear_usuario_completo_con_perfil(self):
        """Test crear usuario con perfil"""
        # Arrange
        usuario_data = {"nombre": "Juan", "email": "juan@test.com", "password": "123456"}
        perfil_data = {"peso": 70.0, "altura": 175.0, "edad": 25}

        self.service.usuario_repo.crear_usuario.return_value = self.usuario_mock
        self.service.perfil_repo.crear_perfil.return_value = self.perfil_mock

        # Act
        resultado = self.service.crear_usuario_completo(usuario_data, perfil_data)

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['usuario'], self.usuario_mock)
        self.assertEqual(resultado['perfil'], self.perfil_mock)
        self.assertEqual(resultado['mensaje'], 'Usuario y perfil creados exitosamente')

        # Verificar que se agregó id_usuario al perfil_data
        expected_perfil_data = perfil_data.copy()
        expected_perfil_data['id_usuario'] = 1
        self.service.perfil_repo.crear_perfil.assert_called_once_with(expected_perfil_data)

    def test_crear_usuario_completo_fallo_usuario(self):
        """Test fallo al crear usuario"""
        # Arrange
        usuario_data = {"nombre": "Juan", "email": "juan@test.com", "password": "123456"}
        self.service.usuario_repo.crear_usuario.return_value = None

        # Act
        resultado = self.service.crear_usuario_completo(usuario_data)

        # Assert
        self.assertIsNone(resultado)

    def test_obtener_usuario_completo_exitoso(self):
        """Test obtener usuario con perfil"""
        # Arrange
        self.service.usuario_repo.obtener_usuario_por_id.return_value = self.usuario_mock
        self.service.perfil_repo.obtener_perfil_por_usuario.return_value = self.perfil_mock

        # Act
        resultado = self.service.obtener_usuario_completo(1)

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['usuario'], self.usuario_mock)
        self.assertEqual(resultado['perfil'], self.perfil_mock)
        self.assertTrue(resultado['tiene_perfil'])

    def test_obtener_usuario_completo_sin_perfil(self):
        """Test obtener usuario sin perfil"""
        # Arrange
        self.service.usuario_repo.obtener_usuario_por_id.return_value = self.usuario_mock
        self.service.perfil_repo.obtener_perfil_por_usuario.return_value = None

        # Act
        resultado = self.service.obtener_usuario_completo(1)

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['usuario'], self.usuario_mock)
        self.assertIsNone(resultado['perfil'])
        self.assertFalse(resultado['tiene_perfil'])

    def test_obtener_usuario_completo_usuario_no_existe(self):
        """Test obtener usuario que no existe"""
        # Arrange
        self.service.usuario_repo.obtener_usuario_por_id.return_value = None

        # Act
        resultado = self.service.obtener_usuario_completo(999)

        # Assert
        self.assertIsNone(resultado)

    def test_actualizar_usuario_completo_solo_usuario(self):
        """Test actualizar solo datos de usuario"""
        # Arrange
        usuario_data = {"nombre": "Juan Carlos"}
        self.service.usuario_repo.actualizar_usuario.return_value = self.usuario_mock

        # Act
        resultado = self.service.actualizar_usuario_completo(1, usuario_data=usuario_data)

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['usuario'], self.usuario_mock)
        self.assertIsNone(resultado['perfil'])
        self.assertIn('Usuario actualizado', resultado['mensaje'])

    def test_actualizar_usuario_completo_crear_perfil_nuevo(self):
        """Test crear perfil cuando no existe al actualizar"""
        # Arrange
        perfil_data = {"peso": 75.0, "altura": 180.0}
        self.service.perfil_repo.actualizar_perfil.return_value = None
        self.service.perfil_repo.perfil_existe.return_value = False
        self.service.perfil_repo.crear_perfil.return_value = self.perfil_mock

        # Act
        resultado = self.service.actualizar_usuario_completo(1, perfil_data=perfil_data)

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['perfil'], self.perfil_mock)
        self.assertIn('Perfil creado', resultado['mensaje'])

    def test_eliminar_usuario_completo_con_perfil(self):
        """Test eliminar usuario que tiene perfil"""
        # Arrange
        self.service.perfil_repo.perfil_existe.return_value = True
        self.service.perfil_repo.eliminar_perfil.return_value = True
        self.service.usuario_repo.eliminar_usuario.return_value = True

        # Act
        resultado = self.service.eliminar_usuario_completo(1)

        # Assert
        self.assertTrue(resultado)
        self.service.perfil_repo.eliminar_perfil.assert_called_once_with(1)
        self.service.usuario_repo.eliminar_usuario.assert_called_once_with(1)

    def test_eliminar_usuario_completo_sin_perfil(self):
        """Test eliminar usuario sin perfil"""
        # Arrange
        self.service.perfil_repo.perfil_existe.return_value = False
        self.service.usuario_repo.eliminar_usuario.return_value = True

        # Act
        resultado = self.service.eliminar_usuario_completo(1)

        # Assert
        self.assertTrue(resultado)
        self.service.perfil_repo.eliminar_perfil.assert_not_called()
        self.service.usuario_repo.eliminar_usuario.assert_called_once_with(1)

    def test_validar_credenciales_exitoso(self):
        """Test validación de credenciales correctas"""
        # Arrange
        self.service.usuario_repo.obtener_usuario_por_email.return_value = self.usuario_mock
        self.service.perfil_repo.obtener_perfil_por_usuario.return_value = self.perfil_mock

        # Act
        resultado = self.service.validar_credenciales("juan@test.com", "123456")

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['usuario'], self.usuario_mock)
        self.assertEqual(resultado['perfil'], self.perfil_mock)
        self.assertTrue(resultado['autenticado'])

    def test_validar_credenciales_password_incorrecto(self):
        """Test validación con contraseña incorrecta"""
        # Arrange
        self.service.usuario_repo.obtener_usuario_por_email.return_value = self.usuario_mock

        # Act
        resultado = self.service.validar_credenciales("juan@test.com", "password_malo")

        # Assert
        self.assertIsNone(resultado)

    def test_validar_credenciales_usuario_no_existe(self):
        """Test validación con usuario que no existe"""
        # Arrange
        self.service.usuario_repo.obtener_usuario_por_email.return_value = None

        # Act
        resultado = self.service.validar_credenciales("noexiste@test.com", "123456")

        # Assert
        self.assertIsNone(resultado)

    def test_buscar_usuarios_por_email(self):
        """Test búsqueda por email"""
        # Arrange
        criterios = {"email": "juan@test.com"}
        self.service.usuario_repo.obtener_usuario_por_email.return_value = self.usuario_mock
        self.service.perfil_repo.obtener_perfil_por_usuario.return_value = self.perfil_mock

        # Act
        resultado = self.service.buscar_usuarios_por_criterios(criterios)

        # Assert
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['usuario'], self.usuario_mock)
        self.assertEqual(resultado[0]['perfil'], self.perfil_mock)

    def test_buscar_usuarios_por_nombre(self):
        """Test búsqueda por nombre"""
        # Arrange
        criterios = {"nombre": "Juan"}
        self.service.usuario_repo.buscar_usuarios_por_nombre.return_value = [self.usuario_mock]
        self.service.perfil_repo.obtener_perfil_por_usuario.return_value = self.perfil_mock

        # Act
        resultado = self.service.buscar_usuarios_por_criterios(criterios)

        # Assert
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['usuario'], self.usuario_mock)

    def test_buscar_usuarios_filtro_edad(self):
        """Test búsqueda con filtro de edad"""
        # Arrange
        criterios = {"edad_min": 20, "edad_max": 30}
        self.service.usuario_repo.obtener_todos_usuarios.return_value = [self.usuario_mock]
        self.service.perfil_repo.obtener_perfil_por_usuario.return_value = self.perfil_mock

        # Act
        resultado = self.service.buscar_usuarios_por_criterios(criterios)

        # Assert
        self.assertEqual(len(resultado), 1)  # La edad 25 está en el rango

    def test_obtener_estadisticas_usuarios(self):
        """Test obtener estadísticas"""
        # Arrange
        self.service.usuario_repo.obtener_todos_usuarios.return_value = [self.usuario_mock, self.usuario_mock]
        self.service.perfil_repo.obtener_todos_perfiles.return_value = [self.perfil_mock]
        self.service.perfil_repo.obtener_estadisticas_edad.return_value = {"promedio": 25.0}

        # Act
        resultado = self.service.obtener_estadisticas_usuarios()

        # Assert
        self.assertEqual(resultado['total_usuarios'], 2)
        self.assertEqual(resultado['total_perfiles'], 1)
        self.assertEqual(resultado['usuarios_sin_perfil'], 1)
        self.assertEqual(resultado['porcentaje_con_perfil'], 50.0)

    def test_calcular_imc_usuario_peso_normal(self):
        """Test cálculo de IMC - peso normal"""
        # Arrange
        self.service.perfil_repo.calcular_imc_usuario.return_value = 22.86  # 70kg / (1.75m)²

        # Act
        resultado = self.service.calcular_imc_usuario(1)

        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['imc'], 22.86)
        self.assertEqual(resultado['clasificacion'], "Peso normal")
        self.assertEqual(resultado['id_usuario'], 1)

    def test_calcular_imc_usuario_sobrepeso(self):
        """Test cálculo de IMC - sobrepeso"""
        # Arrange
        self.service.perfil_repo.calcular_imc_usuario.return_value = 26.5

        # Act
        resultado = self.service.calcular_imc_usuario(1)

        # Assert
        self.assertEqual(resultado['clasificacion'], "Sobrepeso")

    def test_calcular_imc_usuario_obesidad(self):
        """Test cálculo de IMC - obesidad"""
        # Arrange
        self.service.perfil_repo.calcular_imc_usuario.return_value = 32.0

        # Act
        resultado = self.service.calcular_imc_usuario(1)

        # Assert
        self.assertEqual(resultado['clasificacion'], "Obesidad")

    def test_calcular_imc_usuario_bajo_peso(self):
        """Test cálculo de IMC - bajo peso"""
        # Arrange
        self.service.perfil_repo.calcular_imc_usuario.return_value = 17.5

        # Act
        resultado = self.service.calcular_imc_usuario(1)

        # Assert
        self.assertEqual(resultado['clasificacion'], "Bajo peso")

    def test_calcular_imc_usuario_sin_datos(self):
        """Test cálculo de IMC sin datos suficientes"""
        # Arrange
        self.service.perfil_repo.calcular_imc_usuario.return_value = None

        # Act
        resultado = self.service.calcular_imc_usuario(1)

        # Assert
        self.assertIsNone(resultado)

    def test_usuarios_activos_por_fecha(self):
        """Test obtener usuarios por fecha"""
        # Arrange
        fecha_desde = date(2024, 1, 1)
        self.service.usuario_repo.obtener_usuarios_por_fecha.return_value = [self.usuario_mock]
        self.service.perfil_repo.obtener_perfil_por_usuario.return_value = self.perfil_mock

        # Act
        resultado = self.service.usuarios_activos_por_fecha(fecha_desde)

        # Assert
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['usuario'], self.usuario_mock)
        self.assertEqual(resultado[0]['perfil'], self.perfil_mock)
        self.service.usuario_repo.obtener_usuarios_por_fecha.assert_called_once_with(fecha_desde)

    def test_manejo_excepciones(self):
        """Test manejo de excepciones"""
        # Arrange
        self.service.usuario_repo.obtener_usuario_por_id.side_effect = Exception("Error de DB")

        # Act
        resultado = self.service.obtener_usuario_completo(1)

        # Assert
        self.assertIsNone(resultado)


if __name__ == '__main__':
    # Ejecutar los tests
    unittest.main(verbosity=2)