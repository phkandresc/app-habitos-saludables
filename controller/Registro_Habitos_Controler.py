from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from datetime import datetime
#from db.connection import get_db_session
from db.connection  import DatabaseConnection
from repository.HabitosRepository import HabitosRepository
from view.windows.ventana_nuevo_habito import Ui_Form
from model.Habitos import Habitos
from model.Categorias import Categoria

class registro_habitos:
    def __init__(self, parent_controller=None):
        self.vista = QMainWindow()
        self.ui = Ui_Form()
        self.parent_controller = parent_controller  # Guardamos la referencia
        self.ui.setupUi(self.vista)
        self.db = DatabaseConnection()
        self.db_session = None
        with self.db.get_session() as session:
            self.habitos_repository = HabitosRepository(session)
            self.cargar_categorias(session)

        self.conectar_eventos()


    def cargar_categorias(self,session):
        try:
            # Categorías que deberían existir
            categorias_base = [
                "Planificar comidas balanceadas.",
                "Actividad Física",
                "Beber suficiente agua",
                "Meditar 5-10 minutos al día.",
                "Comer proteínas magras",
                "Sueño Reparador"
            ]

            # Obtener las ya existentes
            existentes = session.query(Categoria.nombre).all()
            existentes_nombres = set(cat[0] for cat in existentes)

            # Insertar las que faltan
            # Insertar las que faltan
            for nombre in categorias_base:
                if nombre not in existentes_nombres:
                    nueva_categoria = Categoria(nombre=nombre)
                    session.add(nueva_categoria)

            session.commit()  # Confirmar cambios

            # Cargar categorías en el ComboBox
            categorias = session.query(Categoria.nombre).order_by(Categoria.nombre).all()
            self.ui.cmbCategoria.clear()
            self.ui.cmbCategoria.addItems([cat[0] for cat in categorias])

            nombres = [cat[0] for cat in categorias]
            self.ui.cmbCategoria.clear()
            self.ui.cmbCategoria.addItems(nombres)

        except Exception as e:
            self.mostrar_error(f"Error al cargar categorías: {str(e)}")

    def conectar_eventos(self):
        self.ui.btnCancelar.clicked.connect(self.limpiar_campos)
        self.ui.btnRegresar.clicked.connect(self.regresar)
        self.ui.btnRegistrar.clicked.connect(self.agregar_habito)

    def limpiar_campos(self):
        self.ui.txtNombre.setText("")
        for checkbox in [
            self.ui.checkLunes, self.ui.checkMartes, self.ui.checkMiercoles,
            self.ui.checkJueves, self.ui.checkViernes, self.ui.checkSabado,
            self.ui.checkDomingo
        ]:
            self.cargar_categorias()
            checkbox.setChecked(False)

        # Opcional: Reiniciar la categoría al primer ítem
        self.ui.cmbCategoria.setCurrentIndex(0)

    def regresar(self):
        self.vista.close()
        if self.parent_controller:  # Si tenemos referencia al padre
            self.parent_controller.vista.show()  # Mostramos su vista directamente

    def agregar_habito(self):
        print("agg habito")
        nombre = self.ui.txtNombre.text()

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

        if not nombre or not dias_seleccionados:
            self.mostrar_error("Nombre y al menos un día son obligatorios")
            return

        # Convertir la lista a una cadena separada por comas (o el formato que prefieras)
        frecuencia = ",".join(dias_seleccionados)
        categoriaN = self.ui.cmbCategoria.currentText()
        fecha_actual = datetime.now().date()  # Solo fecha (sin hora)
        print(fecha_actual)

        try:
            # Validar campos vacíos
            if not nombre or not dias_seleccionados:  # Verificamos que haya al menos un día seleccionado
                self.mostrar_error("Todos los campos son obligatorios, los días al menos debe estar seleccionado uno")
                return

            id_categoria = self.obtener_id_categoria(categoriaN)

            print(f"[DEBUG] Insertando hábito: nombre={nombre}, frecuencia={frecuencia}, fecha={fecha_actual}, id_categoria={id_categoria}")

            nuevo_habito = Habitos(
                nombre=nombre,
                frecuencia=frecuencia,
                categoria=categoriaN,
                fecha_creacion=fecha_actual,
                id_categoria=id_categoria
            )

            # Guardar en la base de datos
            self.habitos_repository.crear_habito(nuevo_habito)
            QMessageBox.information(self.vista, "Éxito", "Habito registrado exitosamente.")
            self.cargar_categorias()
            self.limpiar_campos()

        except Exception as e:
            self.mostrar_error(f"Error al registrar habito: {str(e)}")

    def obtener_id_categoria(self, nombre_categoria):
        # Obtener ID desde la base de datos en lugar de mapeo hardcodeado
        from model.Categorias import Categoria
        categoria = self.db_session.query(Categoria).filter_by(nombre=nombre_categoria).first()

        if not categoria:
            # Opcional: Crear la categoría si no existe
            categoria = Categoria(nombre=nombre_categoria)
            self.db_session.add(categoria)
            self.db_session.flush()
            #self.db_session.commit()

        print(f"[DEBUG] Categoría '{nombre_categoria}' tiene ID: {categoria.id_categoria}")
        return categoria.id_categoria

    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.exec()

