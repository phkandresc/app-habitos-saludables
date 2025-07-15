from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from controller.Registro_Habitos_Controler import registro_habitos
from controller.RegistroComunidadController import nueva_comunidad
from controller.HabitosController import HabitosController
from view.windows.VentanaMenuPrincipal import Ui_MainWindow
from model.Usuario import Usuario

class MenuPrincipalController:
    def __init__(self, usuario_autenticado: Usuario):
        self.vista = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.vista)
        # Usuario autenticado
        self.usuario_autenticado = usuario_autenticado

        # Diccionario para gestionar controladores secundarios
        self.controladores = {}

        self._conectar_eventos()

    def _conectar_eventos(self):
        """Conecta los eventos de la interfaz con sus métodos"""
        self.ui.actionCerrar_Sesion.triggered.connect(self.cerrar_sesion)
        self.ui.action_Icono_Cerrar_Sesion.triggered.connect(self.cerrar_sesion)
        self.ui.action_Icono_Comunidad.triggered.connect(lambda: self.abrir_ventana('comunidad'))
        self.ui.pushButton.clicked.connect(lambda: self.abrir_ventana('registro_habitos'))
        self.ui.action_item_Habitos_Saludables.triggered.connect(lambda: self.abrir_ventana('habitos'))

        # Aquí puedes añadir más conexiones para nuevos botones/acciones
        # Ejemplo:
        # self.ui.nuevo_boton.clicked.connect(lambda: self.abrir_ventana('nueva_ventana'))

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
                controlador = nueva_comunidad(self)
            # Agrega aquí más tipos de ventanas según sea necesario
            else:
                self.mostrar_error(f"Tipo de ventana desconocido: {tipo}")
                return

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