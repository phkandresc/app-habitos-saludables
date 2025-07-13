from PyQt6.QtWidgets import QMainWindow
from view.windows.VentanaHabitos import Ui_ventanaHabitos

class HabitosController:
    def __init__(self):
        self.vista = QMainWindow()
        self.ui = Ui_ventanaHabitos()
        self.ui.setupUi(self.vista)
