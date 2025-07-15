from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ComunidadWidget(QWidget):
    unirseClicked = pyqtSignal(int)
    salirClicked = pyqtSignal(int)
    verClicked = pyqtSignal(int)

    def __init__(self, comunidad_id, nombre, creador_nombre, categorias, num_miembros, esta_unido):
        super().__init__()

        self.comunidad_id = comunidad_id

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Título + botones
        top_layout = QHBoxLayout()
        lbl_nombre = QLabel(f"🏷️ {nombre}")
        lbl_nombre.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        top_layout.addWidget(lbl_nombre)

        top_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_unirse = QPushButton("Unirse" if not esta_unido else "Salir")
        self.btn_unirse.setStyleSheet("""
            QPushButton {
                padding: 4px 10px;
                font-size: 9pt;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
            }
        """)
        self.btn_unirse.setFixedHeight(28)
        top_layout.addWidget(self.btn_unirse)

        self.btn_ver = QPushButton("Ver")
        self.btn_ver.setStyleSheet("""
            QPushButton {
                padding: 4px 10px;
                font-size: 9pt;
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
            }
        """)
        self.btn_ver.setFixedHeight(28)
        top_layout.addWidget(self.btn_ver)

        layout.addLayout(top_layout)

        # Info: creador, categorías
        middle_layout = QHBoxLayout()
        lbl_creador = QLabel(f"👤 Creador: {creador_nombre}")
        lbl_creador.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        middle_layout.addWidget(lbl_creador)

        for cat in categorias:
            tag = QLabel(cat)
            tag.setStyleSheet("""
                QLabel {
                    background-color: #dfe6e9;
                    border-radius: 5px;
                    padding: 2px 6px;
                    margin-left: 6px;
                    font-size: 8.5pt;
                }
            """)
            middle_layout.addWidget(tag)

        layout.addLayout(middle_layout)

        # Miembros
        lbl_miembros = QLabel(f"👥 {num_miembros} miembros")
        lbl_miembros.setStyleSheet("font-size: 9pt; color: #34495e;")
        layout.addWidget(lbl_miembros)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
            }
        """)

        # Conexiones
        if not esta_unido:
            self.btn_unirse.clicked.connect(lambda: self.unirseClicked.emit(self.comunidad_id))
        else:
            self.btn_unirse.clicked.connect(lambda: self.salirClicked.emit(self.comunidad_id))

        self.btn_ver.clicked.connect(lambda: self.verClicked.emit(self.comunidad_id))
