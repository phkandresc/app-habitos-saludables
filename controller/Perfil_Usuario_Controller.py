from PyQt6.QtWidgets import QMessageBox, QMainWindow
from view.windows.ventana_perfil_usuario import Ui_Form

class perfil_usuario:
    def __init__(self, parent_controller=None):
        self.vista = QMainWindow()
        self.ui = Ui_Form()
        self.parent_controller = parent_controller  # Guardamos la referencia
        self.ui.setupUi(self.vista)
        self.conectar_eventos()

    def conectar_eventos(self):
        self.ui.btnRegresar.clicked.connect(self.regresar)

    def regresar(self):
        self.vista.close()
        if self.parent_controller:  # Si tenemos referencia al padre
            self.parent_controller.vista.show()  # Mostramos su vista directamente