import logging
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QHeaderView
from PyQt6.QtCore import Qt

from repository.LogroRepository import LogroRepository
from repository.UsuarioRepository import UsuarioRepository
from view.widgets.RankingWidget import RankingWidget
from view.windows.VentanaRankingGeneral import Ui_ventanaRanking

logger = logging.getLogger(__name__)

class RankingController(QObject):
    """Controlador para la vista de ranking."""

    ventana_cerrada = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self, id_usuario: int):
        super().__init__()

        if not self._validar_id_usuario(id_usuario):
            raise ValueError("ID de usuario inválido")

        self.id_usuario = id_usuario
        self.ranking_data = []
        self.posicion_usuario_actual = None
        self.puntos_usuario_actual = 0

        # Inicialización de vista - igual que HabitosController
        self.vista = QMainWindow()
        self.ui = Ui_ventanaRanking()
        self.ui.setupUi(self.vista)

        # Inicialización de repositorios
        self.logro_repository = LogroRepository()
        self.usuario_repository = UsuarioRepository()

        self._setup_controller()

    def _validar_id_usuario(self, id_usuario: int) -> bool:
        """Validar que el ID de usuario sea válido."""
        return isinstance(id_usuario, int) and id_usuario > 0

    def _setup_controller(self):
        """Configurar el controlador y conectar señales."""
        try:
            self._setup_tabla_ranking()
            self._cargar_ranking()
            self._conectar_senales()
            logger.info(f"Controlador de ranking inicializado para usuario {self.id_usuario}")
        except Exception as e:
            logger.error(f"Error configurando controlador de ranking: {e}")
            self.error_ocurrido.emit(f"Error configurando ranking: {str(e)}")

    def _setup_tabla_ranking(self):
        """Configurar la tabla de ranking."""
        try:
            tabla = self.ui.tableRanking

            # Configurar columnas
            tabla.setColumnCount(3)
            tabla.setHorizontalHeaderLabels(["Posición", "Usuario", "Puntos"])

            # Configurar propiedades de la tabla
            tabla.setAlternatingRowColors(True)
            tabla.setSelectionBehavior(tabla.SelectionBehavior.SelectRows)
            tabla.setEditTriggers(tabla.EditTrigger.NoEditTriggers)

            # Ajustar ancho de columnas
            header = tabla.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Posición
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Usuario
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Puntos

            # Ocultar números de fila
            tabla.verticalHeader().setVisible(False)

            logger.info("Tabla de ranking configurada")
        except Exception as e:
            logger.error(f"Error configurando tabla de ranking: {e}")
            raise

    def _cargar_ranking(self):
        """Cargar datos del ranking desde el repositorio."""
        try:
            # Obtener ranking general
            self.ranking_data = self.logro_repository.obtener_ranking_general()

            if not self.ranking_data:
                logger.warning("No se encontraron datos de ranking")
                self._mostrar_mensaje_sin_datos()
                return

            # Encontrar posición del usuario actual
            self._encontrar_posicion_usuario_actual()

            # Llenar tabla
            self._llenar_tabla_ranking()

            # Actualizar etiqueta de posición del usuario
            self._actualizar_posicion_usuario()

            logger.info(f"Ranking cargado: {len(self.ranking_data)} usuarios")
        except Exception as e:
            logger.error(f"Error cargando ranking: {e}")
            self.error_ocurrido.emit(f"Error cargando ranking: {str(e)}")

    def _encontrar_posicion_usuario_actual(self):
        """Encontrar la posición y puntos del usuario actual en el ranking."""
        for usuario_ranking in self.ranking_data:
            if usuario_ranking['id_usuario'] == self.id_usuario:
                self.posicion_usuario_actual = usuario_ranking['posicion']
                self.puntos_usuario_actual = usuario_ranking['puntos_totales']
                break

        if self.posicion_usuario_actual is None:
            logger.warning(f"Usuario {self.id_usuario} no encontrado en ranking")
            self.posicion_usuario_actual = len(self.ranking_data) + 1
            self.puntos_usuario_actual = 0

    def _llenar_tabla_ranking(self):
        """Llenar la tabla con los datos del ranking."""
        try:
            tabla = self.ui.tableRanking
            tabla.setRowCount(len(self.ranking_data))

            for row, usuario_ranking in enumerate(self.ranking_data):
                # Crear widget de ranking
                es_usuario_actual = usuario_ranking['id_usuario'] == self.id_usuario
                widget = RankingWidget(
                    posicion=usuario_ranking['posicion'],
                    nombre_usuario=usuario_ranking['nombre_usuario'],
                    puntos=usuario_ranking['puntos_totales'],
                    es_usuario_actual=es_usuario_actual
                )

                # Obtener items para la tabla
                items = widget.crear_items_tabla()

                # Insertar items en la tabla
                for col, item in enumerate(items):
                    tabla.setItem(row, col, item)

            logger.info(f"Tabla de ranking llenada con {len(self.ranking_data)} usuarios")
        except Exception as e:
            logger.error(f"Error llenando tabla de ranking: {e}")
            raise

    def _actualizar_posicion_usuario(self):
        """Actualizar el label con la posición del usuario actual."""
        try:
            # Obtener información del usuario actual
            usuario_actual = self.usuario_repository.obtener_usuario_por_id(self.id_usuario)
            nombre_usuario = usuario_actual.nombre_usuario if usuario_actual else "Usuario"

            # Usar los puntos obtenidos del ranking general
            puntos_usuario = self.puntos_usuario_actual

            # Crear texto de posición basado en si el usuario está en el ranking
            if self.posicion_usuario_actual and self.posicion_usuario_actual <= len(self.ranking_data):
                # Usuario está en el ranking
                texto_posicion = f"🧍 Tu posición: #{self.posicion_usuario_actual} - {nombre_usuario} ({puntos_usuario} pts)"
            else:
                # Usuario no está en el ranking o no tiene puntos
                texto_posicion = f"🧍 Tu posición: Sin ranking - {nombre_usuario} (0 pts)"

            self.ui.lblPosicionPuntos.setText(texto_posicion)
            logger.info(f"Posición del usuario actualizada: #{self.posicion_usuario_actual} - {nombre_usuario} - {puntos_usuario} pts")
        except Exception as e:
            logger.error(f"Error actualizando posición del usuario: {e}")
            # Fallback en caso de error
            self.ui.lblPosicionPuntos.setText("🧍 Tu posición: Error cargando datos")

    def _mostrar_mensaje_sin_datos(self):
        """Mostrar mensaje cuando no hay datos de ranking."""
        self.ui.tableRanking.setRowCount(1)
        self.ui.tableRanking.setColumnCount(1)
        self.ui.tableRanking.setHorizontalHeaderLabels(["Mensaje"])

        from PyQt6.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem("No hay datos de ranking disponibles")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.tableRanking.setItem(0, 0, item)

        self.ui.lblPosicionPuntos.setText("🧍 Tu posición: Sin datos")

    def _conectar_senales(self):
        """Conectar señales de la vista."""
        try:
            # Conectar señal de cierre de ventana - igual que HabitosController
            self.vista.closeEvent = self._on_ventana_cerrada
            logger.info("Señales conectadas en ranking controller")
        except Exception as e:
            logger.error(f"Error conectando señales: {e}")

    def _on_ventana_cerrada(self, event):
        """Manejar el cierre de la ventana."""
        try:
            logger.info(f"Ventana de ranking cerrada para usuario {self.id_usuario}")
            self.ventana_cerrada.emit()
            event.accept()
        except Exception as e:
            logger.error(f"Error cerrando ventana de ranking: {e}")

    def mostrar_ventana(self):
        """Mostrar la ventana de ranking."""
        try:
            self.vista.show()
            logger.info("Ventana de ranking mostrada")
        except Exception as e:
            logger.error(f"Error mostrando ventana de ranking: {e}")
            self.error_ocurrido.emit(f"Error mostrando ventana: {str(e)}")

    def actualizar_ranking(self):
        """Actualizar los datos del ranking."""
        try:
            self._cargar_ranking()
            logger.info("Ranking actualizado")
        except Exception as e:
            logger.error(f"Error actualizando ranking: {e}")
            self.error_ocurrido.emit(f"Error actualizando ranking: {str(e)}")

    def cerrar_ventana(self):
        """Cerrar la ventana de ranking."""
        try:
            if self.vista:
                self.vista.close()
        except Exception as e:
            logger.error(f"Error cerrando ventana de ranking: {e}")
