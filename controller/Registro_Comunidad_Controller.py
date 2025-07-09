from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow

from db.connection import get_db_session
from model.Comunidad import Comunidad
from repository.ComunidadRepository import ComunidadRepository
from view.windows.ventana_nueva_comunidad import Ui_Form


class nueva_comunidad:
    def __init__(self, parent_controller=None):
        self.vista = QMainWindow()
        self.ui = Ui_Form()
        self.parent_controller = parent_controller  # Guardamos la referencia
        self.ui.setupUi(self.vista)
        self.db_session = get_db_session()
        self.comunidad_repository = ComunidadRepository(self.db_session)
        self.conectar_eventos()
        self.cargar_categorias()

    def cargar_categorias(self):
        categorias = ["Gimnasio y Fuerza","Mindfulness y Relajación", "Cardio y Resistencia", "Baile y Movimiento", "Deportes al Aire Libre","Pérdida de peso"]
        self.ui.cbxCategorias.addItems(categorias)

    def conectar_eventos(self):
        self.ui.btnCancelar.clicked.connect(self.limpiar_campos)
        self.ui.btnRegresar.clicked.connect(self.regresar)

    def limpiar_campos(self):
        self.ui.txtNombre.setText("")
        self.ui.lineEdit.setText("")

        # Opcional: Reiniciar la categoría al primer ítem
        self.ui.cbxCategorias.setCurrentIndex(0)

    def regresar(self):
        self.vista.close()
        if self.parent_controller:  # Si tenemos referencia al padre
            self.parent_controller.vista.show()  # Mostramos su vista directamente

    def agregar_comunidad(self):
        print("comunidad")
        nombre = self.ui.txtNombre.text()
        creador = self.ui.lineEdit.text()
        categoriasN = self.ui.cbxCategorias.currentText()

        try:
            # Validar campos vacíos
            if not nombre or not creador:
                self.mostrar_error("Todos los campos son obligatorios")
                return

            # Crear una nueva instancia de Comunidad
            nuevo_comunidad = Comunidad(
                nombre=nombre,
                creador=creador,
                categorias = self.obtener_id_categoria(categoriasN)
            )
            # Guardar en la base de datos
            self.comunidad_repository.crear_comuniadad(nuevo_comunidad)
            QMessageBox.information(self.vista, "Éxito", "Comunidad registrada exitosamente.")
            self.limpiar_campos()

        except Exception as e:
            self.mostrar_error(f"Error al registrar comunidad: {str(e)}")

    def obtener_id_categoria(self, nombre_categoria):
        # Mapeo simple - deberías obtener esto de la base de datos realmente
        categorias = {
            "Gimnasio y Fuerza":1,
            "Mindfulness y Relajación":2,
            "Cardio y Resistencia":3,
            "Baile y Movimiento":4,
            "Deportes al Aire Libre":5,
            "Pérdida de peso":6
        }
        return categorias.get(nombre_categoria, 1)

    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()