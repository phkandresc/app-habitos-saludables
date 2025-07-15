import logging
from typing import List

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QListWidgetItem, QLabel, QMessageBox

from controller.NuevaComunidadController import NuevaComunidadController
from repository.ComunidadRepository import ComunidadRepository
from repository.IncorporaComunidadRepository import IncorporaComunidadRepository
from repository.CategoriaRepository import CategoriasRepository
from repository.UsuarioRepository import UsuarioRepository
from view.widgets.ComunidadWidget import ComunidadWidget
from view.windows.VentanaComunidades import Ui_ventanaComunidades

# Configurar logging
logger = logging.getLogger(__name__)

class ComunidadController(QObject):
    """Controlador para la gestión de comunidades"""

    ventana_cerrada = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self, id_usuario: int):
        super().__init__()

        if not self._validar_id_usuario(id_usuario):
            raise ValueError("ID de usuario inválido")

        self.id_usuario = id_usuario

        # Referencias a ventanas secundarias
        self.ventana_nueva_comunidad = None

        # Inicialización de vista
        self.vista = QMainWindow()
        self.ui = Ui_ventanaComunidades()
        self.ui.setupUi(self.vista)

        # Inicialización de repositorios
        self.comunidad_repository = ComunidadRepository()
        self.incorpora_repository = IncorporaComunidadRepository()
        self.categorias_repository = CategoriasRepository()
        self.usuario_repository = UsuarioRepository()

        self._setup_controller()

    def _validar_id_usuario(self, id_usuario: int) -> bool:
        """Validar que el ID de usuario sea válido"""
        return isinstance(id_usuario, int) and id_usuario > 0

    def _setup_controller(self):
        """Configuración inicial del controlador"""
        try:
            self._conectar_eventos()
            self._cargar_filtros()
            self.cargar_mis_comunidades()
            self.cargar_todas_comunidades()
            logger.info(f"Controlador de comunidades inicializado para usuario {self.id_usuario}")
        except Exception as e:
            logger.error(f"Error inicializando controlador: {e}")
            self.error_ocurrido.emit(f"Error al inicializar: {e}")

    def _conectar_eventos(self):
        """Conectar eventos de la vista"""
        self.vista.closeEvent = self._on_close

        # Conectar botones
        if hasattr(self.ui, 'btnCrearUnaComunidad'):
            self.ui.btnCrearUnaComunidad.clicked.connect(self.abrir_ventana_crear_comunidad)

        # Remover conexión del filtro ya que no lo usaremos
        # if hasattr(self.ui, 'cmbFiltroComunidades'):
        #     self.ui.cmbFiltroComunidades.currentTextChanged.connect(self._on_filtro_cambiado)

    def _cargar_filtros(self):
        """Cargar opciones del filtro - Ya no se usa"""
        pass
        # try:
        #     if hasattr(self.ui, 'cmbFiltroComunidades'):
        #         self.ui.cmbFiltroComunidades.clear()
        #         self.ui.cmbFiltroComunidades.addItems(["Todas", "Unido"])
        # except Exception as e:
        #     logger.error(f"Error cargando filtros: {e}")

    def _on_filtro_cambiado(self):
        """Manejar cambio en el filtro de comunidades - Ya no se usa"""
        pass
        # try:
        #     self.cargar_todas_comunidades()
        # except Exception as e:
        #     logger.error(f"Error aplicando filtro: {e}")
        #     self.error_ocurrido.emit(f"Error aplicando filtro: {e}")

    def cargar_mis_comunidades(self):
        """Cargar comunidades del usuario en la primera lista"""
        self._limpiar_lista(self.ui.listMisComunidades)

        try:
            # Obtener comunidades creadas por el usuario
            comunidades_creadas = self.comunidad_repository.obtener_comunidades_por_creador(self.id_usuario)

            # Obtener comunidades donde el usuario está incorporado
            incorporaciones = self.incorpora_repository.obtener_comunidades_con_detalles_usuario(
                self.id_usuario, 'activo'
            )

            # Combinar ambas listas evitando duplicados
            todas_mis_comunidades = []
            ids_ya_agregados = set()

            # Agregar comunidades creadas
            for comunidad in comunidades_creadas:
                todas_mis_comunidades.append({
                    'comunidad': comunidad,
                    'es_creador': True,
                    'incorporacion': None
                })
                ids_ya_agregados.add(comunidad.id_comunidad)

            # Agregar comunidades donde está incorporado (si no es creador)
            for item in incorporaciones:
                comunidad = item['comunidad']
                incorporacion = item['incorporacion']

                if comunidad.id_comunidad not in ids_ya_agregados:
                    todas_mis_comunidades.append({
                        'comunidad': comunidad,
                        'es_creador': False,
                        'incorporacion': incorporacion
                    })

            if not todas_mis_comunidades:
                self._mostrar_mensaje_sin_comunidades(
                    self.ui.listMisComunidades,
                    "No tienes comunidades creadas ni te has unido a ninguna 🏠"
                )
                return

            self._agregar_comunidades_a_lista_mejorada(todas_mis_comunidades, self.ui.listMisComunidades)
            logger.info(f"Cargadas {len(todas_mis_comunidades)} comunidades del usuario")

        except Exception as e:
            logger.error(f"Error cargando mis comunidades: {e}")
            self._mostrar_mensaje_error(self.ui.listMisComunidades)
            self.error_ocurrido.emit(f"Error cargando mis comunidades: {e}")

    def cargar_todas_comunidades(self):
        """Cargar todas las comunidades disponibles en la segunda lista"""
        self._limpiar_lista(self.ui.listTodasComunidades)

        try:
            # Siempre mostrar todas las comunidades sin filtro
            todas_comunidades = self.comunidad_repository.obtener_todas_comunidades()

            if not todas_comunidades:
                self._mostrar_mensaje_sin_comunidades(
                    self.ui.listTodasComunidades,
                    "No hay comunidades disponibles 🌍"
                )
                return

            # Convertir a formato con información de incorporación
            comunidades_con_estado = []
            for comunidad in todas_comunidades:
                incorporacion = self.incorpora_repository.obtener_incorporacion(
                    self.id_usuario, comunidad.id_comunidad
                )

                comunidades_con_estado.append({
                    'comunidad': comunidad,
                    'es_creador': comunidad.id_creador == self.id_usuario,
                    'incorporacion': incorporacion
                })

            self._agregar_comunidades_a_lista_mejorada(comunidades_con_estado, self.ui.listTodasComunidades)
            logger.info(f"Cargadas {len(todas_comunidades)} comunidades disponibles")

        except Exception as e:
            logger.error(f"Error cargando todas las comunidades: {e}")
            self._mostrar_mensaje_error(self.ui.listTodasComunidades)
            self.error_ocurrido.emit(f"Error cargando todas las comunidades: {e}")

    def _limpiar_lista(self, lista_widget):
        """Limpiar una lista específica"""
        try:
            lista_widget.clear()
        except Exception as e:
            logger.error(f"Error limpiando lista: {e}")

    def _agregar_comunidades_a_lista_mejorada(self, comunidades_data: List[dict], lista_widget):
        """Agregar comunidades a una lista específica con información mejorada"""
        for item in comunidades_data:
            try:
                comunidad = item['comunidad']
                es_creador = item['es_creador']
                incorporacion = item['incorporacion']

                comunidad_widget = self._crear_comunidad_widget_mejorado(
                    comunidad, es_creador, incorporacion
                )
                self._agregar_widget_a_lista(comunidad_widget, lista_widget)

            except Exception as e:
                logger.error(f"Error agregando comunidad a lista: {e}")
                continue

    def _crear_comunidad_widget_mejorado(self, comunidad, es_creador: bool = False, incorporacion=None):
        """Crear widget de comunidad con información mejorada"""
        try:
            # Obtener categorías de la comunidad
            categorias_ids = self.comunidad_repository.obtener_categorias_de_comunidad(comunidad.id_comunidad)
            categorias_nombres = []
            for cat_id in categorias_ids:
                categoria = self.categorias_repository.obtener_categoria_por_id(cat_id)
                if categoria:
                    categorias_nombres.append(categoria.nombre)

            # Obtener nombre del creador usando el UsuarioRepository
            creador_usuario = self.usuario_repository.obtener_usuario_por_id(comunidad.id_creador)
            if creador_usuario:
                creador_nombre = creador_usuario.nombre_usuario
            else:
                # Fallback si no se encuentra el usuario
                creador_nombre = f"Usuario {comunidad.id_creador}"

            # Obtener número real de miembros
            num_miembros = self.incorpora_repository.contar_miembros_comunidad(
                comunidad.id_comunidad, 'activo'
            )
            # Sumar 1 si el creador no está en la tabla de incorporaciones
            if not self.incorpora_repository.verificar_usuario_en_comunidad(
                comunidad.id_creador, comunidad.id_comunidad
            ):
                num_miembros += 1

            # Determinar estado de incorporación
            esta_unido = False

            if es_creador:
                esta_unido = True
            elif incorporacion:
                esta_unido = incorporacion.es_activo()

            # Crear widget con parámetros correctos
            comunidad_widget = ComunidadWidget(
                comunidad_id=comunidad.id_comunidad,
                nombre=comunidad.nombre,
                creador_nombre=creador_nombre,
                categorias=categorias_nombres,
                num_miembros=num_miembros,
                esta_unido=esta_unido
            )

            # Conectar señales del widget
            comunidad_widget.unirseClicked.connect(self._on_unirse_comunidad)
            comunidad_widget.salirClicked.connect(self._on_salir_comunidad)
            comunidad_widget.verClicked.connect(self._on_ver_comunidad)

            return comunidad_widget

        except Exception as e:
            logger.error(f"Error creando widget de comunidad: {e}")
            return None

    def _agregar_widget_a_lista(self, widget, lista_widget):
        """Agregar widget a una lista específica"""
        try:
            if widget is None:
                return

            list_item = QListWidgetItem()
            list_item.setSizeHint(widget.sizeHint())
            lista_widget.addItem(list_item)
            lista_widget.setItemWidget(list_item, widget)
        except Exception as e:
            logger.error(f"Error agregando widget a lista: {e}")

    def _mostrar_mensaje_sin_comunidades(self, lista_widget, mensaje: str):
        """Mostrar mensaje cuando no hay comunidades"""
        mensaje_widget = self._crear_mensaje_informativo(mensaje)
        self._agregar_widget_a_lista(mensaje_widget, lista_widget)

    def _mostrar_mensaje_error(self, lista_widget):
        """Mostrar mensaje de error en una lista"""
        mensaje_widget = self._crear_mensaje_informativo(
            "Error al cargar las comunidades ⚠️",
            color="#e74c3c"
        )
        self._agregar_widget_a_lista(mensaje_widget, lista_widget)

    def _crear_mensaje_informativo(self, texto: str, color: str = "#7f8c8d") -> QLabel:
        """Crear un label informativo para mostrar en las listas"""
        try:
            label = QLabel(texto)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 12pt;
                    padding: 20px;
                    text-align: center;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    margin: 10px;
                }}
            """)
            label.setWordWrap(True)
            return label
        except Exception as e:
            logger.error(f"Error creando mensaje informativo: {e}")
            return QLabel("Error")

    def _on_unirse_comunidad(self, id_comunidad: int):
        """Manejar evento de unirse a una comunidad"""
        try:
            # Verificar si ya está unido
            if self.incorpora_repository.verificar_usuario_en_comunidad(
                self.id_usuario, id_comunidad
            ):
                QMessageBox.information(
                    self.vista,
                    "Ya unido",
                    "Ya estás unido a esta comunidad"
                )
                return

            # Incorporar usuario a la comunidad
            incorporacion_data = {
                'id_usuario': self.id_usuario,
                'id_comunidad': id_comunidad,
                'estado': 'activo'
            }

            incorporacion = self.incorpora_repository.incorporar_usuario_a_comunidad(incorporacion_data)

            if incorporacion:
                QMessageBox.information(
                    self.vista,
                    "¡Éxito!",
                    "Te has unido exitosamente a la comunidad"
                )
                # Recargar listas
                self.cargar_mis_comunidades()
                self.cargar_todas_comunidades()
                logger.info(f"Usuario {self.id_usuario} se unió a comunidad {id_comunidad}")
            else:
                self._mostrar_error("No se pudo unir a la comunidad")

        except Exception as e:
            logger.error(f"Error uniéndose a comunidad {id_comunidad}: {e}")
            self._mostrar_error(f"Error al unirse a la comunidad: {e}")

    def _on_salir_comunidad(self, id_comunidad: int):
        """Manejar evento de salir de una comunidad"""
        try:
            # Verificar si es el creador
            comunidad = self.comunidad_repository.obtener_comunidad_por_id(id_comunidad)
            if comunidad and comunidad.id_creador == self.id_usuario:
                QMessageBox.warning(
                    self.vista,
                    "No permitido",
                    "No puedes salir de una comunidad que creaste"
                )
                return

            # Confirmar acción
            respuesta = QMessageBox.question(
                self.vista,
                "Confirmar",
                "¿Estás seguro de que deseas salir de esta comunidad?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                # Eliminar incorporación
                if self.incorpora_repository.eliminar_incorporacion(self.id_usuario, id_comunidad):
                    QMessageBox.information(
                        self.vista,
                        "Éxito",
                        "Has salido de la comunidad"
                    )
                    # Recargar listas
                    self.cargar_mis_comunidades()
                    self.cargar_todas_comunidades()
                    logger.info(f"Usuario {self.id_usuario} salió de comunidad {id_comunidad}")
                else:
                    self._mostrar_error("No se pudo salir de la comunidad")

        except Exception as e:
            logger.error(f"Error saliendo de comunidad {id_comunidad}: {e}")
            self._mostrar_error(f"Error al salir de la comunidad: {e}")

    def _on_ver_comunidad(self, id_comunidad: int):
        """Manejar evento de ver detalles de una comunidad"""
        try:
            # Obtener estadísticas de la comunidad
            stats = self.incorpora_repository.obtener_estadisticas_comunidad(id_comunidad)
            comunidad = self.comunidad_repository.obtener_comunidad_por_id(id_comunidad)

            if comunidad and stats:
                mensaje = f"""
