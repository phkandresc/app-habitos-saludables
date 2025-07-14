from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow, QApplication, QListWidgetItem

from view.widgets.HabitoWidget import HabitoWidget
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

    def cargarHabitosEnLista(self, habitos_repository, id_usuario):
        # Obtener hábitos del repositorio
        habitos = habitos_repository.obtener_habitos_por_usuario(id_usuario)
        self.ui.listHabitos.clear()
        for habito in habitos:
            item = QListWidgetItem(self.ui.listHabitos)
            widget = HabitoWidget(habito)  # Debes tener un widget personalizado
            item.setSizeHint(widget.sizeHint())
            self.ui.listHabitos.addItem(item)
            self.ui.listHabitos.setItemWidget(item, widget)


    def _on_close(self, event):
        self.ventana_cerrada.emit()
        event.accept()