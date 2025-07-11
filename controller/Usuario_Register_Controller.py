from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox
from PyQt6.uic.properties import QtCore

from model.Usuario import Usuario
from repository.UsuarioRepository import UsuarioRepository
from db.connection import get_db_session
from view.windows.RegistroView import Ui_Form

class UsuarioRegisterController:
    def __init__(self, parent_controller=None):
        self.db_session = get_db_session()
        self.usuario_repository = UsuarioRepository(self.db_session)
        self.vista = QtWidgets.QWidget()
        self.ui = Ui_Form()
        self.parent_controller = parent_controller  # Guardamos la referencia
        self.ui.setupUi(self.vista)
        # Configurar el evento de cierre
        #self.vista.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, False)
        #self.vista.closeEvent = self.closeEvent  # Sobrescribir el evento de cierre
        self.conectar_eventos()


    def conectar_eventos(self):
        """Conecta los eventos de la interfaz con sus métodos"""
        self.ui.btnRegistrar.clicked.connect(self.registrar_usuario)
        self.ui.btnCancelar.clicked.connect(self.cancelar_registro)

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        self.cancelar_registro()
        event.accept()

    def registrar_usuario(self):
        """Maneja el proceso de registro de usuario"""
        # Obtiene los datos ingresados por el usuario
        nombre = self.ui.txtNombre.text().strip()
        apellido = self.ui.txtUsuario.text().strip()  # Cambia esto si el campo no es el apellido
        correo = self.ui.txtCorreo.text().strip()
        contrasenia = self.ui.txtContrasenia.text().strip()
        confirmar_contrasenia = self.ui.txtConfirmarContrasenia.text().strip()
        fecha_nacimiento = self.ui.txtFechaNacimiento.date().toPyDate()
        sexo = 'Hombre' if self.ui.rbtnHombre.isChecked() else 'Mujer'
        ocupacion = self.ui.txtOcupacion.text().strip()
        peso = self.ui.txtPeso.text().strip()
        altura = self.ui.txtAltura.text().strip()

        try:
            # Validar campos vacíos
            if not all([nombre, apellido, correo, contrasenia, confirmar_contrasenia, ocupacion, peso, altura]):
                self.mostrar_error("Todos los campos son obligatorios")
                return

            # Validar que las contraseñas coincidan
            if contrasenia != confirmar_contrasenia:
                self.mostrar_error("Las contraseñas no coinciden")
                return

            # Crear una nueva instancia de Usuario
            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                correo = correo,
                contrasenia=contrasenia,
                fecha_nacimiento=fecha_nacimiento,
                sexo=sexo,
                ocupacion=ocupacion,
                peso=peso,
                altura=altura
            )

            # Guardar en la base de datos
            self.usuario_repository.crear_usuario(nuevo_usuario)
            QMessageBox.information(self.vista, "Éxito", "Usuario registrado exitosamente.")
            self.limpiar_campos()

        except Exception as e:
            self.mostrar_error(f"Error al registrar usuario: {str(e)}")

    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def limpiar_campos(self):
        """Limpia los campos del formulario"""
        self.ui.txtNombre.clear()
        self.ui.txtUsuario.clear()
        self.ui.txtContrasenia.clear()
        self.ui.txtConfirmarContrasenia.clear()
        self.ui.txtFechaNacimiento.clear()
        self.ui.txtOcupacion.clear()
        self.ui.txtPeso.clear()
        self.ui.txtAltura.clear()
        self.ui.rbtnHombre.setChecked(False)
        self.ui.rbtnMujer.setChecked(False)

    def cancelar_registro(self):
        """Cierra la ventana de registro"""
        self.vista.close()
        if self.parent_controller:  # Si tenemos referencia al padre
            self.parent_controller.vista.show()  # Mostramos su vista directamente

    def cerrar_sesion(self):
        """Cierra la sesión de la base de datos"""
        if self.db_session:
            self.db_session.close()