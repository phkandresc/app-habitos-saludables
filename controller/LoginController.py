# controller/LoginController.py
from typing import Optional

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow

from model.Usuario import Usuario
from model.Perfil_Usuario import Perfil_Usuario
from repository.UsuarioRepository import UsuarioRepository
from view.windows.LoginView import Ui_Login
#from db.connection import get_db_session
from controller.menu_principal_Controller import menu_principal_Controller
from controller.Usuario_Register_Controller import UsuarioRegisterController
from db.connection  import DatabaseConnection

class LoginController:
    def __init__(self):
        self.db = DatabaseConnection()
        self.usuario_repository = None  # Se inicializa luego con sesión
        # Controlador de registro (se inicializa al abrir la ventana de registro)
        self.register_controller = None
        # Ventana principal de login
        self.vista = QMainWindow()
        # Interfaz gráfica de login
        self.ui = Ui_Login()
        self.ui.setupUi(self.vista)
        # Conecta los eventos de la interfaz con sus métodos
        self.conectar_eventos()

    def conectar_eventos(self):
        # Conecta el botón de iniciar sesión con su función
        self.ui.btnIniciarSesion.clicked.connect(self.iniciar_sesion)
        # Conecta el checkbox de mostrar contraseña con su función
        self.ui.cbxMostrarPassword.toggled.connect(self.toggle_password_echo_mode)
        # Accion al presionar la tecla Enter en el campo de contraseña
        self.ui.txtPassword.returnPressed.connect(self.iniciar_sesion)
        self.ui.btnRegistrarse.clicked.connect(self.registrarse)


    def toggle_password_echo_mode(self, checked):
        # Alterna la visibilidad de la contraseña
        if checked:
            self.ui.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        else:
            self.ui.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    def iniciar_sesion(self) -> Optional[Usuario]:
        """Maneja el proceso de inicio de sesión"""

        # Obtiene los datos ingresados por el usuario
        nombre_usuario = self.ui.txtNombreUsuario.text().strip()
        contrasenia = self.ui.txtPassword.text().strip()
        try:
            # Validar campos vacíos
            if not nombre_usuario or not contrasenia:
                self.mostrar_error("Todos los campos son obligatorios")
                return None

            # Autenticar usuario
            with self.db.get_session() as session:
                self.usuario_repository = UsuarioRepository(session)
                usuario = self.usuario_repository.autenticar_usuario(nombre_usuario, contrasenia)

                if usuario:
                    print(f"Usuario autenticado: {usuario.nombre}")
                    print(f"Perfil cargado: {'Sí' if usuario.perfil else 'No'}")
                    self.vista.close()
                    self.menu_controller = menu_principal_Controller(usuario)
                    self.menu_controller.vista.show()
                    return usuario
                else:
                    self.mostrar_error("Usuario o contraseña incorrectos")
                    return None

        except Exception as e:
            self.mostrar_error(f"Error al iniciar sesión: {str(e)}")
            print(e)
            return None

    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def cerrar_sesion(self):
        """Cierra la sesión de la base de datos"""
        if self.db_session:
            self.db_session.close()

    def registrarse(self):
        self.vista.close()
        self.registro_usuario = UsuarioRegisterController(self)
        self.registro_usuario.vista.show()
