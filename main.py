import sys
from PyQt6.QtWidgets import QApplication
from controller.LoginController import LoginController

if __name__ == '__main__':
    app = QApplication(sys.argv)

    controller = LoginController()
    controller.vista.show()

    sys.exit(app.exec())