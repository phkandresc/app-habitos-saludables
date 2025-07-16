import sys
from datetime import datetime, date
from typing import Optional
import logging

from PyQt6.QtCore import pyqtSignal, QObject, QDate
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QApplication, QLineEdit

from model.Usuario import Usuario
from repository.UsuarioRepository import UsuarioRepository
from repository.PerfilUsuarioRepository import PerfilUsuarioRepository
from view.windows.VentanaPerfilUsuario import Ui_ventanaRegistrarse

# Configurar logging
logger = logging.getLogger(__name__)


class PerfilUsuarioController(QObject):
    """Controlador para la gestión del perfil de usuario"""

    ventana_cerrada = pyqtSignal()
    perfil_actualizado = pyqtSignal(int)  # Señal para notificar actualizaciones
    error_ocurrido = pyqtSignal(str)  # Señal para notificar errores

    def __init__(self, id_usuario: int, parent_controller=None):
        super().__init__()

        if not self._validar_id_usuario(id_usuario):
            raise ValueError("ID de usuario inválido")

        self.id_usuario = id_usuario
        self.parent_controller = parent_controller
        self.usuario_actual = None

        # Inicialización de vista
        self.vista = QMainWindow()
        self.ui = Ui_ventanaRegistrarse()
        self.ui.setupUi(self.vista)

        # Inicialización de repositorios
        self.usuario_repository = UsuarioRepository()
        self.perfil_repository = PerfilUsuarioRepository()

        self._setup_controller()

    def _validar_id_usuario(self, id_usuario: int) -> bool:
        """Validar que el ID de usuario sea válido"""
        return isinstance(id_usuario, int) and id_usuario > 0

    def _setup_controller(self):
        """Configuración inicial del controlador"""
        try:
            self._configurar_interfaz()
            self._conectar_eventos()
            self._cargar_datos_usuario()
            logger.info(f"Controlador de perfil inicializado para usuario {self.id_usuario}")
        except Exception as e:
            logger.error(f"Error inicializando controlador de perfil: {e}")
            self.error_ocurrido.emit(f"Error al inicializar perfil: {e}")

    def _configurar_interfaz(self):
        """Configurar elementos específicos de la interfaz"""
        try:
            # Configurar título de ventana
            self.vista.setWindowTitle("Editar Perfil de Usuario")

            # Configurar campos de contraseña para ocultar por defecto
            if hasattr(self.ui, 'txtPassword'):
                self.ui.txtPassword.setEchoMode(QLineEdit.EchoMode.Password)

            if hasattr(self.ui, 'txtConfirmarPassword'):
                self.ui.txtConfirmarPassword.setEchoMode(QLineEdit.EchoMode.Password)

            # Configurar rangos para los spinboxes
            if hasattr(self.ui, 'dsbPeso'):
                self.ui.dsbPeso.setRange(0.0, 500.0)
                self.ui.dsbPeso.setDecimals(1)

            if hasattr(self.ui, 'dsbAltura'):
                self.ui.dsbAltura.setRange(0.0, 3.0)
                self.ui.dsbAltura.setDecimals(2)

            # Configurar fecha mínima y máxima para el date edit
            if hasattr(self.ui, 'dateNacimiento'):
                from PyQt6.QtCore import QDate
                today = QDate.currentDate()
                min_date = QDate(1900, 1, 1)
                max_date = today.addYears(-1)  # Al menos 1 año de edad
                self.ui.dateNacimiento.setDateRange(min_date, max_date)

            logger.info("Interfaz configurada correctamente")

        except Exception as e:
            logger.error(f"Error configurando interfaz: {e}")

    def _conectar_eventos(self):
        """Conectar eventos de la vista"""
        try:
            self.vista.closeEvent = self._on_close

            # Conectar botones principales
            if hasattr(self.ui, 'btnRegistrarse'):
                self.ui.btnRegistrarse.clicked.connect(self._guardar_perfil)
                logger.info("Botón 'Editar' (btnRegistrarse) conectado")

            if hasattr(self.ui, 'pushButton'):
                self.ui.pushButton.clicked.connect(self._cancelar_edicion)
                logger.info("Botón 'Cancelar' (pushButton) conectado")

            # Conectar checkbox para mostrar/ocultar contraseña
            if hasattr(self.ui, 'cbxMostrarPassword'):
                self.ui.cbxMostrarPassword.toggled.connect(self._toggle_password_visibility)
                logger.info("Checkbox mostrar contraseña conectado")

            logger.info("Eventos conectados exitosamente")

        except Exception as e:
            logger.error(f"Error conectando eventos: {e}")
            raise

    def _cancelar_edicion(self):
        """Cancelar la edición del perfil y cerrar la ventana"""
        try:
            logger.info("Cancelando edición del perfil")
            self._cerrar_ventana()
        except Exception as e:
            logger.error(f"Error cancelando edición: {e}")

    def _cerrar_ventana(self):
        """Cerrar la ventana y emitir señal de cierre"""
        try:
            logger.info(f"Cerrando ventana de perfil para usuario {self.id_usuario}")
            self.ventana_cerrada.emit()
            self.vista.close()
        except Exception as e:
            logger.error(f"Error cerrando ventana: {e}")

    def _toggle_password_visibility(self, checked: bool):
        """Mostrar u ocultar la contraseña"""
        try:
            echo_mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password

            if hasattr(self.ui, 'txtPassword'):
                self.ui.txtPassword.setEchoMode(echo_mode)

            if hasattr(self.ui, 'txtConfirmarPassword'):
                self.ui.txtConfirmarPassword.setEchoMode(echo_mode)

            logger.info(f"Visibilidad de contraseña: {'visible' if checked else 'oculta'}")
        except Exception as e:
            logger.error(f"Error cambiando visibilidad de contraseña: {e}")

    def _cargar_datos_usuario(self):
        """Cargar datos del usuario y su perfil"""
        try:
            self.usuario_actual = self._obtener_usuario()

            if not self.usuario_actual:
                self._mostrar_error("No se pudo cargar la información del usuario")
                return

            self._llenar_campos_usuario()
            logger.info(f"Datos del usuario {self.id_usuario} cargados exitosamente")

        except Exception as e:
            logger.error(f"Error cargando datos del usuario {self.id_usuario}: {e}")
            self._mostrar_error(f"Error cargando datos del usuario: {e}")
            self.error_ocurrido.emit(f"Error cargando datos: {e}")

    def _obtener_usuario(self) -> Optional[Usuario]:
        """Obtener datos completos del usuario con su perfil usando ambos repositorios"""
        try:
            # Obtener el usuario usando UsuarioRepository
            usuario = self.usuario_repository.obtener_usuario_por_id(self.id_usuario)

            if not usuario:
                logger.error(f"Usuario {self.id_usuario} no encontrado")
                return None

            # Obtener el perfil usando PerfilUsuarioRepository
            perfil = self.perfil_repository.obtener_perfil_por_usuario(self.id_usuario)

            # Asignar el perfil al usuario si existe
            if perfil:
                usuario.perfil = perfil
                logger.info(f"Perfil cargado para usuario {self.id_usuario}")
            else:
                logger.info(f"No se encontró perfil para usuario {self.id_usuario}")
                usuario.perfil = None

            return usuario

        except Exception as e:
            logger.error(f"Error obteniendo usuario {self.id_usuario}: {e}")
            return None

    def _llenar_campos_usuario(self):
        """Llenar los campos de la interfaz con los datos del usuario"""
        if not self.usuario_actual:
            logger.warning("No hay usuario actual para llenar campos")
            return

        try:
            logger.info(f"Llenando campos para usuario: {self.usuario_actual.nombre_usuario}")

            # Llenar información de inicio de sesión
            self._llenar_campo_texto('txtNombre', self.usuario_actual.nombre, "nombre")
            self._llenar_campo_texto('txtApellido', self.usuario_actual.apellido, "apellido")
            self._llenar_campo_texto('txtNombreUsuario', self.usuario_actual.nombre_usuario, "nombre_usuario")
            self._llenar_campo_texto('txtCorreo', self.usuario_actual.correo_electronico, "correo_electronico")
            self._llenar_campo_texto('txtPassword', self.usuario_actual.contrasenia, "contrasenia")
            self._llenar_campo_texto('txtConfirmarPassword', self.usuario_actual.contrasenia, "confirmar_contrasenia")

            # Llenar información personal
            self._seleccionar_sexo(self.usuario_actual.sexo)
            self._establecer_fecha_nacimiento(self.usuario_actual.fecha_nacimiento)

            # Llenar información del perfil si existe
            if hasattr(self.usuario_actual, 'perfil') and self.usuario_actual.perfil:
                logger.info("Llenando campos del perfil")
                self._llenar_campos_perfil()
            else:
                logger.info("Usuario sin perfil - usando valores por defecto")
                self._configurar_valores_perfil_por_defecto()

            logger.info("Campos llenados exitosamente")

        except Exception as e:
            logger.error(f"Error llenando campos de la interfaz: {e}", exc_info=True)

    def _llenar_campo_texto(self, nombre_campo: str, valor, descripcion: str):
        """Llenar un campo de texto específico con logging detallado"""
        try:
            if hasattr(self.ui, nombre_campo):
                campo = getattr(self.ui, nombre_campo)
                if valor:
                    campo.setText(str(valor))
                    logger.debug(f"Campo {descripcion} llenado con: {valor}")
                else:
                    campo.setText("")
                    logger.debug(f"Campo {descripcion} vacío")
            else:
                logger.warning(f"Campo {nombre_campo} no encontrado en UI")
        except Exception as e:
            logger.error(f"Error llenando campo {nombre_campo}: {e}")

    def _llenar_campos_perfil(self):
        """Llenar campos específicos del perfil"""
        perfil = self.usuario_actual.perfil

        try:
            logger.debug(f"Perfil - Peso: {getattr(perfil, 'peso', 'N/A')}, Altura: {getattr(perfil, 'altura', 'N/A')}, Ocupación: {getattr(perfil, 'ocupacion', 'N/A')}")

            # Llenar peso
            if hasattr(perfil, 'peso') and perfil.peso and hasattr(self.ui, 'dsbPeso'):
                self.ui.dsbPeso.setValue(float(perfil.peso))
                logger.debug(f"Peso establecido: {perfil.peso}")

            # Llenar altura
            if hasattr(perfil, 'altura') and perfil.altura and hasattr(self.ui, 'dsbAltura'):
                self.ui.dsbAltura.setValue(float(perfil.altura))
                logger.debug(f"Altura establecida: {perfil.altura}")

            # Llenar ocupación
            ocupacion = getattr(perfil, 'ocupacion', '')
            self._llenar_campo_texto('txtOcupacion', ocupacion, "ocupacion")

        except Exception as e:
            logger.error(f"Error llenando campos del perfil: {e}", exc_info=True)

    def _configurar_valores_perfil_por_defecto(self):
        """Configurar valores por defecto cuando no hay perfil"""
        try:
            if hasattr(self.ui, 'dsbPeso'):
                self.ui.dsbPeso.setValue(0.0)

            if hasattr(self.ui, 'dsbAltura'):
                self.ui.dsbAltura.setValue(0.0)

            self._llenar_campo_texto('txtOcupacion', '', "ocupacion")

            logger.debug("Valores por defecto del perfil configurados")

        except Exception as e:
            logger.error(f"Error configurando valores por defecto: {e}")

    def _seleccionar_sexo(self, sexo: str):
        """Seleccionar sexo en el combo box"""
        try:
            if hasattr(self.ui, 'cmbSexo') and sexo:
                combo = self.ui.cmbSexo

                # Mapear valores de la BD a los índices del combo
                if sexo.upper() in ['M', 'MASCULINO', 'HOMBRE']:
                    index = 0  # Hombre
                elif sexo.upper() in ['F', 'FEMENINO', 'MUJER']:
                    index = 1  # Mujer
                else:
                    index = 0  # Por defecto Hombre

                combo.setCurrentIndex(index)
                logger.debug(f"Sexo '{sexo}' seleccionado (índice {index})")
            else:
                logger.warning("Campo cmbSexo no encontrado o sexo vacío")
        except Exception as e:
            logger.error(f"Error seleccionando sexo: {e}")

    def _establecer_fecha_nacimiento(self, fecha_nacimiento):
        """Establecer fecha de nacimiento en el widget de fecha"""
        try:
            if hasattr(self.ui, 'dateNacimiento') and fecha_nacimiento:
                date_edit = self.ui.dateNacimiento

                if isinstance(fecha_nacimiento, datetime):
                    qdate = QDate(fecha_nacimiento.year, fecha_nacimiento.month, fecha_nacimiento.day)
                elif isinstance(fecha_nacimiento, date):
                    qdate = QDate(fecha_nacimiento.year, fecha_nacimiento.month, fecha_nacimiento.day)
                else:
                    logger.warning(f"Formato de fecha inválido: {type(fecha_nacimiento)} - {fecha_nacimiento}")
                    return

                date_edit.setDate(qdate)
                logger.debug(f"Fecha de nacimiento establecida: {fecha_nacimiento}")
            else:
                logger.warning("Campo dateNacimiento no encontrado o fecha vacía")
        except Exception as e:
            logger.error(f"Error estableciendo fecha de nacimiento: {e}")

    def _guardar_perfil(self):
        """Guardar cambios en el perfil del usuario"""
        try:
            logger.info("Iniciando proceso de guardado del perfil")

            datos = self._recopilar_datos_formulario()

            if not self._validar_datos(datos):
                return

            # Usar el repositorio para actualizar
            usuario_actualizado = self.usuario_repository.actualizar_usuario(
                self.id_usuario, datos
            )

            if usuario_actualizado:
                # Recargar el usuario completo con su perfil
                self.usuario_actual = self._obtener_usuario()
                self._mostrar_informacion("Perfil actualizado exitosamente")
                self.perfil_actualizado.emit(self.id_usuario)
                logger.info(f"Perfil del usuario {self.id_usuario} actualizado exitosamente")
            else:
                self._mostrar_error("Error al actualizar el perfil")

        except Exception as e:
            logger.error(f"Error guardando perfil del usuario {self.id_usuario}: {e}")
            self._mostrar_error(f"Error guardando perfil: {e}")
            self.error_ocurrido.emit(f"Error guardando perfil: {e}")

    def _recopilar_datos_formulario(self) -> dict:
        """Recopilar datos del formulario usando los nombres correctos de los campos"""
        datos = {
            'usuario': {},
            'perfil': {}
        }

        try:
            # Datos del usuario - información de inicio de sesión
            if hasattr(self.ui, 'txtNombre'):
                nombre = self.ui.txtNombre.text().strip()
                if nombre:
                    datos['usuario']['nombre'] = nombre

            if hasattr(self.ui, 'txtApellido'):
                apellido = self.ui.txtApellido.text().strip()
                if apellido:
                    datos['usuario']['apellido'] = apellido

            if hasattr(self.ui, 'txtNombreUsuario'):
                nombre_usuario = self.ui.txtNombreUsuario.text().strip()
                if nombre_usuario:
                    datos['usuario']['nombre_usuario'] = nombre_usuario

            if hasattr(self.ui, 'txtCorreo'):
                correo = self.ui.txtCorreo.text().strip()
                if correo:
                    datos['usuario']['correo_electronico'] = correo

            if hasattr(self.ui, 'txtPassword'):
                password = self.ui.txtPassword.text().strip()
                if password:
                    datos['usuario']['contrasenia'] = password

            # Sexo del usuario
            if hasattr(self.ui, 'cmbSexo'):
                sexo_index = self.ui.cmbSexo.currentIndex()
                datos['usuario']['sexo'] = 'M' if sexo_index == 0 else 'F'

            # Fecha de nacimiento del usuario
            if hasattr(self.ui, 'dateNacimiento'):
                qdate = self.ui.dateNacimiento.date()
                fecha_nacimiento = date(qdate.year(), qdate.month(), qdate.day())
                datos['usuario']['fecha_nacimiento'] = fecha_nacimiento

            # Datos del perfil
            if hasattr(self.ui, 'dsbPeso'):
                peso = self.ui.dsbPeso.value()
                if peso > 0:
                    datos['perfil']['peso'] = peso

            if hasattr(self.ui, 'dsbAltura'):
                altura = self.ui.dsbAltura.value()
                if altura > 0:
                    datos['perfil']['altura'] = altura

            if hasattr(self.ui, 'txtOcupacion'):
                ocupacion = self.ui.txtOcupacion.text().strip()
                if ocupacion:
                    datos['perfil']['ocupacion'] = ocupacion

            logger.debug(f"Datos recopilados: Usuario={list(datos['usuario'].keys())}, Perfil={list(datos['perfil'].keys())}")

        except (ValueError, TypeError) as e:
            logger.error(f"Error recopilando datos del formulario: {e}")
            raise

        return datos

    def _validar_datos(self, datos: dict) -> bool:
        """Validar datos antes de guardar"""
        try:
            # Validar datos obligatorios del usuario
            if not datos.get('usuario', {}).get('nombre'):
                self._mostrar_error("El nombre es obligatorio")
                return False

            if not datos.get('usuario', {}).get('apellido'):
                self._mostrar_error("El apellido es obligatorio")
                return False

            if not datos.get('usuario', {}).get('nombre_usuario'):
                self._mostrar_error("El nombre de usuario es obligatorio")
                return False

            # Validar correo electrónico
            correo = datos.get('usuario', {}).get('correo_electronico', '')
            if correo and not self._validar_email(correo):
                self._mostrar_error("Formato de correo electrónico inválido")
                return False

            # Validar contraseñas coincidentes
            if not self._validar_contrasenas():
                return False

            # Validar datos del perfil
            peso = datos.get('perfil', {}).get('peso')
            if peso is not None and (peso <= 0 or peso > 500):
                self._mostrar_error("El peso debe estar entre 1 y 500 kg")
                return False

            altura = datos.get('perfil', {}).get('altura')
            if altura is not None and (altura <= 0 or altura > 3):
                self._mostrar_error("La altura debe estar entre 0.01 y 3 metros")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validando datos: {e}")
            return False

    def _validar_contrasenas(self) -> bool:
        """Validar que las contraseñas coincidan"""
        try:
            if hasattr(self.ui, 'txtPassword') and hasattr(self.ui, 'txtConfirmarPassword'):
                password = self.ui.txtPassword.text()
                confirm_password = self.ui.txtConfirmarPassword.text()

                if password != confirm_password:
                    self._mostrar_error("Las contraseñas no coinciden")
                    return False

                if len(password) < 6:
                    self._mostrar_error("La contraseña debe tener al menos 6 caracteres")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validando contraseñas: {e}")
            return False

    def _validar_email(self, email: str) -> bool:
        """Validar formato de email básico"""
        import re
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None

    def _mostrar_error(self, mensaje: str):
        """Mostrar mensaje de error al usuario"""
        QMessageBox.critical(self.vista, "Error", mensaje)

    def _mostrar_informacion(self, mensaje: str):
        """Mostrar mensaje de información al usuario"""
        QMessageBox.information(self.vista, "Información", mensaje)

    def _on_close(self, event):
        """Manejar cierre de ventana"""
        try:
            logger.info(f"Ventana de perfil cerrada por el usuario {self.id_usuario}")
            self.ventana_cerrada.emit()
            event.accept()
        except Exception as e:
            logger.error(f"Error en evento de cierre: {e}")
            event.accept()

    # Métodos públicos para la interfaz
    def mostrar(self):
        """Mostrar la ventana"""
        try:
            self.vista.show()
            logger.info("Ventana de perfil mostrada")
        except Exception as e:
            logger.error(f"Error mostrando ventana de perfil: {e}")

    def ocultar(self):
        """Ocultar la ventana y emitir señal de cierre"""
        try:
            logger.info("Ocultando ventana de perfil")
            self._cerrar_ventana()
        except Exception as e:
            logger.error(f"Error ocultando ventana de perfil: {e}")

    def obtener_usuario_actual(self) -> Optional[Usuario]:
        """Obtener el usuario actualmente cargado"""
        return self.usuario_actual

    def recargar_datos(self):
        """Recargar datos del usuario"""
        logger.info("Recargando datos del usuario")
        self._cargar_datos_usuario()


if __name__ == '__main__':
    # Ejemplo de uso del controlador
    try:
        app = QApplication(sys.argv)
        controller = PerfilUsuarioController(id_usuario=14)
        controller.mostrar()

        # Ejecutar el bucle de eventos de la aplicación
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Error al iniciar controlador de perfil: {e}")
        QMessageBox.critical(None, "Error", f"Error al iniciar la aplicación: {e}")
        sys.exit(1)
