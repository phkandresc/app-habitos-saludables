
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from controller.Registro_Habitos_Controler import registro_habitos
from controller.Registro_Comunidad_Controller import nueva_comunidad
from model import Usuario
from view.windows.ventana_Menu_Principal import Ui_MainWindow
from controller.Perfil_Usuario_Controller import perfil_usuario
class menu_principal_Controller:
    def __init__(self, usuario_autenticado: Usuario):
        print("Ususario que acaba de ingresar: ",usuario_autenticado.nombre)
        self.usuario_autenticado = usuario_autenticado
        self.vista = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.vista)
        self.conectar_eventos()

    def conectar_eventos(self):
        self.ui.actionCerrar_Sesion.triggered.connect(self.cerrar_aplicacion)
        self.ui.action_Icono_Cerrar_Sesion.triggered.connect(self.cerrar_aplicacion)
        self.ui.action_Icono_Comunidad.triggered.connect(self.comunidad)
        self.ui.action_Icono_Perfil_Usuario.triggered.connect(self.perfil_Usuario)

        self.ui.pushButton.clicked.connect(self.nuevo_habito)

    def cerrar_aplicacion(self):
        self.vista.close()
        #LoginController.cerrar_sesion()

    def nuevo_habito(self):
        self.vista.close()
        self.habitos_controller = registro_habitos(self)
        self.habitos_controller.vista.show()

    def comunidad(self):
        self.vista.close()
        self.ingresar_comunidad = nueva_comunidad(self)
        self.ingresar_comunidad.vista.show()

    def perfil_Usuario(self): # Para igresar a la ventana perfil usuario
        self.vista.hide()  # Oculta la ventana en lugar de cerrarla
        self.perfil_usuarios = perfil_usuario(self)
        self.perfil_usuarios.vista.show()
