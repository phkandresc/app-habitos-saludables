from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class RankingWidget(QWidget):
    """Widget personalizado para mostrar información de ranking en una tabla."""

    def __init__(self, posicion: int, nombre_usuario: str, puntos: int, es_usuario_actual: bool = False):
        super().__init__()
        self.posicion = posicion
        self.nombre_usuario = nombre_usuario
        self.puntos = puntos
        self.es_usuario_actual = es_usuario_actual

    def crear_items_tabla(self):
        """Crear los items para insertar en la tabla."""
        items = []

        # Item de posición
        item_posicion = QTableWidgetItem(f"#{self.posicion}")
        item_posicion.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Item de nombre de usuario
        item_nombre = QTableWidgetItem(self.nombre_usuario)
        item_nombre.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Item de puntos
        item_puntos = QTableWidgetItem(f"{self.puntos} pts")
        item_puntos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        items = [item_posicion, item_nombre, item_puntos]

        # Si es el usuario actual, destacar con negrita
        if self.es_usuario_actual:
            font = QFont()
            font.setBold(True)
            for item in items:
                item.setFont(font)
                # Agregar emoji para destacar al usuario actual
                if item == item_nombre:
                    item.setText(f"👤 {self.nombre_usuario}")

        # Agregar emoji de trofeo para los primeros puestos
        if self.posicion == 1:
            items[0].setText("🥇 #1")
        elif self.posicion == 2:
            items[0].setText("🥈 #2")
        elif self.posicion == 3:
            items[0].setText("🥉 #3")

        return items
