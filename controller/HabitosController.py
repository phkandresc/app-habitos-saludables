import sys

from PyQt6.QtCore import pyqtSignal, QObject, QDate, Qt
from PyQt6.QtWidgets import QMainWindow, QListWidgetItem, QLabel, QMessageBox, QApplication
from datetime import date
from typing import Optional
import logging

from controller.NuevoHabitoController import NuevoHabitoController
from repository.CategoriaRepository import CategoriasRepository
from repository.HabitosRepository import HabitosRepository
from repository.SeguimientoDiarioRepository import SeguimientoDiarioRepository
from view.widgets.HabitoWidget import HabitoWidget
from view.windows.VentanaHabitos import Ui_ventanaHabitos

# Configurar logging
logger = logging.getLogger(__name__)


class HabitosController(QObject):
    """Controlador para la gestión de hábitos con calendario"""

    ventana_cerrada = pyqtSignal()
    habito_actualizado = pyqtSignal(int)  # Señal para notificar actualizaciones
    error_ocurrido = pyqtSignal(str)  # Señal para notificar errores

    def __init__(self, id_usuario: int):
        super().__init__()

        if not self._validar_id_usuario(id_usuario):
            raise ValueError("ID de usuario inválido")

        self.id_usuario = id_usuario
        self.fecha_seleccionada = date.today()

        # Referencias a ventanas secundarias
        self.ventana_nuevo_habito = None

        # Inicialización de vista
        self.vista = QMainWindow()
        self.ui = Ui_ventanaHabitos()
        self.ui.setupUi(self.vista)

        # Inicialización de repositorios
        self.habitos_repository = HabitosRepository()
        self.categorias_repository = CategoriasRepository()
        self.seguimiento_repository = SeguimientoDiarioRepository()

        self._setup_controller()

    def _validar_id_usuario(self, id_usuario: int) -> bool:
        """Validar que el ID de usuario sea válido"""
        return isinstance(id_usuario, int) and id_usuario > 0

    def _setup_controller(self):
        """Configuración inicial del controlador"""
        try:
            self._conectar_eventos()
            self._configurar_calendario()
            self.cargar_habitos_en_lista()
            logger.info(f"Controlador de hábitos inicializado para usuario {self.id_usuario}")
        except Exception as e:
            logger.error(f"Error inicializando controlador: {e}")
            self.error_ocurrido.emit(f"Error al inicializar: {e}")

    def _conectar_eventos(self):
        """Conectar eventos de la vista"""
        self.vista.closeEvent = self._on_close

        # Conectar calendario si existe
        if self._calendario_disponible():
            self.ui.calendarioHabitos.selectionChanged.connect(self._on_fecha_cambiada)
        else:
            logger.warning("Calendario no disponible en la interfaz")

        # Conectar otros botones de la interfaz si existen
        self._conectar_botones_interfaz()

    def _conectar_botones_interfaz(self):
        """Conectar botones adicionales de la interfaz"""
        # Corregir esta línea que tenía un error
        if hasattr(self.ui, 'btnAgregarUnHabito'):
            self.ui.btnAgregarUnHabito.clicked.connect(self.abrir_ventana_agregar_habito)

        if hasattr(self.ui, 'btnRefrescar'):
            self.ui.btnAgregarUnHabito.clicked.connect(self.abrir_ventana_agregar_habito)


    def _configurar_calendario(self):
        """Configurar el calendario con la fecha actual"""
        if self._calendario_disponible():
            try:
                self.ui.calendarioHabitos.setSelectedDate(QDate.currentDate())
            except Exception as e:
                logger.error(f"Error configurando calendario: {e}")

    def _calendario_disponible(self) -> bool:
        """Verificar si el calendario está disponible en la UI"""
        return hasattr(self.ui, 'calendarioHabitos') and self.ui.calendarioHabitos is not None

    def _on_fecha_cambiada(self):
        """Manejar cambio de fecha en el calendario"""
        try:
            if not self._calendario_disponible():
                return

            qdate = self.ui.calendarioHabitos.selectedDate()
            nueva_fecha = date(qdate.year(), qdate.month(), qdate.day())

            if nueva_fecha != self.fecha_seleccionada:
                self.fecha_seleccionada = nueva_fecha
                logger.info(f"Fecha cambiada a: {self.fecha_seleccionada}")
                self.cargar_habitos_en_lista()

        except Exception as e:
            logger.error(f"Error al cambiar fecha: {e}")
            self.error_ocurrido.emit(f"Error al cambiar fecha: {e}")

    def cargar_habitos_en_lista(self):
        """Cargar hábitos del usuario para la fecha seleccionada"""
        self._limpiar_lista()

        try:
            habitos_con_estado = self._obtener_habitos_fecha()

            if not habitos_con_estado:
                self._mostrar_mensaje_sin_habitos()
                return

            self._agregar_habitos_a_lista(habitos_con_estado)
            logger.info(f"Cargados {len(habitos_con_estado)} hábitos para {self.fecha_seleccionada}")

        except Exception as e:
            logger.error(f"Error cargando hábitos: {e}")
            self._mostrar_mensaje_error()
            self.error_ocurrido.emit(f"Error cargando hábitos: {e}")

    def _limpiar_lista(self):
        """Limpiar la lista de hábitos"""
        try:
            self.ui.listHabitos.clear()
        except Exception as e:
            logger.error(f"Error limpiando lista: {e}")

    def _obtener_habitos_fecha(self):
        """Obtener hábitos para la fecha seleccionada"""
        return self.habitos_repository.obtener_habitos_con_estado_por_usuario(
            self.id_usuario, self.fecha_seleccionada
        )

    def _agregar_habitos_a_lista(self, habitos_con_estado):
        """Agregar hábitos a la lista visual"""
        for item in habitos_con_estado:
            try:
                habito = item['habito']
                estado = item['estado']

                habito_widget = self._crear_habito_widget(habito, estado)
                self._agregar_widget_a_lista(habito_widget)

            except Exception as e:
                logger.error(f"Error agregando hábito a lista: {e}")
                continue

    def _crear_habito_widget(self, habito, estado):
        """Crear widget de hábito con conexiones"""
        categoria_nombre = self._obtener_nombre_categoria(habito.id_categoria)
        habito_widget = HabitoWidget(habito, categoria_nombre, estado)

        # Conectar señales del widget
        habito_widget.editarClicked.connect(self._on_editar_habito)
        habito_widget.eliminarClicked.connect(self._on_eliminar_habito)
        habito_widget.estadoClicked.connect(self._on_cambiar_estado_habito)

        return habito_widget

    def _agregar_widget_a_lista(self, widget):
        """Agregar widget a la lista"""
        try:
            list_item = QListWidgetItem()
            list_item.setSizeHint(widget.sizeHint())
            self.ui.listHabitos.addItem(list_item)
            self.ui.listHabitos.setItemWidget(list_item, widget)
        except Exception as e:
            logger.error(f"Error agregando widget a lista: {e}")

    def _mostrar_mensaje_sin_habitos(self):
        """Mostrar mensaje cuando no hay hábitos para el día seleccionado"""
        mensaje = self._crear_mensaje_informativo(
            "No hay hábitos programados para este día 📅"
        )
        self._agregar_widget_a_lista(mensaje)

    def _mostrar_mensaje_error(self):
        """Mostrar mensaje de error"""
        mensaje = self._crear_mensaje_informativo(
            "Error al cargar los hábitos ⚠️",
            color="#e74c3c"
        )
        self._agregar_widget_a_lista(mensaje)

    def _crear_mensaje_informativo(self, texto: str, color: str = "#7f8c8d") -> QLabel:
        """Crear un QLabel con estilo para mensajes informativos"""
        mensaje = QLabel(texto)
        mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mensaje.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14pt;
                font-style: italic;
                padding: 20px;
                background-color: #f8f9fa;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                margin: 10px;
            }}
        """)
        return mensaje

    def _obtener_nombre_categoria(self, id_categoria: Optional[int]) -> str:
        """Obtener nombre de categoría por ID"""
        if not id_categoria:
            return "Sin categoría"

        try:
            categoria = self.categorias_repository.obtener_categoria_por_id(id_categoria)
            return categoria.nombre if categoria else "Sin categoría"
        except Exception as e:
            logger.error(f"Error obteniendo categoría {id_categoria}: {e}")
            return "Sin categoría"

    def _on_cambiar_estado_habito(self, habito_id: int):
        """Manejar cambio de estado de hábito para la fecha seleccionada"""
        try:
            widget = self.sender()
            if not widget:
                logger.warning("No se pudo obtener el widget que envió la señal")
                return

            nuevo_estado = "completado" if widget.estado == "pendiente" else "pendiente"

            # Crear o actualizar seguimiento en BD
            seguimiento_data = {
                'id_usuario': self.id_usuario,
                'id_habito': habito_id,
                'fecha': self.fecha_seleccionada,
                'estado': nuevo_estado
            }

            seguimiento = self.seguimiento_repository.crear_o_actualizar_seguimiento(seguimiento_data)

            if seguimiento:
                # Actualizar widget visual
                self._actualizar_widget_estado(widget, nuevo_estado)
                self.habito_actualizado.emit(habito_id)
                logger.info(
                    f"Estado del hábito {habito_id} cambiado a {nuevo_estado} para fecha {self.fecha_seleccionada}")
            else:
                self._mostrar_error("Error al actualizar estado en la base de datos")

        except Exception as e:
            logger.error(f"Error cambiando estado hábito {habito_id}: {e}")
            self._mostrar_error(f"Error cambiando estado del hábito: {e}")


    def _actualizar_widget_estado(self, widget, nuevo_estado: str):
        """Actualizar el estado visual del widget"""
        try:
            widget.estado = nuevo_estado
            widget.actualizar_estilo_estado()
        except Exception as e:
            logger.error(f"Error actualizando widget: {e}")


    def _on_eliminar_habito(self, habito_id: int):
        """Manejar eliminación de hábito"""
        try:
            respuesta = self._confirmar_eliminacion()
            if respuesta:
                if self.habitos_repository.eliminar_habito(habito_id):
                    self.actualizar_habitos()
                    self._mostrar_informacion("Hábito eliminado exitosamente")
                    logger.info(f"Hábito {habito_id} eliminado exitosamente")
                else:
                    self._mostrar_error("Error al eliminar el hábito")
        except Exception as e:
            logger.error(f"Error eliminando hábito {habito_id}: {e}")
            self._mostrar_error(f"Error eliminando hábito: {e}")

    def _confirmar_eliminacion(self) -> bool:
        """Mostrar diálogo de confirmación para eliminación"""
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar este hábito?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return respuesta == QMessageBox.StandardButton.Yes

    def _mostrar_error(self, mensaje: str):
        """Mostrar mensaje de error al usuario"""
        QMessageBox.critical(self.vista, "Error", mensaje)

    def _mostrar_informacion(self, mensaje: str):
        """Mostrar mensaje de información al usuario"""
        QMessageBox.information(self.vista, "Información", mensaje)

    def _on_close(self, event):
        """Manejar cierre de ventana"""
        logger.info(f"Cerrando ventana de hábitos para usuario {self.id_usuario}")
        self.ventana_cerrada.emit()
        event.accept()

    # Métodos públicos para la interfaz
    def mostrar(self):
        """Mostrar la ventana"""
        try:
            self.vista.show()
            logger.info("Ventana de hábitos mostrada")
        except Exception as e:
            logger.error(f"Error mostrando ventana: {e}")

    def ocultar(self):
        """Ocultar la ventana"""
        try:
            self.vista.hide()
            logger.info("Ventana de hábitos ocultada")
        except Exception as e:
            logger.error(f"Error ocultando ventana: {e}")

    def actualizar_habitos(self):
        """Refrescar la lista de hábitos"""
        logger.info("Actualizando lista de hábitos")
        self.cargar_habitos_en_lista()

    def obtener_fecha_seleccionada(self) -> date:
        """Obtener la fecha actualmente seleccionada"""
        return self.fecha_seleccionada

    def establecer_fecha(self, nueva_fecha: date):
        """Establecer una nueva fecha en el calendario"""
        if not isinstance(nueva_fecha, date):
            logger.error("La fecha debe ser un objeto date válido")
            return

        if self._calendario_disponible():
            try:
                qdate = QDate(nueva_fecha.year, nueva_fecha.month, nueva_fecha.day)
                self.ui.calendarioHabitos.setSelectedDate(qdate)
                logger.info(f"Fecha establecida a: {nueva_fecha}")
            except Exception as e:
                logger.error(f"Error estableciendo fecha: {e}")

    def obtener_estadisticas_periodo(self, fecha_inicio: date, fecha_fin: date) -> dict:
        """Obtener estadísticas de hábitos para un período"""
        try:
            return self.habitos_repository.obtener_estadisticas_usuario(
                self.id_usuario, fecha_inicio, fecha_fin
            )
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def abrir_ventana_agregar_habito(self):
        """Abrir ventana para agregar un nuevo hábito"""
        try:
            logger.info("Abriendo ventana para agregar nuevo hábito")

            # Si ya existe una ventana abierta, la cerramos primero
            if self.ventana_nuevo_habito is not None:
                self.ventana_nuevo_habito.ocultar()
                self.ventana_nuevo_habito = None

            # Crear nueva instancia del controlador en modo creación
            self.ventana_nuevo_habito = NuevoHabitoController(self.id_usuario)

            # Conectar señales para actualizar la lista cuando se agregue un hábito
            self.ventana_nuevo_habito.habito_agregado.connect(self._on_habito_agregado)
            self.ventana_nuevo_habito.ventana_cerrada.connect(self._on_ventana_nuevo_habito_cerrada)

            # Mostrar la ventana
            self.ventana_nuevo_habito.mostrar()

        except Exception as e:
            logger.error(f"Error abriendo ventana de nuevo hábito: {e}")
            self._mostrar_error(f"Error al abrir ventana de nuevo hábito: {e}")

    def _on_habito_agregado(self, habito_id: int):
        """Manejar cuando se agrega un nuevo hábito"""
        try:
            logger.info(f"Nuevo hábito agregado con ID: {habito_id}")

            # Actualizar la lista de hábitos
            self.actualizar_habitos()

            # Emitir señal de actualización
            self.habito_actualizado.emit(habito_id)

            # Mostrar mensaje de confirmación
            self._mostrar_informacion("Hábito agregado exitosamente")

        except Exception as e:
            logger.error(f"Error procesando hábito agregado {habito_id}: {e}")

    def _on_ventana_nuevo_habito_cerrada(self):
        """Manejar cuando se cierra la ventana de nuevo hábito"""
        logger.info("Ventana de nuevo hábito cerrada")
        self.ventana_nuevo_habito = None

    def _on_editar_habito(self, habito_id: int):
        """Manejar edición de hábito"""
        try:
            logger.info(f"Iniciando edición para hábito {habito_id}")

            # Si ya existe una ventana abierta, la cerramos primero
            if self.ventana_nuevo_habito is not None:
                self.ventana_nuevo_habito.ocultar()
                self.ventana_nuevo_habito = None

            # Crear instancia del controlador en modo edición
            self.ventana_nuevo_habito = NuevoHabitoController(self.id_usuario, habito_id)

            # Conectar señales
            self.ventana_nuevo_habito.habito_editado.connect(self._on_habito_editado)
            self.ventana_nuevo_habito.ventana_cerrada.connect(self._on_ventana_nuevo_habito_cerrada)

            # Mostrar la ventana
            self.ventana_nuevo_habito.mostrar()

        except Exception as e:
            logger.error(f"Error abriendo ventana de edición para hábito {habito_id}: {e}")
            self._mostrar_error(f"Error al abrir ventana de edición: {e}")

    def _on_habito_editado(self, habito_id: int):
        """Manejar cuando se edita un hábito"""
        try:
            logger.info(f"Hábito {habito_id} editado exitosamente")

            # Actualizar la lista de hábitos
            self.actualizar_habitos()

            # Emitir señal de actualización
            self.habito_actualizado.emit(habito_id)

        except Exception as e:
            logger.error(f"Error procesando hábito editado {habito_id}: {e}")

    def _on_close(self, event):
        """Manejar cierre de ventana"""
        try:
            # Cerrar ventanas secundarias si están abiertas
            if self.ventana_nuevo_habito is not None:
                self.ventana_nuevo_habito.ocultar()
                self.ventana_nuevo_habito = None

            logger.info(f"Cerrando ventana de hábitos para usuario {self.id_usuario}")
            self.ventana_cerrada.emit()
            event.accept()

        except Exception as e:
            logger.error(f"Error cerrando ventana: {e}")
            event.accept()  # Asegurar que la ventana se cierre


if __name__ == '__main__':
    # Ejemplo de uso del controlador
    try:
        app = QApplication(sys.argv)
        controller = HabitosController(id_usuario=14)
        controller.mostrar()

        # Ejecutar el bucle de eventos de la aplicación
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Error al iniciar controlador de hábitos: {e}")
        QMessageBox.critical(None, "Error", f"Error al iniciar la aplicación: {e}")
        sys.exit(1)