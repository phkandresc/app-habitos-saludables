from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from datetime import datetime
from repository.HabitosRepository import HabitosRepository
from view.windows.VentanaNuevoHabito import Ui_ventanaRegistrarHabito
from model.Categorias import Categoria
from db.Connection import DatabaseConnection
from sqlalchemy.orm import sessionmaker


class RegistroHabitosController:
    def __init__(self, parent_controller=None):
        self.vista = QMainWindow()
        self.ui = Ui_Form()
        self.parent_controller = parent_controller
        self.ui.setupUi(self.vista)

        # Inicializar base de datos y repositorio
        self.db = DatabaseConnection()
        self.Session = sessionmaker(bind=self.db.engine)
        self.habitos_repository = HabitosRepository()

        self.cargar_categorias()
        self.conectar_eventos()

    def cargar_categorias(self):
        """Cargar categorías desde la base de datos"""
        session = self.Session()
        try:
            categorias = session.query(Categoria.nombre).order_by(Categoria.nombre).all()
            nombres = [cat[0] for cat in categorias] if categorias else [
                "Planificar comidas balanceadas",
                "Actividad Física",
                "Beber suficiente agua",
                "Meditar 5-10 minutos al día",
                "Comer proteínas magras",
                "Sueño Reparador"
            ]
            self.ui.cmbCategoria.clear()
            self.ui.cmbCategoria.addItems(nombres)
        except Exception as e:
            self.mostrar_error(f"Error al cargar categorías: {str(e)}")
        finally:
            session.close()

    def conectar_eventos(self):
        """Conectar eventos de la interfaz"""
        self.ui.btnCancelar.clicked.connect(self.limpiar_campos)
        self.ui.btnRegresar.clicked.connect(self.regresar)
        self.ui.btnRegistrar.clicked.connect(self.agregar_habito)

    def limpiar_campos(self):
        """Limpiar todos los campos del formulario"""
        self.ui.txtNombre.setText("")
        for checkbox in [
            self.ui.checkLunes, self.ui.checkMartes, self.ui.checkMiercoles,
            self.ui.checkJueves, self.ui.checkViernes, self.ui.checkSabado,
            self.ui.checkDomingo
        ]:
            checkbox.setChecked(False)
        self.ui.cmbCategoria.setCurrentIndex(0)

    def regresar(self):
        """Regresar al menú principal"""
        try:
            self.vista.close()
            if self.parent_controller:
                self.parent_controller.mostrar_vista()
        except Exception as e:
            self.mostrar_error(f"Error al regresar: {str(e)}")

    def agregar_habito(self):
        """Agregar nuevo hábito"""
        try:
            nombre = self.ui.txtNombre.text().strip()

            # Obtener días seleccionados
            dias = {
                "Lunes": self.ui.checkLunes.isChecked(),
                "Martes": self.ui.checkMartes.isChecked(),
                "Miércoles": self.ui.checkMiercoles.isChecked(),
                "Jueves": self.ui.checkJueves.isChecked(),
                "Viernes": self.ui.checkViernes.isChecked(),
                "Sábado": self.ui.checkSabado.isChecked(),
                "Domingo": self.ui.checkDomingo.isChecked()
            }
            dias_seleccionados = [dia for dia, seleccionado in dias.items() if seleccionado]

            # Validaciones
            if not nombre:
                self.mostrar_error("El nombre del hábito es obligatorio")
                return

            if not dias_seleccionados:
                self.mostrar_error("Debe seleccionar al menos un día")
                return

            # Preparar datos
            frecuencia = ",".join(dias_seleccionados)
            categoria_nombre = self.ui.cmbCategoria.currentText()
            fecha_actual = datetime.now().date()
            id_categoria = self.obtener_id_categoria(categoria_nombre)

            # Crear diccionario de datos para el repositorio
            habito_data = {
                'nombre': nombre,
                'frecuencia': frecuencia,
                'categoria': categoria_nombre,
                'fecha_creacion': fecha_actual,
                'id_categoria': id_categoria
            }

            # Guardar hábito
            nuevo_habito = self.habitos_repository.crear_habito(habito_data)

            if nuevo_habito:
                self.mostrar_exito("Hábito registrado exitosamente")
                self.limpiar_campos()
                self.cargar_categorias()  # Recargar por si se creó nueva categoría
            else:
                self.mostrar_error("Error al registrar el hábito")

        except Exception as e:
            self.mostrar_error(f"Error al registrar hábito: {str(e)}")
            print(f"Error en agregar_habito: {e}")

    def obtener_id_categoria(self, nombre_categoria):
        """Obtener ID de categoría, creándola si no existe"""
        session = self.Session()
        try:
            categoria = session.query(Categoria).filter_by(nombre=nombre_categoria).first()

            if not categoria:
                # Crear nueva categoría
                categoria = Categoria(nombre=nombre_categoria)
                session.add(categoria)
                session.commit()
                session.refresh(categoria)
                print(f"Nueva categoría creada: {nombre_categoria}")

            return categoria.id_categoria

        except Exception as e:
            session.rollback()
            print(f"Error al obtener/crear categoría: {e}")
            return None
        finally:
            session.close()

    def mostrar_error(self, mensaje: str):
        """Mostrar mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

    def mostrar_exito(self, mensaje: str):
        """Mostrar mensaje de éxito"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Éxito")
        msg.setText(mensaje)
        msg.exec()


# Función factory para mantener compatibilidad
def registro_habitos(parent_controller=None):
    return RegistroHabitosController(parent_controller)