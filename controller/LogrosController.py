from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from sqlalchemy.orm import sessionmaker
from db.Connection import DatabaseConnection
from repository.LogroRepository import LogroRepository
from repository.UsuarioRepository import UsuarioRepository
from view.widgets.LogroWidget import LogroWidget

class LogrosController(QObject):
    # Señal para notificar que se cerró la ventana
    ventana_cerrada = pyqtSignal()

    def __init__(self, id_usuario, parent_controller=None):
        super().__init__()
        self.vista = QMainWindow()
        self.id_usuario = id_usuario
        self.parent_controller = parent_controller

        self.db = DatabaseConnection()
        self.Session = sessionmaker(bind=self.db.get_engine())
        self.logro_repository = LogroRepository()
        self.usuario_repository = UsuarioRepository()

        # Inicializar la vista sin mostrarla aún
        self._inicializar_vista()

        # Conectar el evento closeEvent para capturar cierre
        self.vista.closeEvent = self.on_close

    def _inicializar_vista(self):
        """Inicializa la vista con los datos del usuario"""
        try:
            print(f"DEBUG: Inicializando vista de logros para usuario {self.id_usuario}")
            session = self.Session()

            print("DEBUG: Obteniendo usuario...")
            usuario = self.usuario_repository.obtener_usuario_por_id(self.id_usuario)
            print(f"DEBUG: Usuario obtenido: {usuario}")

            print("DEBUG: Obteniendo logros...")
            logros = self.logro_repository.obtener_logros_por_usuario(self.id_usuario)
            print(f"DEBUG: Logros obtenidos: {len(logros) if logros else 0}")

            session.close()

            nombre_usuario = usuario.nombre if usuario else f"Usuario {self.id_usuario}"
            print(f"DEBUG: Creando LogroWidget con nombre: {nombre_usuario}")

            self.ui = LogroWidget(logros, nombre_usuario=nombre_usuario)
            self.vista.setCentralWidget(self.ui)
            self.vista.setWindowTitle(f"Logros de {nombre_usuario}")

            print("DEBUG: Vista inicializada correctamente")
        except Exception as e:
            print(f"ERROR inicializando vista de logros: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_error(f"Error cargando logros: {str(e)}")

    def mostrar(self):
        print(f"DEBUG: Mostrando ventana de logros")
        self.vista.show()
        print(f"DEBUG: Ventana mostrada, visible: {self.vista.isVisible()}")

    def cerrar_vista(self):
        self.vista.close()

    def mostrar_error(self, mensaje: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_exito(self, mensaje: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Éxito")
        msg.setText(mensaje)
        msg.exec()

    def on_close(self, event):
        # Emitir señal para avisar que cerró la ventana
        self.ventana_cerrada.emit()
        event.accept()  # Permitir que se cierre la ventana
