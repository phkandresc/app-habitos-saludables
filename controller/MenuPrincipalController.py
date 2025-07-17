from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt, QObject
from datetime import date
from typing import Optional
from controller.HabitosController import HabitosController
from controller.ComunidadController import ComunidadController
from controller.LogrosController import LogrosController
from controller.PerfilUsuarioController import PerfilUsuarioController
from controller.RankingController import RankingController
from view.windows.VentanaMenuPrincipal import Ui_ventanaMenuPrincipal
from view.widgets.HabitoWidget import HabitoWidget
from repository.HabitosRepository import HabitosRepository
from repository.CategoriaRepository import CategoriasRepository
from repository.SeguimientoDiarioRepository import SeguimientoDiarioRepository
from repository.LogroRepository import LogroRepository
from repository.NivelRepository import NivelRepository
from model.Usuario import Usuario
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class MenuPrincipalController(QObject):
    def __init__(self, usuario_autenticado: Usuario):
        super().__init__()
        self.vista = QMainWindow()
        self.ui = Ui_ventanaMenuPrincipal()
        self.ui.setupUi(self.vista)
        # Usuario autenticado
        self.usuario_autenticado = usuario_autenticado

        # Repositorios
        self.habitos_repository = HabitosRepository()
        self.categorias_repository = CategoriasRepository()
        self.logro_repository = LogroRepository()
        self.nivel_repository = NivelRepository()

        # Diccionario para gestionar controladores secundarios
        self.controladores = {}

        self._conectar_eventos()
        self._configurar_interfaz_usuario()
        self._cargar_habitos_del_dia()

    def _conectar_eventos(self):
        """Conecta los eventos de la interfaz con sus métodos"""
        self.ui.actionCerrar_Sesion.triggered.connect(self.cerrar_sesion)
        self.ui.action_Icono_Cerrar_Sesion.triggered.connect(self.cerrar_sesion)
        self.ui.action_Icono_Comunidad.triggered.connect(lambda: self.abrir_ventana('comunidad'))
        self.ui.action_item_Habitos_Saludables.triggered.connect(self.habitos)

        self.ui.action_Icono_Logros.triggered.connect(lambda: self.abrir_ventana('logros'))
        self.ui.action_Icono_Perfil_Usuario.triggered.connect(self.perfil)
        self.ui.action_Icono_Ranking.triggered.connect(lambda: self.abrir_ventana('ranking'))

        # Aquí puedes añadir más conexiones para nuevos botones/acciones
        # Ejemplo:
        # self.ui.nuevo_boton.clicked.connect(lambda: self.abrir_ventana('nueva_ventana'))

    def habitos(self):
        """Abrir ventana de hábitos"""
        try:
            controlador = HabitosController(self.usuario_autenticado.id_usuario)
            controlador.ventana_cerrada.connect(self.mostrar_vista)
            self.controladores['habitos'] = controlador
            self.vista.hide()
            controlador.vista.show()
        except Exception as e:
            self.mostrar_error(f"Error al abrir ventana de hábitos: {str(e)}")
            print(f"Error en habitos(): {e}")

    def perfil(self):
        """Abrir ventana de perfil de usuario"""
        try:
            controlador = PerfilUsuarioController(self.usuario_autenticado.id_usuario)
            controlador.ventana_cerrada.connect(self.mostrar_vista)
            self.controladores['perfil'] = controlador
            self.vista.hide()
            controlador.vista.show()
        except Exception as e:
            self.mostrar_error(f"Error al abrir ventana de perfil: {str(e)}")
            print(f"Error en perfil(): {e}")

    def abrir_ventana(self, tipo):
        """Abre una ventana secundaria según el tipo"""
        try:
            if tipo == 'habitos':
                controlador = HabitosController(self.usuario_autenticado.id_usuario)
                controlador.ventana_cerrada.connect(self.mostrar_vista)
            elif tipo == 'registro_habitos':
                controlador = registro_habitos(self)
                if hasattr(controlador, 'ventana_cerrada'):
                    controlador.ventana_cerrada.connect(self.mostrar_vista)
            elif tipo == 'comunidad':
                controlador = ComunidadController(self.usuario_autenticado.id_usuario)
                controlador.ventana_cerrada.connect(self.mostrar_vista)
            elif tipo == 'logros':
                controlador = LogrosController(self.usuario_autenticado.id_usuario)
                controlador.ventana_cerrada.connect(self.mostrar_vista)
            elif tipo == 'ranking':
                controlador = RankingController(self.usuario_autenticado.id_usuario)
                controlador.ventana_cerrada.connect(self.mostrar_vista)

            # Agrega aquí más tipos de ventanas según sea necesario
            # Ejemplo:
            # self.ui.nuevo_boton.clicked.connect(lambda: self.abrir_ventana('nueva_ventana'))

            if controlador and hasattr(controlador, 'vista'):
                self.controladores[tipo] = controlador
                self.vista.hide()
                controlador.vista.show()
            else:
                self.mostrar_error(f"Error al abrir ventana: {tipo}")

        except Exception as e:
            self.mostrar_error(f"Error al abrir ventana '{tipo}': {str(e)}")
            print(f"Error en abrir_ventana('{tipo}'): {e}")

    def cerrar_sesion(self):
        """Cierra la sesión y vuelve al login"""
        try:
            respuesta = QMessageBox.question(
                self.vista,
                "Cerrar Sesión",
                "¿Está seguro que desea cerrar sesión?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.vista.close()
                from controller.LoginController import LoginController
                login_controller = LoginController()
                login_controller.mostrar_vista()
        except Exception as e:
            self.mostrar_error(f"Error al cerrar sesión: {str(e)}")
            print(f"Error en cerrar_sesion: {e}")

    def cerrar_aplicacion(self):
        """Cierra completamente la aplicación"""
        try:
            respuesta = QMessageBox.question(
                self.vista,
                "Salir",
                "¿Está seguro que desea salir de la aplicación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.vista.close()
                QtWidgets.QApplication.quit()
        except Exception as e:
            self.mostrar_error(f"Error al cerrar aplicación: {str(e)}")
            print(f"Error en cerrar_aplicacion: {e}")

    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_exito(self, mensaje: str):
        """Muestra mensaje de éxito"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Éxito")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_vista(self):
        """Muestra la ventana del menú principal"""
        self.vista.show()

    def cerrar_vista(self):
        """Cierra la ventana del menú principal"""
        self.vista.close()

    def _cargar_habitos_del_dia(self):
        """Carga los hábitos del día en curso usando HabitoWidget"""
        self._limpiar_lista_habitos()

        try:
            fecha_hoy = date.today()
            habitos_con_estado = self._obtener_habitos_fecha(fecha_hoy)

            if not habitos_con_estado:
                self._mostrar_mensaje_sin_habitos()
                return

            self._agregar_habitos_a_lista(habitos_con_estado)
            logger.info(f"Cargados {len(habitos_con_estado)} hábitos del día {fecha_hoy}")

        except Exception as e:
            logger.error(f"Error cargando hábitos del día: {e}")
            self._mostrar_mensaje_error()

    def _limpiar_lista_habitos(self):
        """Limpiar la lista de hábitos"""
        try:
            self.ui.listHabitosDelDiaEnCurso.clear()
        except Exception as e:
            logger.error(f"Error limpiando lista de hábitos: {e}")

    def _obtener_nombre_categoria(self, id_categoria: Optional[int]) -> str:
        """Obtiene el nombre de la categoría por su ID"""
        try:
            if not id_categoria:
                return "Sin categoría"

            categoria = self.categorias_repository.obtener_categoria_por_id(id_categoria)
            return categoria.nombre if categoria else "Sin categoría"
        except Exception as e:
            logger.error(f"Error obteniendo categoría {id_categoria}: {e}")
            return "Sin categoría"

    def _obtener_habitos_fecha(self, fecha: date):
        """Obtener hábitos para la fecha especificada"""
        try:
            return self.habitos_repository.obtener_habitos_por_fecha(
                self.usuario_autenticado.id_usuario,
                fecha
            )
        except Exception as e:
            logger.error(f"Error obteniendo hábitos para fecha {fecha}: {e}")
            return []

    def _agregar_habitos_a_lista(self, habitos_con_estado):
        """Agregar hábitos a la lista visual"""
        for item_data in habitos_con_estado:
            try:
                habito = item_data['habito']
                estado = item_data['estado']

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
            self.ui.listHabitosDelDiaEnCurso.addItem(list_item)
            self.ui.listHabitosDelDiaEnCurso.setItemWidget(list_item, widget)
        except Exception as e:
            logger.error(f"Error agregando widget a lista: {e}")

    def _mostrar_mensaje_sin_habitos(self):
        """Mostrar mensaje cuando no hay hábitos para el día"""
        mensaje = self._crear_mensaje_informativo(
            "No hay hábitos programados para hoy 📅"
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

    def cerrar_sesion(self):
        """Cierra la sesión y vuelve al login"""
        try:
            respuesta = QMessageBox.question(
                self.vista,
                "Cerrar Sesión",
                "¿Está seguro que desea cerrar sesión?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.vista.close()
                from controller.LoginController import LoginController
                login_controller = LoginController()
                login_controller.mostrar_vista()
        except Exception as e:
            self.mostrar_error(f"Error al cerrar sesión: {str(e)}")
            print(f"Error en cerrar_sesion: {e}")

    def cerrar_aplicacion(self):
        """Cierra completamente la aplicación"""
        try:
            respuesta = QMessageBox.question(
                self.vista,
                "Salir",
                "¿Está seguro que desea salir de la aplicación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.vista.close()
                QtWidgets.QApplication.quit()
        except Exception as e:
            self.mostrar_error(f"Error al cerrar aplicación: {str(e)}")
            print(f"Error en cerrar_aplicacion: {e}")

    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_exito(self, mensaje: str):
        """Muestra mensaje de éxito"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Éxito")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_vista(self):
        """Muestra la ventana del menú principal"""
        self.vista.show()

    def cerrar_vista(self):
        """Cierra la ventana del menú principal"""
        self.vista.close()

    def _configurar_interfaz_usuario(self):
        """Configura la interfaz con los datos del usuario"""
        try:
            # Actualizar el saludo con el nombre del usuario
            nombre_usuario = getattr(self.usuario_autenticado, 'nombre_usuario', None) or \
                           getattr(self.usuario_autenticado, 'nombre', 'Usuario')

            self.ui.lblHolaUsuario.setText(f"¡Hola, @{nombre_usuario}!")

            # Cargar información del nivel del usuario
            self._cargar_informacion_nivel()

            logger.info(f"Interfaz configurada para usuario: {nombre_usuario}")

        except Exception as e:
            logger.error(f"Error configurando interfaz de usuario: {e}")
            # Usar un valor por defecto en caso de error
            self.ui.lblHolaUsuario.setText("¡Hola, @Usuario!")
            self._mostrar_informacion_nivel_por_defecto()

    def _cargar_informacion_nivel(self):
        """Carga y muestra la información del nivel del usuario"""
        try:
            # Obtener puntos totales del usuario
            puntos_totales = self.logro_repository.obtener_puntos_por_id_usuario(
                self.usuario_autenticado.id_usuario
            )

            # Actualizar nivel del usuario basado en sus puntos
            self.nivel_repository.actualizar_nivel_usuario_por_puntos(
                self.usuario_autenticado.id_usuario, puntos_totales
            )

            # Obtener nivel actual del usuario
            nivel_actual = self.nivel_repository.obtener_nivel_usuario(
                self.usuario_autenticado.id_usuario
            )

            # Obtener todos los niveles para calcular el próximo
            todos_los_niveles = self.nivel_repository.obtener_todos_niveles()

            # Actualizar la interfaz
            self._actualizar_etiquetas_nivel(puntos_totales, nivel_actual, todos_los_niveles)
            self._actualizar_barra_progreso_nivel(puntos_totales, nivel_actual, todos_los_niveles)

            logger.info(f"Información de nivel cargada: {puntos_totales} puntos, nivel: {nivel_actual.nombre if nivel_actual else 'Sin nivel'}")

        except Exception as e:
            logger.error(f"Error cargando información del nivel: {e}")
            self._mostrar_informacion_nivel_por_defecto()

    def _actualizar_etiquetas_nivel(self, puntos_totales: int, nivel_actual, todos_los_niveles):
        """Actualiza las etiquetas de nivel, puntos y descripción"""
        try:
            # Actualizar puntos totales
            self.ui.lblPuntos.setText(f"{puntos_totales} pts")

            # Actualizar nivel actual
            if nivel_actual:
                self.ui.lblNivel.setText(nivel_actual.nombre)
            else:
                self.ui.lblNivel.setText("Sin nivel")

            # Encontrar y mostrar próximo nivel
            proximo_nivel = self._obtener_proximo_nivel(puntos_totales, todos_los_niveles)
            if proximo_nivel:
                puntos_faltantes = proximo_nivel.puntos_requeridos - puntos_totales
                self.ui.lblDescripcion.setText(
                    f"Próximo nivel: {proximo_nivel.nombre} ({puntos_faltantes} pts faltantes)"
                )
            else:
                self.ui.lblDescripcion.setText("¡Has alcanzado el nivel máximo!")

        except Exception as e:
            logger.error(f"Error actualizando etiquetas de nivel: {e}")

    def _actualizar_barra_progreso_nivel(self, puntos_totales: int, nivel_actual, todos_los_niveles):
        """Actualiza la barra de progreso del nivel"""
        try:
            # Encontrar próximo nivel
            proximo_nivel = self._obtener_proximo_nivel(puntos_totales, todos_los_niveles)

            if proximo_nivel:
                # Calcular puntos del nivel anterior
                puntos_nivel_anterior = 0
                if nivel_actual:
                    puntos_nivel_anterior = nivel_actual.puntos_requeridos or 0

                # Calcular progreso
                puntos_en_rango = puntos_totales - puntos_nivel_anterior
                puntos_rango_total = proximo_nivel.puntos_requeridos - puntos_nivel_anterior

                if puntos_rango_total > 0:
                    progreso = int((puntos_en_rango / puntos_rango_total) * 100)
                    progreso = max(0, min(100, progreso))  # Asegurar que esté entre 0 y 100
                else:
                    progreso = 100

                self.ui.pbProgresoNivel.setValue(progreso)
            else:
                # Nivel máximo alcanzado
                self.ui.pbProgresoNivel.setValue(100)

        except Exception as e:
            logger.error(f"Error actualizando barra de progreso: {e}")
            self.ui.pbProgresoNivel.setValue(0)

    def _obtener_proximo_nivel(self, puntos_actuales: int, todos_los_niveles):
        """Obtiene el próximo nivel que puede alcanzar el usuario"""
        try:
            # Filtrar niveles que requieren más puntos que los actuales
            niveles_superiores = [
                nivel for nivel in todos_los_niveles
                if nivel.puntos_requeridos and nivel.puntos_requeridos > puntos_actuales
            ]

            # Ordenar por puntos requeridos y tomar el primero (el más cercano)
            if niveles_superiores:
                return min(niveles_superiores, key=lambda n: n.puntos_requeridos)

            return None
        except Exception as e:
            logger.error(f"Error obteniendo próximo nivel: {e}")
            return None

    def _mostrar_informacion_nivel_por_defecto(self):
        """Muestra información por defecto en caso de error"""
        try:
            self.ui.lblPuntos.setText("0 pts")
            self.ui.lblNivel.setText("Sin nivel")
            self.ui.lblDescripcion.setText("Completa hábitos para ganar puntos")
            self.ui.pbProgresoNivel.setValue(0)
        except Exception as e:
            logger.error(f"Error mostrando información por defecto: {e}")

    def _on_editar_habito(self, habito_id: int):
        """Manejar edición de hábito (renombrado para consistencia)"""
        try:
            logger.info(f"Iniciando edición para hábito {habito_id}")
            self.habitos()
        except Exception as e:
            logger.error(f"Error al editar hábito {habito_id}: {e}")
            self.mostrar_error(f"Error al editar hábito: {str(e)}")

    def _on_eliminar_habito(self, habito_id: int):
        """Manejar eliminación de hábito (renombrado para consistencia)"""
        try:
            respuesta = self._confirmar_eliminacion()
            if respuesta:
                if self.habitos_repository.eliminar_habito(habito_id):
                    self.mostrar_exito("Hábito eliminado exitosamente")
                    self._cargar_habitos_del_dia()  # Recargar la lista
                    logger.info(f"Hábito {habito_id} eliminado exitosamente")
                else:
                    self.mostrar_error("Error al eliminar el hábito")
        except Exception as e:
            logger.error(f"Error eliminando hábito {habito_id}: {e}")
            self.mostrar_error(f"Error eliminando hábito: {e}")

    def _on_cambiar_estado_habito(self, habito_id: int):
        """Cambiar estado del hábito (corregido para usar métodos correctos del repositorio)"""
        try:
            fecha_hoy = date.today()

            # Obtener el estado actual del hábito desde la base de datos
            seguimiento_repo = SeguimientoDiarioRepository()
            seguimiento_actual = seguimiento_repo.obtener_seguimiento_por_clave(
                self.usuario_autenticado.id_usuario, habito_id, fecha_hoy
            )

            # Determinar el nuevo estado
            if seguimiento_actual and seguimiento_actual.estado == "completado":
                nuevo_estado = "pendiente"
            else:
                nuevo_estado = "completado"

            # Crear o actualizar seguimiento en BD
            seguimiento_data = {
                'id_usuario': self.usuario_autenticado.id_usuario,
                'id_habito': habito_id,
                'fecha': fecha_hoy,
                'estado': nuevo_estado
            }

            seguimiento = seguimiento_repo.crear_o_actualizar_seguimiento(seguimiento_data)

            if seguimiento:
                # Recargar toda la lista para mostrar los cambios
                self._cargar_habitos_del_dia()
                logger.info(f"Estado del hábito {habito_id} cambiado a {nuevo_estado}")
            else:
                self.mostrar_error("Error al actualizar estado en la base de datos")

        except Exception as e:
            logger.error(f"Error cambiando estado hábito {habito_id}: {e}")
            self.mostrar_error(f"Error cambiando estado del hábito: {e}")

    def _actualizar_widget_estado(self, widget, nuevo_estado: str):
        """Actualizar el estado visual del widget"""
        try:
            widget.estado = nuevo_estado
            widget.actualizar_estilo_estado()
        except Exception as e:
            logger.error(f"Error actualizando widget: {e}")

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

    def actualizar_habitos_del_dia(self):
        """Metodo publico para refrescar la lista de hábitos del día"""
        logger.info("Actualizando lista de hábitos del día")
        self._cargar_habitos_del_dia()
