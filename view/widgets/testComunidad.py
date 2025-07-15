import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QListWidgetItem,
    QVBoxLayout, QMessageBox
)
from ComunidadWidget import ComunidadWidget  # Asegúrate de tenerlo en un archivo separado

# Datos simulados
comunidades = [
    {
        "id": 1,
        "nombre": "Vida Saludable",
        "creador": "Andrea Martínez",
        "categorias": ["Ejercicio", "Nutrición"],
        "miembros": 25,
        "esta_unido": False
    },
    {
        "id": 2,
        "nombre": "Lectura Diaria",
        "creador": "Carlos Ruiz",
        "categorias": ["Crecimiento Personal"],
        "miembros": 13,
        "esta_unido": True
    },
    {
        "id": 3,
        "nombre": "Sueño Reparador",
        "creador": "Valentina López",
        "categorias": ["Descanso", "Salud Mental"],
        "miembros": 40,
        "esta_unido": False
    }
]

class VentanaComunidades(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba - ComunidadWidget")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()
        self.lista = QListWidget()
        layout.addWidget(self.lista)
        self.setLayout(layout)

        for c in comunidades:
            widget = ComunidadWidget(
                comunidad_id=c["id"],
                nombre=c["nombre"],
                creador_nombre=c["creador"],
                categorias=c["categorias"],
                num_miembros=c["miembros"],
                esta_unido=c["esta_unido"]
            )

            widget.unirseClicked.connect(self.unirse)
            widget.salirClicked.connect(self.salir)
            widget.verClicked.connect(self.ver)

            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())

            self.lista.addItem(item)
            self.lista.setItemWidget(item, widget)

    def unirse(self, id_comunidad):
        QMessageBox.information(self, "Unirse", f"Te has unido a la comunidad #{id_comunidad}")

    def salir(self, id_comunidad):
        QMessageBox.warning(self, "Salir", f"Has salido de la comunidad #{id_comunidad}")

    def ver(self, id_comunidad):
        QMessageBox.information(self, "Detalle", f"Viendo detalles de la comunidad #{id_comunidad}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaComunidades()
    ventana.show()
    sys.exit(app.exec())
