
from PyQt5.QtWidgets import QWidget, QLabel, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox, QFileDialog
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor
from PyQt5.QtCore import Qt,QTimer
from PyQt5.uic import loadUi
from Imagenes import bgPrueba_rc

# vista/login_vista.py
# from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox
# from PyQt5.QtGui import QFont, QPalette, QColor, QCursor
# from PyQt5.QtCore import Qt

class LoginVista(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" 🐱Sistema Biomédico - Ingreso")
        self.setGeometry(500, 150, 600, 480)
        self.setFixedSize(600, 480)
        self.controlador = None
        self.interfaz()
        self.estilo()

    def set_controlador(self, controlador):
        self.controlador = controlador

    def get_controlador(self):
        return self.controlador

    def interfaz(self):
        # Línea divisoria decorativa
        self.linea = QFrame()
        self.linea.setFrameShape(QFrame.HLine)
        self.linea.setFrameShadow(QFrame.Sunken)
        self.linea.setStyleSheet("color: #777;")

        # Campo de usuario
        self.label_usuario = QLabel("Usuario:")
        self.input_usuario = QLineEdit()

        # Campo de contraseña
        self.label_password = QLabel("Contraseña:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)

        # CheckBox para mostrar/ocultar contraseña
        self.checkbox_mostrar = QCheckBox("Mostrar contraseña")
        self.checkbox_mostrar.stateChanged.connect(self.toggle_password)

        # Etiqueta para errores
        self.label_error = QLabel("")
        self.label_error.setStyleSheet("color: #FF5555; font-weight: bold; font-size: 14px;")
        self.label_error.setAlignment(Qt.AlignCenter)

        # Botón de login
        self.boton_login = QPushButton("Ingresar")
        self.boton_login.setCursor(QCursor(Qt.PointingHandCursor))

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.addWidget(self.linea)
        layout.addWidget(self.label_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.checkbox_mostrar)
        layout.addWidget(self.label_error)
        layout.addStretch(1)
        layout.addWidget(self.boton_login)

        self.setLayout(layout)

    def estilo(self):
        # Colores y fuentes personalizados
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1E1E2F"))
        palette.setColor(QPalette.WindowText, QColor("#F0F0F0"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QLabel {
                color: #F0F0F0;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #2E2E3A;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 10px;
                color: #F0F0F0;
                font-size: 16px;
            }
            QCheckBox {
                color: #CCCCCC;
                font-size: 13px;
            }
            QPushButton {
                background-color: #00A8CC;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 14px;
                font-size: 17px;
            }
            QPushButton:hover {
                background-color: #007EA7;
            }
        """)

        font = QFont("Segoe UI", 12)
        self.setFont(font)

    def clear(self):
        self.input_usuario.clear()
        self.input_password.clear()

    def error(self, mensaje):
        self.label_error.setText(mensaje)
        self.label_error.setStyleSheet("color: red; font-weight: bold;")
        self.label_error.setVisible(True)
        QTimer.singleShot(4000, lambda: self.label_error.clear())
    def espera(self):
        self.setCursor(QCursor(Qt.WaitCursor))

    def normal(self):
        self.setCursor(QCursor(Qt.ArrowCursor))

    def toggle_password(self, estado):
        # Cambia entre mostrar y ocultar contraseña
        if estado == Qt.Checked:
            self.input_password.setEchoMode(QLineEdit.Normal)
        else:
            self.input_password.setEchoMode(QLineEdit.Password)


class senales_tabla_menu_Vista(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("archivosUI/senalesVentana.ui",self)
        self.setup()

    def setup(self):
        self.senalesBoton.clicked.connect(self.elegirSenalVista)
        # self.tabularesBoton.clicked.connect(self.elegirTablaVista)

    def elegirSenalVista(self):
        vistaElegirSenal = elegirSenalVentana(self)
        vistaElegirSenal.asignarControlador(self.__controlador)
        self.close()
        vistaElegirSenal.show()

    # def elegirTablaVista(self):
    #     vistaElegirTabla = elegirTablaVentana(self)
    #     vistaElegirTabla.asignarControlador(self.__controlador)
    #     self.close()
    #     vistaElegirTabla.show()
        
    def asignarControlador(self,c):
        self.__controlador = c

class elegirSenalVentana(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("archivosUI/elegirSenalVentana.ui",self)
        self.setup()

    def setup(self):
        self.abriSenal.clicked.connect(self.cargarSenal)

    def asignarControlador(self,c):
        self.__controlador = c

    def cargarSenal(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Archivos mat (*.mat)")
        if archivo !='':
            self.__controlador.recibirRuta(archivo)
            self.__llaves = self.__controlador.dLlaves()
            print(self.__llaves)
            # vistaElegirSenal = ElegirLlave(self)
            # vistaElegirSenal.asignarControlador(self.__controlador)
            # self.close()
            # vistaElegirSenal.show()
        else:
            self.seleccionetexto.setText("Señal no válida")
            self.seleccionetexto.repaint()

            

class ElegirLlave(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("archivosUI/llaveVentana.ui",self)
        self.setup()

    # def setup(self):
    #     self.abriSenal.clicked.connect(self.cargarSenal)

    def asignarControlador(self,c):
        self.__controlador = c