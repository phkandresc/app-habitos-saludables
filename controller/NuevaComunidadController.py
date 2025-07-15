from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from typing import List
import logging

from repository.ComunidadRepository import ComunidadRepository
from repository.CategoriaRepository import CategoriasRepository
from repository.ComunidadCategoriaRepository import ComunidadCategoriaRepository
from view.windows.VentanaNuevaComunidad import Ui_ventanaNuevaComunidad

# Configurar logging
logger = logging.getLogger(__name__)

class NuevaComunidadController(QObject):
    """Controlador para la creación de nuevas comunidades"""

    comunidad_creada = pyqtSignal(int)  # Señal con ID de la comunidad creada
    ventana_cerrada = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self, id_usuario: int):
        super().__init__()

        if not self._validar_id_usuario(id_usuario):
            raise ValueError("ID de usuario inválido")

        self.id_usuario = id_usuario

        # Inicialización de vista
        self.vista = QMainWindow()
        self.ui = Ui_ventanaNuevaComunidad()
        self.ui.setupUi(self.vista)

        # Inicialización de repositorios
        self.comunidad_repository = ComunidadRepository()
        self.categorias_repository = CategoriasRepository()
        self.comunidad_categoria_repository = ComunidadCategoriaRepository()

        self._setup_controller()

    def _validar_id_usuario(self, id_usuario: int) -> bool:
        """Validar que el ID de usuario sea válido"""
        return isinstance(id_usuario, int) and id_usuario > 0

    def _setup_controller(self):
        """Configuración inicial del controlador"""
        try:
            self._conectar_eventos()
            self._cargar_categorias()
            logger.info(f"Controlador de nueva comunidad inicializado para usuario {self.id_usuario}")
        except Exception as e:
            logger.error(f"Error inicializando controlador: {e}")
            self.error_ocurrido.emit(f"Error al inicializar: {e}")

    def _conectar_eventos(self):
        """Conectar eventos de la vista"""
        self.vista.closeEvent = self._on_close

        # Conectar botones
        self.ui.btnCrearComunidad.clicked.connect(self.crear_comunidad)
        self.ui.btnCancelar.clicked.connect(self.cerrar_ventana)

    def _cargar_categorias(self):
        """Cargar categorías disponibles en el combo box"""
        try:
            categorias = self.categorias_repository.obtener_todas_categorias()

            # Limpiar el combo box actual
            self.ui.cmbCategoria.clear()

            # Agregar categorías dinámicamente
            for categoria in categorias:
                self.ui.cmbCategoria.addItem(categoria.nombre, categoria.id_categoria)

            logger.info(f"Cargadas {len(categorias)} categorías")
        except Exception as e:
            logger.error(f"Error cargando categorías: {e}")
            # Mantener las categorías por defecto si hay error
            pass

    def crear_comunidad(self):
        """Crear una nueva comunidad con los datos del formulario"""
        try:
            # Validar datos del formulario
            if not self._validar_formulario():
                return

            nombre = self.ui.txtNombre.text().strip()

            # Crear la comunidad solo con los campos que existen en el modelo
            comunidad_data = {
                'nombre': nombre,
                'id_creador': self.id_usuario
            }

            comunidad = self.comunidad_repository.crear_comunidad(comunidad_data)

            if comunidad:
                # Si se seleccionó una categoría, asociarla a la comunidad
                categoria_id = self.ui.cmbCategoria.currentData()
                if categoria_id is None:
                    categoria_id = self.ui.cmbCategoria.currentIndex() + 1

                # Crear la relación ComunidadCategoria
                self._asociar_categoria_a_comunidad(comunidad.id_comunidad, categoria_id)

                QMessageBox.information(
                    self.vista,
                    "Éxito",
                    f"Comunidad '{nombre}' creada exitosamente"
                )

                # Emitir señal y cerrar ventana
                self.comunidad_creada.emit(comunidad.id_comunidad)
                self.cerrar_ventana()

                logger.info(f"Comunidad creada exitosamente: ID {comunidad.id_comunidad}")
            else:
                self._mostrar_error("No se pudo crear la comunidad")

        except Exception as e:
            logger.error(f"Error creando comunidad: {e}")
            self._mostrar_error(f"Error al crear comunidad: {e}")

    def _asociar_categoria_a_comunidad(self, id_comunidad: int, id_categoria: int):
        """Asociar una categoría a la comunidad creada"""
        try:
            if not id_categoria or id_categoria <= 0:
                logger.warning("ID de categoría inválido, no se creará relación")
                return

            relacion = self.comunidad_categoria_repository.crear_relacion(id_comunidad, id_categoria)

            if relacion:
                logger.info(f"Categoría {id_categoria} asociada exitosamente a comunidad {id_comunidad}")
            else:
                logger.warning(f"No se pudo asociar categoría {id_categoria} a comunidad {id_comunidad}")

        except Exception as e:
            logger.error(f"Error asociando categoría a comunidad: {e}")
            # No mostramos error al usuario ya que la comunidad se creó exitosamente
            # Solo es un problema menor con la categoría

    def _validar_formulario(self) -> bool:
        """Validar que los datos del formulario sean correctos"""
        nombre = self.ui.txtNombre.text().strip()

        if not nombre:
            self._mostrar_error("El nombre de la comunidad es obligatorio")
            self.ui.txtNombre.setFocus()
            return False

        if len(nombre) < 3:
            self._mostrar_error("El nombre debe tener al menos 3 caracteres")
            self.ui.txtNombre.setFocus()
            return False

        if len(nombre) > 100:
            self._mostrar_error("El nombre no puede exceder 100 caracteres")
            self.ui.txtNombre.setFocus()
            return False

        return True

    def _mostrar_error(self, mensaje: str):
        """Mostrar mensaje de error al usuario"""
        QMessageBox.warning(self.vista, "Error", mensaje)
        self.error_ocurrido.emit(mensaje)

    def cerrar_ventana(self):
        """Cerrar la ventana"""
        self.vista.close()

    def mostrar_ventana(self):
        """Mostrar la ventana"""
        self.vista.show()

    def _on_close(self, event):
        """Manejar el evento de cierre de ventana"""
        self.ventana_cerrada.emit()
        event.accept()
