from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow, QApplication
from view.windows.VentanaHabitos import Ui_ventanaHabitos

class HabitosController(QObject):
    # Señal que se emite cuando la ventana se cierra
    ventana_cerrada = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.vista = QMainWindow()
        self.ui = Ui_ventanaHabitos()
        self.ui.setupUi(self.vista)
        self.conectar_eventos()

    def conectar_eventos(self):
        # closeEvent se conecta a un metodo personalizado para manejar el cierre de la ventana
        self.vista.closeEvent = self._on_close

    def _on_close(self, event):
        self.ventana_cerrada.emit()
        event.accept()