from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtGui import QFont

class LogroWidget(QWidget):
    def __init__(self, logros, nombre_usuario="Usuario"):
        super().__init__()
        self.setWindowTitle(f"🎖 Logros de {nombre_usuario}")
        self.setGeometry(200, 100, 520, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel(f"🏅 Logros Desbloqueados por {nombre_usuario}")
        titulo.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(titulo)

        self.lista_logros = QListWidget()
        layout.addWidget(self.lista_logros)

        self.mostrar_logros(logros)

    def mostrar_logros(self, logros):
        self.lista_logros.clear()

        if not logros:
            item = QListWidgetItem()
            mensaje = QLabel("📭 Aún no has desbloqueado ningún logro.")
            mensaje.setFont(QFont("Arial", 10))
            mensaje.setStyleSheet("color: #777; padding: 10px;")

            contenedor = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(mensaje)
            layout.setContentsMargins(10, 10, 10, 10)
            contenedor.setLayout(layout)

            item.setSizeHint(contenedor.sizeHint())
            self.lista_logros.addItem(item)
            self.lista_logros.setItemWidget(item, contenedor)
            return

        for logro in logros:
            item = QListWidgetItem()
            widget = self.crear_widget_logro(logro)
            item.setSizeHint(widget.sizeHint())
            self.lista_logros.addItem(item)
            self.lista_logros.setItemWidget(item, widget)

    def crear_widget_logro(self, logro):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        lbl_nombre = QLabel(f"🏆 {logro.nombre} ({logro.puntos} pts)")
        lbl_nombre.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(lbl_nombre)

        lbl_desc = QLabel(f"📝 {logro.descripcion}")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #555; font-size: 9pt;")
        layout.addWidget(lbl_desc)

        widget.setLayout(layout)
        widget.setStyleSheet("""
            QWidget {
                background-color: #eaf2f8;
                border: 1px solid #aed6f1;
                border-radius: 6px;
            }
        """)
        return widget
