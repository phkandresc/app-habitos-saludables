from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox
from repository.UsuarioRepository import UsuarioRepository
from view.windows.RegistroView import Ui_Form

class UsuarioRegisterController:
    def __init__(self):
        self.usuario_repository = UsuarioRepository()
        self.vista = QtWidgets.QWidget()
        self.ui = Ui_Form()
        self.ui.setupUi(self.vista)
        self.conectar_eventos()

    def conectar_eventos(self):
        """Conecta los eventos de la interfaz con sus métodos"""
        self.ui.btnRegistrar.clicked.connect(self.registrar_usuario)
        self.ui.btnCancelar.clicked.connect(self.cancelar_registro)

    def registrar_usuario(self):
        """Maneja el proceso de registro de usuario"""
        # Obtiene los datos ingresados por el usuario
        nombre = self.ui.txtNombre.text().strip()
        apellido = self.ui.txtUsuario.text().strip()  # Cambia esto si el campo no es el apellido
        direccion = self.ui.txtCorreo.text().strip()  # Asumiendo que txtCorreo es dirección
        contrasenia = self.ui.txtContrasenia.text().strip()
        confirmar_contrasenia = self.ui.txtConfirmarContrasenia.text().strip()
        fecha_nacimiento = self.ui.txtFechaNacimiento.date().toPyDate()
        sexo = 'H' if self.ui.rbtnHombre.isChecked() else 'M'  # Ajustado a 2 caracteres según el modelo
        nombre_usuario = self.ui.txtOcupacion.text().strip()  # Asumiendo que txtOcupacion es nombre_usuario

        try:
            # Validar campos vacíos
            if not all([nombre, apellido, direccion, contrasenia, confirmar_contrasenia, nombre_usuario]):
                self.mostrar_error("Todos los campos son obligatorios")
                return

            # Validar que las contraseñas coincidan
            if contrasenia != confirmar_contrasenia:
                self.mostrar_error("Las contraseñas no coinciden")
                return

            # Crear diccionario con los datos del usuario
            usuario_data = {
                'nombre': nombre,
                'apellido': apellido,
                'direccion': direccion,
                'contrasenia': contrasenia,
                'fecha_nacimiento': fecha_nacimiento,
                'sexo': sexo,
                'nombre_usuario': nombre_usuario
            }

            # Guardar en la base de datos
            nuevo_usuario = self.usuario_repository.crear_usuario(usuario_data)
            if nuevo_usuario:
                QMessageBox.information(self.vista, "Éxito", "Usuario registrado exitosamente.")
                self.limpiar_campos()
            else:
                self.mostrar_error("Error al registrar usuario en la base de datos")

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
        # Removidos los campos que no existen en el modelo Usuario
        self.ui.rbtnHombre.setChecked(False)
        self.ui.rbtnMujer.setChecked(False)

    def cancelar_registro(self):
        """Cierra la ventana de registro"""
        self.vista.close()

    def cerrar_sesion(self):
        """Cierra la sesión de la base de datos"""
        # El DatabaseConnection maneja las sesiones automáticamente
        pass
