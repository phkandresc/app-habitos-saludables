from datetime import datetime

from PyQt6.QtWidgets import QMessageBox, QMainWindow

from model import Usuario
from view.windows.ventana_perfil_usuario import Ui_Form

class perfil_usuario:
    def __init__(self, parent_controller=None):
        #print("Ususario que acaba de ingresar en Perfil: ",usuario_autenticado.nombre)
        #self.usuario = usuario_autenticado
        self.vista = QMainWindow()
        self.ui = Ui_Form()
        self.parent_controller = parent_controller  # Guardamos la referencia
        self.ui.setupUi(self.vista)
        #self.cargar_datos_usuario()
        self.conectar_eventos()



    def cargar_datos_usuario(self):
        """Carga los datos completos del usuario en la interfaz"""
        if self.usuario:
            print(f"Cargando datos para: {self.usuario.nombre}")

            # Datos básicos del usuario
            self.ui.txtNombre.setText(self.usuario.nombre)
            self.ui.txtApellido.setText(self.usuario.apellido)
            self.ui.txtNombreUsuario.setText(self.usuario.nombre_usuario)

            # Verificar y cargar datos del perfil
            if self.usuario.perfil:
                perfil = self.usuario.perfil
                self.ui.txtOcupacion.setText(perfil.ocupacion)
                self.ui.txtPeso.setText(f"{perfil.peso:.2f}" if perfil.peso else "N/A")
                self.ui.txtAltura.setText(f"{perfil.altura:.2f}" if perfil.altura else "N/A")

                # Calcular edad
                if self.usuario.fecha_nacimiento:
                    edad = datetime.now().year - self.usuario.fecha_nacimiento.year
                    self.ui.txtEdad.setText(str(edad))
            else:
                print("El usuario no tiene perfil asociado")
                self.limpiar_campos_perfil()

    def limpiar_campos_perfil(self):
        """Limpia los campos del perfil"""
        self.ui.txtOcupacion.setText("")
        self.ui.txtPeso.setText("")
        self.ui.txtAltura.setText("")
        self.ui.txtEdad.setText("")

    def conectar_eventos(self):
        self.ui.btnRegresar.clicked.connect(self.regresar)

    def regresar(self):
        self.vista.close()
        if self.parent_controller:  # Si tenemos referencia al padre
            self.parent_controller.vista.show()  # Mostramos su vista directamente

    """def cargar_datos_usuario(self):
        #Carga los datos del usuario en los campos del formulario
        if self.usuario:
            self.ui.txtNombre.setText(self.usuario.nombre or "")
            self.ui.txtApellido.setText(self.usuario.apellido or "")
            self.ui.txtNombreUsuario.setText(self.usuario.nombre_usuario or "")

            # Verificar si existe perfil y cargar esos datos
            if hasattr(self.usuario, 'perfil') and self.usuario.perfil:
                perfil = self.usuario.perfil
                self.ui.txtOcupacion.setText(perfil.ocupacion or "")
                self.ui.txtPeso.setText(str(perfil.peso) if perfil.peso else "")
                self.ui.txtAltura.setText(str(perfil.altura) if perfil.altura else "")

                # Calcular edad si hay fecha de nacimiento
                if self.usuario.fecha_nacimiento:
                    edad = datetime.now().year - self.usuario.fecha_nacimiento.year
                    self.ui.txtEdad.setText(str(edad))
            else:
                # Limpiar campos si no hay perfil
                self.ui.txtOcupacion.setText("")
                self.ui.txtPeso.setText("")
                self.ui.txtAltura.setText("")
                self.ui.txtEdad.setText("")"""