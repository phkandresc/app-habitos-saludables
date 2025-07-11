from PyQt6 import QtWidgets
from model.Usuario import Usuario
from view.windows.ventana_registro_usuario import Ui_Form

class UsuarioController(QtWidgets.QWidget,Ui_Form):
    def __init__(self, parent=None):
        super(UsuarioController,self).__init__(parent)
        self.setupUi(self)

        # Conectar señales a métodos
        self.btnRegistrar.clicked.connect(self.registrar_usuario)
        self.btnCancelar.clicked.connect(self.cancelar)

    def registrar_usuario(self):
        # Obtener datos de la interfaz
        nombre = self.txtNombre.text()
        apellido = self.txtUsuario.text()  # Cambia esto si el campo no es el apellido
        direccion = self.txtDireccion.text()
        contrasenia = self.txtContrasenia.text()
        fecha_nacimiento = self.txtFechaNacimiento.date().toPyDate()
        sexo = 'Hombre' if self.rbtnHombre.isChecked() else 'Mujer'
        ocupacion = self.txtOcupacion.text()
        peso = self.txtPeso.text()
        altura = self.txtAltura_3.text()

        # Crear una nueva instancia de Usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            direccion=direccion,
            contrasenia=contrasenia,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo
        )
        print(nuevo_usuario.nombre)


    def limpiar_campos(self):
        self.txtNombre.clear()
        self.txtUsuario.clear()
        self.txtDireccion.clear()
        self.txtContrasenia.clear()
        self.txtFechaNacimiento.clear()
        self.txtOcupacion.clear()
        self.txtPeso.clear()
        self.txtAltura_3.clear()
        self.rbtnHombre.setChecked(False)
        self.rbtnMujer.setChecked(False)

    def cancelar(self):
        self.close()  # Cierra la ventana actual
