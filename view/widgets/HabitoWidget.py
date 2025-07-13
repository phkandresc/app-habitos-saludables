from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy, QSpacerItem)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

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