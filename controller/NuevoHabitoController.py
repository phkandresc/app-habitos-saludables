from PyQt6.QtCore import pyqtSignal, QObject, QDate
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from datetime import date
from typing import Optional, List
import logging

from repository.HabitosRepository import HabitosRepository
from repository.CategoriaRepository import CategoriasRepository
from view.windows.VentanaNuevoHabito import Ui_ventanaRegistrarHabito

# Configurar logging
logger = logging.getLogger(__name__)


class NuevoHabitoController(QObject):
    """Controlador para la creación de nuevos hábitos"""
    habito_editado = pyqtSignal(int)   # Señal con ID del hábito editado
    habito_agregado = pyqtSignal(int)  # Señal con ID del hábito creado
    ventana_cerrada = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    # Mapeo de días de la semana según la interfaz
    CHECKBOXES_DIAS = {
        "Lunes": "checkLunes",
        "Martes": "checkMartes",
        "Miércoles": "checkMiercoles",
        "Jueves": "checkJueves",
        "Viernes": "checkViernes",
        "Sábado": "checkSabado",
        "Domingo": "checkDomingo"
    }

    def __init__(self, id_usuario: int, habito_id: Optional[int] = None):
        super().__init__()

        if not self._validar_id_usuario(id_usuario):
            raise ValueError("ID de usuario inválido")

        self.id_usuario = id_usuario
        self.habito_id = habito_id  # None para crear, ID para editar
        self.modo_edicion = habito_id is not None

        # Inicialización de vista
        self.vista = QMainWindow()
        self.ui = Ui_ventanaRegistrarHabito()
        self.ui.setupUi(self.vista)

        # Inicialización de repositorios
        self.habitos_repository = HabitosRepository()
        self.categorias_repository = CategoriasRepository()

        self._setup_controller()

    def _validar_id_usuario(self, id_usuario: int) -> bool:
        """Validar que el ID de usuario sea válido"""
        return isinstance(id_usuario, int) and id_usuario > 0

    def _setup_controller(self):
        """Configuración inicial del controlador"""
        try:
            self._conectar_eventos()
            self._configurar_interfaz()
            self._cargar_categorias()

            # Si estamos en modo edición, cargar datos del hábito
            if self.modo_edicion:
                self._cargar_datos_habito()

            logger.info(
                f"Controlador de hábito inicializado para usuario {self.id_usuario} - Modo: {'Edición' if self.modo_edicion else 'Creación'}")
        except Exception as e:
            logger.error(f"Error inicializando controlador de hábito: {e}")
            self.error_ocurrido.emit(f"Error al inicializar: {e}")

    def _conectar_eventos(self):
        """Conectar eventos de la vista"""
        self.vista.closeEvent = self._on_close

        # Conectar botones según la interfaz real
        self.ui.btnGuardarHabito.clicked.connect(self._on_guardar_habito)
        self.ui.btnCancelar.clicked.connect(self._on_cancelar)

    def _configurar_interfaz(self):
        """Configurar elementos de la interfaz"""
        try:
            # Configurar título según el modo
            titulo = "Editar Hábito" if self.modo_edicion else "Nuevo Hábito"
            self.vista.setWindowTitle(titulo)

            # Configurar texto del botón
            texto_boton = "Actualizar" if self.modo_edicion else "Guardar"
            self.ui.btnGuardarHabito.setText(texto_boton)

            # Limpiar el combo de categorías que viene con datos de prueba
            self.ui.cmbCategoria.clear()

            # Configurar placeholder para el nombre
            self.ui.txtNombre.setPlaceholderText("Ingrese el nombre del hábito")

        except Exception as e:
            logger.error(f"Error configurando interfaz: {e}")

    def _cargar_datos_habito(self):
        """Cargar datos del hábito para edición"""
        try:
            habito = self.habitos_repository.obtener_habito_por_id(self.habito_id)
            if not habito:
                raise ValueError(f"Hábito con ID {self.habito_id} no encontrado")

            # Cargar nombre
            self.ui.txtNombre.setText(habito.nombre)

            # Cargar categoría
            self._seleccionar_categoria_en_combo(habito.id_categoria)

            # Cargar días de la frecuencia
            self._seleccionar_dias_frecuencia(habito.frecuencia)

            logger.info(f"Datos del hábito {self.habito_id} cargados para edición")

        except Exception as e:
            logger.error(f"Error cargando datos del hábito: {e}")
            self._mostrar_error(f"Error cargando datos del hábito: {e}")

    def _seleccionar_categoria_en_combo(self, id_categoria: Optional[int]):
        """Seleccionar la categoría correspondiente en el combo"""
        try:
            if id_categoria is None:
                self.ui.cmbCategoria.setCurrentIndex(0)  # "Sin categoría"
                return

            for i in range(self.ui.cmbCategoria.count()):
                if self.ui.cmbCategoria.itemData(i) == id_categoria:
                    self.ui.cmbCategoria.setCurrentIndex(i)
                    break

        except Exception as e:
            logger.error(f"Error seleccionando categoría: {e}")

    def _seleccionar_dias_frecuencia(self, frecuencia: str):
        """Seleccionar días según la frecuencia del hábito"""
        try:
            # Primero limpiar todos los checkboxes
            for checkbox_name in self.CHECKBOXES_DIAS.values():
                checkbox = getattr(self.ui, checkbox_name, None)
                if checkbox:
                    checkbox.setChecked(False)

            if frecuencia == "diario":
                # Marcar todos los días
                for checkbox_name in self.CHECKBOXES_DIAS.values():
                    checkbox = getattr(self.ui, checkbox_name, None)
                    if checkbox:
                        checkbox.setChecked(True)
            else:
                # Frecuencia personalizada - marcar días específicos
                dias_frecuencia = frecuencia.split(",")
                for dia in dias_frecuencia:
                    dia = dia.strip()
                    if dia in self.CHECKBOXES_DIAS:
                        checkbox_name = self.CHECKBOXES_DIAS[dia]
                        checkbox = getattr(self.ui, checkbox_name, None)
                        if checkbox:
                            checkbox.setChecked(True)

        except Exception as e:
            logger.error(f"Error seleccionando días de frecuencia: {e}")

    def _on_guardar_habito(self):
        """Manejar guardar/actualizar hábito"""
        try:
            # Validar formulario
            if not self._validar_formulario():
                return

            # Obtener datos del formulario
            datos_habito = self._obtener_datos_formulario()

            if self.modo_edicion:
                # Actualizar hábito existente
                if self._actualizar_habito(datos_habito):
                    logger.info(f"Hábito {self.habito_id} actualizado exitosamente")
                    self.habito_editado.emit(self.habito_id)
                    self._mostrar_informacion("Hábito actualizado exitosamente")
                    self.ocultar()
                else:
                    self._mostrar_error("Error al actualizar el hábito")
            else:
                # Crear nuevo hábito
                habito_id = self._crear_habito(datos_habito)
                if habito_id:
                    logger.info(f"Hábito creado exitosamente con ID: {habito_id}")
                    self.habito_agregado.emit(habito_id)
                    self._mostrar_informacion("Hábito creado exitosamente")
                    self.ocultar()
                else:
                    self._mostrar_error("Error al crear el hábito")

        except Exception as e:
            logger.error(f"Error guardando hábito: {e}")
            self._mostrar_error(f"Error al guardar el hábito: {e}")

    def _actualizar_habito(self, datos: dict) -> bool:
        """Actualizar hábito existente en la base de datos"""
        try:
            # Agregar ID del hábito a los datos
            datos['id_habito'] = self.habito_id

            # Actualizar en la base de datos
            return self.habitos_repository.actualizar_habito(self.habito_id, datos)

        except Exception as e:
            logger.error(f"Error actualizando hábito en BD: {e}")
            return False

    def _cargar_categorias(self):
        """Cargar categorías disponibles en el combo"""
        try:
            # Limpiar combo y agregar opción por defecto
            self.ui.cmbCategoria.clear()
            self.ui.cmbCategoria.addItem("Sin categoría", None)

            # Cargar categorías del usuario
            categorias = self.categorias_repository.obtener_todas_categorias()
            for categoria in categorias:
                self.ui.cmbCategoria.addItem(categoria.nombre, categoria.id_categoria)

            logger.info(f"Cargadas {len(categorias)} categorías")

        except Exception as e:
            logger.error(f"Error cargando categorías: {e}")
            self._mostrar_error("Error al cargar las categorías")

    def _on_guardar_habito(self):
        """Manejar guardar/actualizar hábito"""
        try:
            # Validar formulario
            if not self._validar_formulario():
                return

            # Obtener datos del formulario
            datos_habito = self._obtener_datos_formulario()

            if self.modo_edicion:
                # Actualizar hábito existente
                if self._actualizar_habito(datos_habito):
                    logger.info(f"Hábito {self.habito_id} actualizado exitosamente")
                    self.habito_editado.emit(self.habito_id)
                    self._mostrar_informacion("Hábito actualizado exitosamente")
                    self.ocultar()
                else:
                    self._mostrar_error("Error al actualizar el hábito")
            else:
                # Crear nuevo hábito
                habito_id = self._crear_habito(datos_habito)
                if habito_id:
                    logger.info(f"Hábito creado exitosamente con ID: {habito_id}")
                    self.habito_agregado.emit(habito_id)
                    self._mostrar_informacion("Hábito creado exitosamente")
                    self.ocultar()
                else:
                    self._mostrar_error("Error al crear el hábito")

        except Exception as e:
            logger.error(f"Error guardando hábito: {e}")
            self._mostrar_error(f"Error al guardar el hábito: {e}")

    def _validar_formulario(self) -> bool:
        """Validar que el formulario esté completo"""
        try:
            # Validar nombre obligatorio
            if not self.ui.txtNombre.text().strip():
                self._mostrar_error("El nombre del hábito es obligatorio")
                self.ui.txtNombre.setFocus()
                return False

            # Validar que al menos un día esté seleccionado
            dias_seleccionados = self._obtener_dias_seleccionados()
            if not dias_seleccionados:
                self._mostrar_error("Debe seleccionar al menos un día de la semana")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validando formulario: {e}")
            return False

    def _obtener_datos_formulario(self) -> dict:
        """Obtener todos los datos del formulario"""
        try:
            datos = {}

            # Nombre obligatorio
            datos['nombre'] = self.ui.txtNombre.text().strip()

            # Frecuencia basada en días seleccionados
            dias_seleccionados = self._obtener_dias_seleccionados()

            # Si todos los días están seleccionados, es diario
            if len(dias_seleccionados) == 7:
                datos['frecuencia'] = "diario"
            else:
                # Unir días seleccionados con comas
                datos['frecuencia'] = ",".join(dias_seleccionados)

            # Categoría seleccionada
            categoria_data = self.ui.cmbCategoria.currentData()
            datos['id_categoria'] = categoria_data if categoria_data is not None else None

            # Fecha de creación actual
            datos['fecha_creacion'] = date.today()

            # Usuario
            datos['id_usuario'] = self.id_usuario

            return datos

        except Exception as e:
            logger.error(f"Error obteniendo datos del formulario: {e}")
            return {}

    def _obtener_dias_seleccionados(self) -> List[str]:
        """Obtener lista de días seleccionados en los checkboxes"""
        dias_seleccionados = []

        for dia, checkbox_name in self.CHECKBOXES_DIAS.items():
            checkbox = getattr(self.ui, checkbox_name, None)
            if checkbox and checkbox.isChecked():
                dias_seleccionados.append(dia)

        return dias_seleccionados

    def _crear_habito(self, datos: dict) -> Optional[int]:
        """Crear hábito en la base de datos usando diccionario de datos"""
        try:
            habito = self.habitos_repository.crear_habito(datos)

            if habito:
                return habito.id_habito
            else:
                return None
        except Exception as e:
            logger.error(f"Error creando hábito en BD: {e}")
            return None

    def _on_cancelar(self):
        """Manejar cancelación"""
        logger.info("Cancelando creación de hábito")
        self.ocultar()

    def _seleccionar_dias_frecuencia(self, frecuencia: str):
        """Seleccionar días según la frecuencia del hábito"""
        try:
            # Primero limpiar todos los checkboxes
            for checkbox_name in self.CHECKBOXES_DIAS.values():
                checkbox = getattr(self.ui, checkbox_name, None)
                if checkbox:
                    checkbox.setChecked(False)

            if frecuencia == "diario":
                # Marcar todos los días
                for checkbox_name in self.CHECKBOXES_DIAS.values():
                    checkbox = getattr(self.ui, checkbox_name, None)
                    if checkbox:
                        checkbox.setChecked(True)
            else:
                # Frecuencia personalizada - marcar días específicos
                dias_frecuencia = frecuencia.split(",")
                for dia in dias_frecuencia:
                    dia = dia.strip()
                    if dia in self.CHECKBOXES_DIAS:
                        checkbox_name = self.CHECKBOXES_DIAS[dia]
                        checkbox = getattr(self.ui, checkbox_name, None)
                        if checkbox:
                            checkbox.setChecked(True)

        except Exception as e:
            logger.error(f"Error seleccionando días de frecuencia: {e}")

    def _mostrar_error(self, mensaje: str):
        """Mostrar mensaje de error al usuario"""
        QMessageBox.critical(self.vista, "Error", mensaje)

    def _mostrar_informacion(self, mensaje: str):
        """Mostrar mensaje de información al usuario"""
        QMessageBox.information(self.vista, "Información", mensaje)

    def _on_close(self, event):
        """Manejar cierre de ventana"""
        logger.info("Cerrando ventana de nuevo hábito")
        self.ventana_cerrada.emit()
        event.accept()

    # Métodos públicos para la interfaz
    def mostrar(self):
        """Mostrar la ventana"""
        try:
            self._limpiar_formulario()
            self.vista.show()
            self.ui.txtNombre.setFocus()  # Enfocar campo nombre
            logger.info("Ventana de nuevo hábito mostrada")
        except Exception as e:
            logger.error(f"Error mostrando ventana: {e}")

    def ocultar(self):
        """Ocultar la ventana"""
        try:
            self.vista.hide()
            logger.info("Ventana de nuevo hábito ocultada")
        except Exception as e:
            logger.error(f"Error ocultando ventana: {e}")

    def preseleccionar_dias(self, dias: List[str]):
        """Preseleccionar días específicos"""
        try:
            for dia in dias:
                if dia in self.CHECKBOXES_DIAS:
                    checkbox_name = self.CHECKBOXES_DIAS[dia]
                    checkbox = getattr(self.ui, checkbox_name, None)
                    if checkbox:
                        checkbox.setChecked(True)
        except Exception as e:
            logger.error(f"Error preseleccionando días: {e}")

    def establecer_categoria_por_defecto(self, id_categoria: int):
        """Establecer una categoría específica como seleccionada"""
        try:
            for i in range(self.ui.cmbCategoria.count()):
                if self.ui.cmbCategoria.itemData(i) == id_categoria:
                    self.ui.cmbCategoria.setCurrentIndex(i)
                    break
        except Exception as e:
            logger.error(f"Error estableciendo categoría por defecto: {e}")

    def _actualizar_habito(self, datos: dict) -> bool:
        """Actualizar hábito existente en la base de datos"""
        try:
            # Agregar ID del hábito a los datos
            datos['id_habito'] = self.habito_id

            # Actualizar en la base de datos
            resultado = self.habitos_repository.actualizar_habito(self.habito_id, datos)

            if resultado:
                logger.info(f"Hábito {self.habito_id} actualizado exitosamente en BD")
                return True
            else:
                logger.error(f"Error actualizando hábito {self.habito_id} en BD")
                return False

        except Exception as e:
            logger.error(f"Error actualizando hábito en BD: {e}")
            return False

    def establecer_nombre_por_defecto(self, nombre: str):
        """Establecer un nombre por defecto en el campo"""
        try:
            self.ui.txtNombre.setText(nombre)
        except Exception as e:
            logger.error(f"Error estableciendo nombre por defecto: {e}")

    def _limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        try:
            # Solo limpiar si NO estamos en modo edición
            if not self.modo_edicion:
                # Limpiar nombre
                self.ui.txtNombre.clear()

                # Resetear categoría a "Sin categoría"
                self.ui.cmbCategoria.setCurrentIndex(0)

                # Desmarcar todos los checkboxes de días
                for checkbox_name in self.CHECKBOXES_DIAS.values():
                    checkbox = getattr(self.ui, checkbox_name, None)
                    if checkbox:
                        checkbox.setChecked(False)

                logger.info("Formulario limpiado")

        except Exception as e:
            logger.error(f"Error limpiando formulario: {e}")