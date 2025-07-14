from typing import Optional
from PyQt6 import QtWidgets
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QMessageBox, QMainWindow
import re

from repository.UsuarioRepository import UsuarioRepository
from repository.PerfilUsuarioRepository import PerfilUsuarioRepository
from view.windows.VentanaRegistro import Ui_ventanaRegistrarse


class UsuarioRegisterController:
    def __init__(self):
        self.usuario_repository = UsuarioRepository()
        self.perfil_repository = PerfilUsuarioRepository()
        # Referencia al controlador de login
        self.login_controller = None

        # Configuración de la ventana principal
        self.vista = QMainWindow()
        self.ui = Ui_ventanaRegistrarse()
        self.ui.setupUi(self.vista)

        # Configuración inicial
        self._configurar_ventana()
        self.conectar_eventos()

    def _configurar_ventana(self):
        # Centrar la ventana en la pantalla
        self.vista.setFixedSize(self.vista.size())


    def conectar_eventos(self):
        """Conecta los eventos de la interfaz con sus métodos"""
        self.ui.btnRegistrarse.clicked.connect(self.registrar_usuario)
        self.ui.btnVolverIniciarSesion.clicked.connect(self.volver_login)
        self.ui.cbxMostrarPassword.toggled.connect(self.toggle_password_visibility)
        self.ui.txtOcupacion.returnPressed.connect(self.registrar_usuario)

    def toggle_password_visibility(self, checked: bool):
        """Alterna la visibilidad de las contraseñas"""
        echo_mode = (QtWidgets.QLineEdit.EchoMode.Normal if checked
                     else QtWidgets.QLineEdit.EchoMode.Password)
        self.ui.txtPassword.setEchoMode(echo_mode)
        self.ui.txtConfirmarPassword.setEchoMode(echo_mode)

    def registrar_usuario(self) -> bool:
        """Maneja el proceso de registro de usuario"""
        try:
            # Obtener datos del formulario
            datos_usuario = self._obtener_datos_formulario()

            # Validar datos
            if not self._validar_datos_usuario(datos_usuario):
                return False

            # Verificar unicidad
            if not self._verificar_unicidad(datos_usuario):
                return False

            # Crear usuario y perfil
            return self._crear_usuario_y_perfil(datos_usuario)

        except ValueError as ve:
            self.mostrar_error(f"Error en los datos ingresados: {str(ve)}")
            return False
        except Exception as e:
            self.mostrar_error(f"Error al registrar usuario: {str(e)}")
            print(f"Error en registrar_usuario: {e}")
            return False

    def _obtener_datos_formulario(self) -> dict:
        """Obtiene y procesa los datos del formulario"""
        sexo = self.ui.cmbSexo.currentText()
        sexo_db = 'M' if sexo.lower().startswith('h') else 'F'

        return {
            'nombre': self.ui.txtNombre.text().strip(),
            'apellido': self.ui.txtApellido.text().strip(),
            'nombre_usuario': self.ui.txtNombreUsuario.text().strip(),
            'correo_electronico': self.ui.txtCorreo.text().strip(),
            'contrasenia': self.ui.txtPassword.text().strip(),
            'confirmar_password': self.ui.txtConfirmarPassword.text().strip(),
            'sexo': sexo_db,
            'fecha_nacimiento': self.ui.dateNacimiento.date().toPyDate(),
            'peso': float(self.ui.dsbPeso.value()),
            'altura': float(self.ui.dsbAltura.value()),
            'ocupacion': self.ui.txtOcupacion.text().strip()
        }

    def _validar_datos_usuario(self, datos: dict) -> bool:
        """Valida todos los datos del usuario"""
        # Validar campos obligatorios
        campos_requeridos = ['nombre', 'apellido', 'nombre_usuario', 'correo_electronico',
                             'contrasenia', 'confirmar_password', 'ocupacion']

        for campo in campos_requeridos:
            if not datos[campo]:
                self.mostrar_error("Todos los campos son obligatorios")
                return False

        # Validar coincidencia de contraseñas
        if datos['contrasenia'] != datos['confirmar_password']:
            self.mostrar_error("Las contraseñas no coinciden")
            self._limpiar_passwords()
            return False

        # Validar formato de correo
        if not self._validar_email(datos['correo_electronico']):
            self.mostrar_error("El formato del correo electrónico no es válido")
            return False

        # Validar peso y altura
        if datos['peso'] <= 0 or datos['altura'] <= 0:
            self.mostrar_error("Peso y altura deben ser mayores a 0")
            return False

        # Validar longitud de contraseña
        if len(datos['contrasenia']) < 6:
            self.mostrar_error("La contraseña debe tener al menos 6 caracteres")
            return False

        # Validar longitud de nombre de usuario
        if len(datos['nombre_usuario']) < 3:
            self.mostrar_error("El nombre de usuario debe tener al menos 3 caracteres")
            return False

        return True

    def _validar_email(self, email: str) -> bool:
        """Valida el formato del correo electrónico"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None

    def _verificar_unicidad(self, datos: dict) -> bool:
        """Verifica que el nombre de usuario y correo sean únicos"""
        if self.usuario_repository.usuario_existe(nombre_usuario=datos['nombre_usuario']):
            self.mostrar_error("El nombre de usuario ya está en uso")
            return False

        if self.usuario_repository.usuario_existe(correo_electronico=datos['correo_electronico']):
            self.mostrar_error("El correo electrónico ya está en uso")
            return False

        return True

    def _crear_usuario_y_perfil(self, datos: dict) -> bool:
        """Crea el usuario y su perfil asociado"""
        usuario_data = {
            'nombre': datos['nombre'],
            'apellido': datos['apellido'],
            'correo_electronico': datos['correo_electronico'],
            'contrasenia': datos['contrasenia'],
            'fecha_nacimiento': datos['fecha_nacimiento'],
            'sexo': datos['sexo'],
            'nombre_usuario': datos['nombre_usuario']
        }

        nuevo_usuario = self.usuario_repository.crear_usuario(usuario_data)

        if nuevo_usuario:
            perfil_data = {
                'id_usuario': nuevo_usuario.id_usuario,
                'peso': datos['peso'],
                'altura': datos['altura'],
                'ocupacion': datos['ocupacion']
            }

            nuevo_perfil = self.perfil_repository.crear_perfil(perfil_data)

            if nuevo_perfil:
                self.mostrar_exito("Usuario registrado exitosamente")
                self.limpiar_campos()
                return True
            else:
                # Rollback: eliminar usuario si falla la creación del perfil
                self.usuario_repository.eliminar_usuario(nuevo_usuario.id_usuario)
                self.mostrar_error("Error al crear perfil de usuario")
                return False
        else:
            self.mostrar_error("Error al registrar usuario en la base de datos")
            return False

    def volver_login(self):
        """Vuelve a la ventana de login"""
        try:
            # Importación dinámica para evitar dependencias circulares
            from controller.LoginController import LoginController

            self.vista.close()
            self.login_controller = LoginController()
            self.login_controller.vista.show()
        except Exception as e:
            self.mostrar_error(f"Error al volver al login: {str(e)}")
            print(f"Error en volver_login: {e}")

    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        msg = QMessageBox(self.vista)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_exito(self, mensaje: str):
        """Muestra mensaje de éxito"""
        msg = QMessageBox(self.vista)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Éxito")
        msg.setText(mensaje)
        msg.exec()

    def limpiar_campos(self):
        """Limpia todos los campos del formulario"""
        self.ui.txtNombre.clear()
        self.ui.txtApellido.clear()
        self.ui.txtNombreUsuario.clear()
        self.ui.txtCorreo.clear()
        self.ui.txtPassword.clear()
        self.ui.txtConfirmarPassword.clear()
        self.ui.cbxMostrarPassword.setChecked(False)
        self.ui.cmbSexo.setCurrentIndex(0)
        self.ui.dateNacimiento.setDate(QDate.currentDate().addYears(-18))
        self.ui.dsbPeso.setValue(0.0)
        self.ui.dsbAltura.setValue(0.0)
        self.ui.txtOcupacion.clear()

    def _limpiar_passwords(self):
        """Limpia solo los campos de contraseña"""
        self.ui.txtPassword.clear()
        self.ui.txtConfirmarPassword.clear()
        self.ui.cbxMostrarPassword.setChecked(False)

    def mostrar_vista(self):
        """Muestra la ventana de registro"""
        self.limpiar_campos()
        self.vista.show()

    def cerrar_vista(self):
        """Cierra la ventana de registro"""
        self.vista.close()