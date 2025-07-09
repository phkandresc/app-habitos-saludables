
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from controller.Registro_Habitos_Controler import registro_habitos
from controller.Registro_Comunidad_Controller import nueva_comunidad
from view.windows.ventana_Menu_Principal import Ui_MainWindow

class menu_principal_Controller:
    def __init__(self):
        self.vista = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.vista)
        self.conectar_eventos()

    def conectar_eventos(self):
        self.ui.actionCerrar_Sesion.triggered.connect(self.cerrar_aplicacion)
        self.ui.action_Icono_Cerrar_Sesion.triggered.connect(self.cerrar_aplicacion)
        self.ui.action_Icono_Comunidad.triggered.connect(self.comunidad)

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
