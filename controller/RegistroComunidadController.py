from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from datetime import datetime

from db.Connection import DatabaseConnection
from model.Comunidad import Comunidad
from repository.ComunidadRepository import ComunidadRepository
from view.windows.ventana_nueva_comunidad import Ui_Form


class RegistroComunidadController:
    def __init__(self, parent_controller=None):
        self.vista = QMainWindow()
        self.ui = Ui_Form()
        self.parent_controller = parent_controller
        self.ui.setupUi(self.vista)

        # Inicializar repositorio sin pasar db_session
        self.comunidad_repository = ComunidadRepository()

        self.conectar_eventos()
        self.cargar_categorias()

    def cargar_categorias(self):
        """Cargar categorías disponibles"""
        categorias = [
            "Gimnasio y Fuerza",
            "Mindfulness y Relajación",
            "Cardio y Resistencia",
            "Baile y Movimiento",
            "Deportes al Aire Libre",
            "Pérdida de peso"
        ]
        self.ui.cbxCategorias.clear()
        self.ui.cbxCategorias.addItems(categorias)

    def conectar_eventos(self):
        """Conectar eventos de la interfaz"""
        self.ui.btnCancelar.clicked.connect(self.limpiar_campos)
        self.ui.btnRegresar.clicked.connect(self.regresar)
        self.ui.btnRegistrar.clicked.connect(self.agregar_comunidad)  # ✅ Conectar botón registrar

    def limpiar_campos(self):
        """Limpiar todos los campos del formulario"""
        self.ui.txtNombre.setText("")
        self.ui.lineEdit.setText("")
        self.ui.cbxCategorias.setCurrentIndex(0)

    def regresar(self):
        """Regresar al menú principal"""
        try:
            self.vista.close()
            if self.parent_controller:
                self.parent_controller.mostrar_vista()  # ✅ Usar método mostrar_vista()
        except Exception as e:
            self.mostrar_error(f"Error al regresar: {str(e)}")

    def agregar_comunidad(self):
        """Agregar nueva comunidad"""
        try:
            nombre = self.ui.txtNombre.text().strip()
            creador = self.ui.lineEdit.text().strip()
            categoria_nombre = self.ui.cbxCategorias.currentText()

            # Validaciones
            if not nombre:
                self.mostrar_error("El nombre de la comunidad es obligatorio")
                return

            if not creador:
                self.mostrar_error("El nombre del creador es obligatorio")
                return

            # Preparar datos para el repositorio
            comunidad_data = {
                'nombre': nombre,
                'creador': creador,
                'categoria': categoria_nombre,
                'id_categoria': self.obtener_id_categoria(categoria_nombre),
                'fecha_creacion': datetime.now().date()
            }

            # Crear comunidad usando el repositorio
            nueva_comunidad = self.comunidad_repository.crear_comunidad(comunidad_data)

            if nueva_comunidad:
                self.mostrar_exito("Comunidad registrada exitosamente")
                self.limpiar_campos()
            else:
                self.mostrar_error("Error al registrar la comunidad")

        except Exception as e:
            self.mostrar_error(f"Error al registrar comunidad: {str(e)}")
            print(f"Error en agregar_comunidad: {e}")

    def obtener_id_categoria(self, nombre_categoria: str) -> int:
        """Obtener ID de categoría por nombre"""
        categorias = {
            "Gimnasio y Fuerza": 1,
            "Mindfulness y Relajación": 2,
            "Cardio y Resistencia": 3,
            "Baile y Movimiento": 4,
            "Deportes al Aire Libre": 5,
            "Pérdida de peso": 6
        }
        return categorias.get(nombre_categoria, 1)

    def mostrar_error(self, mensaje: str):
        """Mostrar mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_exito(self, mensaje: str):
        """Mostrar mensaje de éxito"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Éxito")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_vista(self):
        """Mostrar la ventana de registro de comunidad"""
        self.vista.show()

    def cerrar_vista(self):
        """Cerrar la ventana de registro de comunidad"""
        self.vista.close()


# Función factory para mantener compatibilidad
def nueva_comunidad(parent_controller=None):
    return RegistroComunidadController(parent_controller)