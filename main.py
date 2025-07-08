"""if __name__ == '__main__':
    print("Hello, World!")"""
import sys
from PyQt6 import QtWidgets
from controller.UsuarioController import UsuarioController

app = QtWidgets.QApplication(sys.argv)
myApp = UsuarioController()

myApp.show()
app.exec()
