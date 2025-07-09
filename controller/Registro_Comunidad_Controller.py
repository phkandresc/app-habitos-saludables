from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from view.windows.ventana_nueva_comunidad import Ui_Form


class nueva_comunidad:
    def __init__(self):
        self.vista = QMainWindow()
        self.ui = Ui_Form()
        self.ui.setupUi(self.vista)