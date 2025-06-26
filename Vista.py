from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt

class LoginVista(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" 🐱Sistema Biomédico - Ingreso")
        self.setGeometry(600, 300, 350, 280)
        self.interfaz()
        self.estilo()
        self.controlador = None
    def set_controlador(self, controlador):
        self.controlador = controlador

    def get_controlador(self):
        return self.controlador

    