Nombre: {comunidad.nombre}
Creador: Usuario {comunidad.id_creador}
Total de miembros: {stats['total_miembros']}
Miembros activos: {stats['miembros_activos']}
Miembros pendientes: {stats['miembros_pendientes']}
Miembros bloqueados: {stats['miembros_bloqueados']}
                """

                QMessageBox.information(
                    self.vista,
                    f"Detalles de {comunidad.nombre}",
                    mensaje.strip()
                )
            else:
                self._mostrar_error("No se pudieron obtener los detalles de la comunidad")

            logger.info(f"Viendo detalles de comunidad {id_comunidad}")

        except Exception as e:
            logger.error(f"Error viendo comunidad {id_comunidad}: {e}")
            self._mostrar_error(f"Error al ver la comunidad: {e}")

    def abrir_ventana_crear_comunidad(self):
        """Abrir ventana para crear nueva comunidad"""
        try:
            if self.ventana_nueva_comunidad is not None:
                self.ventana_nueva_comunidad.vista.raise_()
                self.ventana_nueva_comunidad.vista.activateWindow()
                return

            # Crear nueva instancia del controlador
            self.ventana_nueva_comunidad = NuevaComunidadController(self.id_usuario)

            # Conectar señales
            self.ventana_nueva_comunidad.comunidad_creada.connect(self._on_comunidad_creada)
            self.ventana_nueva_comunidad.ventana_cerrada.connect(self._on_ventana_nueva_comunidad_cerrada)
            self.ventana_nueva_comunidad.error_ocurrido.connect(self.error_ocurrido.emit)

            # Mostrar ventana
            self.ventana_nueva_comunidad.mostrar_ventana()

            logger.info("Ventana de nueva comunidad abierta")

        except Exception as e:
            logger.error(f"Error abriendo ventana crear comunidad: {e}")
            self._mostrar_error(f"Error al abrir ventana: {e}")

    def _on_comunidad_creada(self, comunidad_id: int):
        """Manejar evento cuando se crea una nueva comunidad"""
        try:
            # Recargar las listas para mostrar la nueva comunidad
            self.cargar_mis_comunidades()
            self.cargar_todas_comunidades()

            logger.info(f"Nueva comunidad creada con ID {comunidad_id}, listas recargadas")

        except Exception as e:
            logger.error(f"Error manejando comunidad creada: {e}")

    def _on_ventana_nueva_comunidad_cerrada(self):
        """Manejar evento cuando se cierra la ventana de nueva comunidad"""
        try:
            if self.ventana_nueva_comunidad is not None:
                self.ventana_nueva_comunidad.deleteLater()
                self.ventana_nueva_comunidad = None

            logger.info("Ventana de nueva comunidad cerrada y limpiada")

        except Exception as e:
            logger.error(f"Error limpiando ventana nueva comunidad: {e}")

    def _mostrar_error(self, mensaje: str):
        """Mostrar mensaje de error"""
        try:
            QMessageBox.critical(
                self.vista,
                "Error",
                mensaje
            )
        except Exception as e:
            logger.error(f"Error mostrando mensaje de error: {e}")

    def _on_close(self, event):
        """Manejar cierre de ventana"""
        try:
            self.ventana_cerrada.emit()
            event.accept()
        except Exception as e:
            logger.error(f"Error cerrando ventana: {e}")
            event.accept()

    def mostrar_vista(self):
        """Mostrar la vista principal"""
        try:
            self.vista.show()
        except Exception as e:
            logger.error(f"Error mostrando vista: {e}")
            self._mostrar_error(f"Error mostrando vista: {e}")
