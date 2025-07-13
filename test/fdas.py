from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
import sys

# Modelo de prueba
class Habito:
    def __init__(self, id_habito, nombre, frecuencia, id_categoria, estado):
        self.id_habito = id_habito
        self.nombre = nombre
        self.frecuencia = frecuencia
        self.id_categoria = id_categoria
        self.estado = estado

# Widget personalizado con botón de estado
class HabitoWidget(QWidget):
    editarClicked = pyqtSignal(int)
    eliminarClicked = pyqtSignal(int)
    estadoClicked = pyqtSignal(int)

    def __init__(self, habito, categoria_nombre):
        super().__init__()

        self.habito_id = habito.id_habito
        self.estado = habito.estado.lower()

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Línea superior: nombre + botones
        top_layout = QHBoxLayout()
        lbl_nombre = QLabel(f"📝 {habito.nombre}")
        lbl_nombre.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        top_layout.addWidget(lbl_nombre)

        top_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        btn_editar = QPushButton("✏️ Editar")
        btn_eliminar = QPushButton("🗑 Eliminar")
        btn_editar.setFixedHeight(24)
        btn_eliminar.setFixedHeight(24)
        btn_editar.setStyleSheet("font-size: 9pt;")
        btn_eliminar.setStyleSheet("font-size: 9pt;")
        top_layout.addWidget(btn_editar)
        top_layout.addWidget(btn_eliminar)

        layout.addLayout(top_layout)

        # Línea inferior: categoría + botón de estado
        bottom_layout = QHBoxLayout()

        lbl_categoria = QLabel(f"🏷️ {categoria_nombre}")
        lbl_categoria.setStyleSheet("color: #7f8c8d; font-size: 10pt;")
        bottom_layout.addWidget(lbl_categoria)

        bottom_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Botón de estado
        self.btn_estado = QPushButton()
        self.btn_estado.setFixedHeight(24)
        self.actualizar_estilo_estado()
        bottom_layout.addWidget(self.btn_estado)

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
            }
        """)

        # Conexiones
        btn_editar.clicked.connect(lambda: self.editarClicked.emit(self.habito_id))
        btn_eliminar.clicked.connect(lambda: self.eliminarClicked.emit(self.habito_id))
        self.btn_estado.clicked.connect(lambda: self.estadoClicked.emit(self.habito_id))

    def actualizar_estilo_estado(self):
        if self.estado == "completado":
            self.btn_estado.setText("✅ Completado")
            self.btn_estado.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    font-weight: bold;
                    font-size: 9pt;
                    border-radius: 5px;
                    padding: 2px 8px;
                }
            """)
        else:
            self.btn_estado.setText("⏳ Pendiente")
            self.btn_estado.setStyleSheet("""
                QPushButton {
                    background-color: #bdc3c7;
                    color: white;
                    font-size: 9pt;
                    border-radius: 5px;
                    padding: 2px 8px;
                }
            """)

# Ventana de prueba
class TestVentana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba HabitoWidget con Botón Estado")
        self.setGeometry(100, 100, 520, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        # Datos de prueba
        habitos = [
            Habito(1, "Hacer ejercicio", "lunes, miércoles, viernes", 1, "completado"),
            Habito(2, "Leer 30 minutos", "todos los días", 2, "pendiente"),
            Habito(3, "Dormir 8 horas", "lunes a domingo", 3, "pendiente"),
        ]

        categorias = {
            1: "Ejercicio",
            2: "Crecimiento personal",
            3: "Salud"
        }

        for habito in habitos:
            widget = HabitoWidget(habito, categorias[habito.id_categoria])
            widget.editarClicked.connect(self.editar_habito)
            widget.eliminarClicked.connect(self.eliminar_habito)
            widget.estadoClicked.connect(self.ver_estado_habito)

            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.lista.addItem(item)
            self.lista.setItemWidget(item, widget)

    def editar_habito(self, habito_id):
        print(f"[Editar] Hábito ID: {habito_id}")

    def eliminar_habito(self, habito_id):
        print(f"[Eliminar] Hábito ID: {habito_id}")

    def ver_estado_habito(self, habito_id):
        print(f"[Estado] Click en estado del hábito ID: {habito_id}")
        # Aquí abrirás la ventana para registrar observaciones u otra acción

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = TestVentana()
    ventana.show()
    sys.exit(app.exec())
