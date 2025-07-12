from typing import Optional
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow

from model.Usuario import Usuario
from repository.UsuarioRepository import UsuarioRepository
from view.windows.LoginView import Ui_Login


class LoginController:
    def __init__(self):
        self.usuario_repository = UsuarioRepository()
        # Referencias a otros controladores
        self.menu_controller = None
        self.registro_controller = None
        # Usuario actualmente autenticado
        self.usuario_actual = None

        # Configuración de la ventana principal
        self.vista = QMainWindow()
        self.ui = Ui_Login()
        self.ui.setupUi(self.vista)

        # Configuración inicial
        self._configurar_ventana()
        self.conectar_eventos()

    def _configurar_ventana(self):
        """Configuración inicial de la ventana"""
        self.vista.setWindowTitle("Iniciar Sesión")
        # Centrar la ventana en la pantalla
        self.vista.setFixedSize(self.vista.size())

    def conectar_eventos(self):
        """Conecta los eventos de la interfaz con sus métodos"""
        self.ui.btnIniciarSesion.clicked.connect(self.iniciar_sesion)
        self.ui.cbxMostrarPassword.toggled.connect(self.toggle_password_echo_mode)
        self.ui.txtPassword.returnPressed.connect(self.iniciar_sesion)
        self.ui.btnRegistrarse.clicked.connect(self.abrir_registro)

    def toggle_password_echo_mode(self, checked: bool):
        """Alterna la visibilidad de la contraseña"""
        echo_mode = (QtWidgets.QLineEdit.EchoMode.Normal if checked
                     else QtWidgets.QLineEdit.EchoMode.Password)
        self.ui.txtPassword.setEchoMode(echo_mode)

    def iniciar_sesion(self) -> Optional[Usuario]:
        """Maneja el proceso de inicio de sesión"""
        nombre_usuario = self.ui.txtNombreUsuario.text().strip()
        contrasenia = self.ui.txtPassword.text().strip()

        try:
            # Validar entrada
            if not self._validar_campos(nombre_usuario, contrasenia):
                return None

            # Autenticar usuario
            usuario = self.usuario_repository.autenticar_usuario(nombre_usuario, contrasenia)

            if usuario:
                self.usuario_actual = usuario
                print(f"Usuario {usuario.nombre} ha iniciado sesión correctamente")
                self._abrir_menu_principal()
                return usuario
            else:
                self.mostrar_error("Usuario o contraseña incorrectos")
                self._limpiar_password()
                return None

        except Exception as e:
            self.mostrar_error(f"Error al iniciar sesión: {str(e)}")
            print(f"Error en iniciar_sesion: {e}")
            return None

    def _validar_campos(self, nombre_usuario: str, contrasenia: str) -> bool:
        """Valida que los campos no estén vacíos"""
        if not nombre_usuario or not contrasenia:
            self.mostrar_error("Todos los campos son obligatorios")
            return False
        return True

    def _abrir_menu_principal(self):
        """Abre el menú principal y cierra la ventana de login"""
        try:
            # Importación dinámica para evitar dependencias circulares
            from controller.MenuPrincipalController import MenuPrincipalController

            self.vista.close()
            self.menu_controller = MenuPrincipalController()
            self.menu_controller.vista.show()
        except Exception as e:
            self.mostrar_error(f"Error al abrir menú principal: {str(e)}")
            print(f"Error en _abrir_menu_principal: {e}")

    def abrir_registro(self):
        """Abre la ventana de registro"""
        try:
            # Importación dinámica para evitar dependencias circulares
            from controller.UsuarioRegisterController import UsuarioRegisterController

            self.vista.close()
            self.registro_controller = UsuarioRegisterController()
            self.registro_controller.vista.show()
        except Exception as e:
            self.mostrar_error(f"Error al abrir registro: {str(e)}")
            print(f"Error en abrir_registro: {e}")

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
        """Limpia todos los campos de entrada"""
        self.ui.txtNombreUsuario.clear()
        self.ui.txtPassword.clear()
        self.ui.cbxMostrarPassword.setChecked(False)

    def _limpiar_password(self):
        """Limpia solo el campo de contraseña"""
        self.ui.txtPassword.clear()
        self.ui.cbxMostrarPassword.setChecked(False)

    def mostrar_vista(self):
        """Muestra la ventana de login"""
        self.limpiar_campos()
        self.vista.show()

    def cerrar_vista(self):
        """Cierra la ventana de login"""
        self.vista.close()

    def get_usuario_actual(self) -> Optional[Usuario]:
        """Retorna el usuario actualmente autenticado"""
        return self.usuario_actual

    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        self.usuario_actual = None
        self.limpiar_campos()