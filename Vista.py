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

    def interfaz(self):
        self.label_usuario = QLabel("Usuario:")
        self.input_usuario = QLineEdit()

        self.label_password = QLabel("Contraseña:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)

        self.boton_login = QPushButton("Ingresar")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(self.label_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.boton_login)

        self.setLayout(layout)

    def estilo(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1E1E2F"))
        palette.setColor(QPalette.WindowText, QColor("#F0F0F0"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QLabel {
                color: #F0F0F0;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background-color: #2E2E3A;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
                color: #F0F0F0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005F99;
            }
        """)

        font = QFont("Segoe UI", 10)
        self.setFont(font)
