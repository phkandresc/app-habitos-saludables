from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from controller.Registro_Habitos_Controler import registro_habitos
from controller.RegistroComunidadController import nueva_comunidad
from controller.HabitosController import HabitosController
from view.windows.ventana_Menu_Principal import Ui_MainWindow


class MenuPrincipalController:
    def __init__(self):
        self.vista = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.vista)

        # Inicializar controladores como None
        self.habitos_controller = None
        self.comunidad_controller = None

        self.conectar_eventos()

    def conectar_eventos(self):
        """Conecta los eventos de la interfaz con sus métodos"""
        self.ui.actionCerrar_Sesion.triggered.connect(self.cerrar_sesion)
        self.ui.action_Icono_Cerrar_Sesion.triggered.connect(self.cerrar_sesion)
        self.ui.action_Icono_Comunidad.triggered.connect(self.comunidad)
        self.ui.pushButton.clicked.connect(self.nuevo_habito)
        self.ui.action_item_Habitos_Saludables.triggered.connect(self.habitos)

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
                # Aquí podrías volver al LoginController si es necesario
                from controller.Login_Controller import LoginController
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

    def nuevo_habito(self):
        """Abre la ventana de registro de hábitos"""
        try:
            self.habitos_controller = registro_habitos(self)
            if self.habitos_controller and hasattr(self.habitos_controller, 'vista'):
                self.vista.close()
                self.habitos_controller.vista.show()
            else:
                self.mostrar_error("Error al abrir ventana de hábitos")

        except Exception as e:
            self.mostrar_error(f"Error al abrir registro de hábitos: {str(e)}")
            print(f"Error en nuevo_habito: {e}")

    def comunidad(self):
        """Abre la ventana de comunidades"""
        try:
            self.comunidad_controller = nueva_comunidad(self)
            if self.comunidad_controller and hasattr(self.comunidad_controller, 'vista'):
                self.vista.close()
                self.comunidad_controller.vista.show()
            else:
                self.mostrar_error("Error al abrir ventana de comunidad")

        except Exception as e:
            self.mostrar_error(f"Error al abrir comunidades: {str(e)}")
            print(f"Error en comunidad: {e}")

    def habitos(self):
        """Abre la ventana de gestión de hábitos"""
        print("VENTANA DE HABITOS")

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

    def volver_al_menu(self):
        """Método para que otros controladores vuelvan al menú"""
        try:
            self.mostrar_vista()
        except Exception as e:
            self.mostrar_error(f"Error al volver al menú: {str(e)}")
            print(f"Error en volver_al_menu: {e}")