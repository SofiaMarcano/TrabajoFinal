import numpy as np
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor
from PyQt5.QtCore import Qt,QTimer
from PyQt5.uic import loadUi
from Imagenes import bgPrueba_rc
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QWidget, QFileDialog, QMessageBox,QFrame, QCheckBox, QSizePolicy,
    QTableWidget, QTableWidgetItem,QComboBox
)
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
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        loadUi("archivosUI/senalesVentana.ui",self)
        self.setup()

    def setup(self):
        self.senalesBoton.clicked.connect(self.elegirSenalVista)
        self.volverBoton.clicked.connect(self.volverMenu)
        self.tabularesBoton.clicked.connect(self.elegirTablaVista)

    def elegirSenalVista(self):
        vistaElegirSenal = elegirSenalVentana(self)
        vistaElegirSenal.setControlador(self.__controlador)
        self.close()
        vistaElegirSenal.show()
    def elegirTablaVista(self):
        vistaCSV = CCSV(self)
        vistaCSV.setControlador(self.__controlador)
        self.close()
        vistaCSV.show()
        
    def setControlador(self,c):
        self.__controlador = c

    def volverMenu(self):
        self.close()
        self.parent.show()

class elegirSenalVentana(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        loadUi("archivosUI/elegirSenalVentana.ui",self)
        self.setup()

    def setup(self):
         self.senalesBoton.clicked.connect(self.cargarSenal)
         self.tabularesBoton.clicked.connect(self.openCsv)
         self.volverBoton.clicked.connect(self.volverMenu)
    def setControlador(self,c):
        self.__controlador = c

    def cargarSenal(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Archivos mat (*.mat)")
        if archivo !='':
            self.__controlador.recibirRuta(archivo)
            vistaElegirSenal = ElegirLlave(self)
            vistaElegirSenal.setControlador(self.__controlador)
            vistaElegirSenal.listarLlaves()
            self.close()
            vistaElegirSenal.show()
        else:
            self.seleccionetexto.setText("Archivo no válido")
            self.seleccionetexto.repaint()
    def openCsv(self):
        vistaCSV = CCSV(self)
        vistaCSV.setControlador(self.__controlador)
        self.close()
        vistaCSV.show()
    def volverMenu(self):
        self.close()
        self.parent.show()
            

class ElegirLlave(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        loadUi("archivosUI/elegirLlaveVentana.ui",self)
        self.setup()

    def setup(self):
        self.continuarLlave.clicked.connect(self.verificar)
        self.volverBoton.clicked.connect(self.volverMenu)
    
    def listarLlaves(self):
        self.__llaves = self.__controlador.dLlaves()
        self.comboBox.addItems(list(self.__llaves))
        
        print(self.__llaves)

    def verificar(self):
        llave = self.comboBox.currentText()
        respuesta = self.__controlador.verificarLlave(llave)
        if respuesta == "OK":
            vistaSenal = senalVista(self)
            vistaSenal.setControlador(self.__controlador)
            vistaSenal.cargarDatos(llave)
            self.close()
            vistaSenal.show()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"La llave '{llave}' no es un arreglo.\nPor favor, intenta con otra.")
            msg.setIcon(QMessageBox.Warning)

            # Aplica estilos
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    font-size: 14pt;
                    border-radius: 10px;
                }
                QMessageBox QLabel {
                    background-color: white;
                }

                QPushButton {
                    background-color: #2980B9;
                    color: white;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3498DB;
                }
            """)

            msg.exec_()

    def setControlador(self,c):
        self.__controlador = c
    def volverMenu(self):
        self.close()
        self.parent.show()

class MyGraphCanvas(FigureCanvas):
    def __init__(self, parent = None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self,self.fig)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def graficar(self, datos):
        self.axes.clear()
        for c in range(datos.shape[0]):
            self.axes.plot(datos[c,:] + c*10)

        self.axes.set_xlabel('Muestras')
        self.axes.set_ylabel('Voltaje (uV)')
        self.axes.set_title('Señales EEG')
        self.fig.patch.set_facecolor('none')
        self.fig.tight_layout()
        self.draw() 

    # def graficaProm(self,datos):
    #     self.ax2 = self.fig.add_subplot(212)
    #     self.ax2.stem(datos)
    #     self.ax2.set_xlabel('Muestras')
    #     self.ax2.set_ylabel('Voltaje (uV)')
    #     self.ax2.set_title('Señales EEG')
    #     self.draw()  

class senalVista(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("archivosUI/senales.ui",self)
        self.parent = parent
        self.setup()

    def setup(self):
        self.layout = QVBoxLayout()
        self.senalPpal.setLayout(self.layout)
        self.sc = MyGraphCanvas(self.senalPpal, width=2, height=2, dpi=60)
        self.layout.addWidget(self.sc)
        

        self.volverBoton.clicked.connect(self.volverMenu)
        # self.canalesBoton.clicked.connect(self.numCanales)
        # self.segmentarBoton.clicked.connect(self.segmentar)
        # self.estBoton.clicked.connect(self.est)
        # self.filtradoBoton.clicked.connect(self.filtrar)
        # self.boxBoton.clicked.connect(self.boxplotear)
        # self.picosBoton.clicked.connect(self.picos)
        # self.histBoton.clicked.connect(self.histogramar)
        # self.adelante.clicked.connect(self.adelantar)
        # self.atras.clicked.connect(self.atrasar)
        # self.guardar.clicked.connect(self.guardar)

    def setControlador(self,c):
        self.__controlador = c


    def cargarDatos(self,llave):
        self.__arch = self.__controlador.dDatos()
        data = self.__arch[llave]
        c, m, e = data.shape
        continua = np.reshape(data,(c,m*e), order = "F")
        self.__controlador.rDatos(continua)

        self.x_min = 0
        self.x_max = 2000

        self.sc.graficar(self.__controlador.devolverDatosSenal(self.x_min, self.x_max))

    def volverMenu(self):
        self.close()
        self.parent.show()

class CCSV(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.__controlador = None

        self.setWindowTitle(" 🐱Cargar Datos Tabulares (.csv)")
        self.setGeometry(450, 200, 600, 300)
        self.setFixedSize(600, 300)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1E1E2F"))
        palette.setColor(QPalette.WindowText, QColor("#F0F0F0"))
        self.setPalette(palette)
        self.setStyleSheet("""
            QLabel {
                color: #F0F0F0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #2E2E3A;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #F0F0F0;
            }
            QPushButton {
                background-color: #00A8CC;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #007EA7;
            }
        """)
        self.labelTitulo = QLabel("Cargar Datos Tabulares (.csv)")
        self.labelTitulo.setFont(QFont("Segoe UI", 16))
        self.labelTitulo.setAlignment(Qt.AlignCenter)

        self.labelEstado = QLabel("No hay archivo cargado.")
        self.labelEstado.setAlignment(Qt.AlignCenter)
        self.labelEstado.setStyleSheet("color: #FF5555; font-weight: bold;")

        self.inputRuta = QLineEdit()
        self.inputRuta.setPlaceholderText("Ruta del archivo CSV")
        self.inputRuta.setReadOnly(True)

        self.botonSeleccionar = QPushButton("Seleccionar CSV")
        self.botonSeleccionar.setCursor(QCursor(Qt.PointingHandCursor))

        self.botonVisualizar = QPushButton("Visualizar tabla")
        self.botonVisualizar.setCursor(QCursor(Qt.PointingHandCursor))

        self.botonVolver = QPushButton("Volver")
        self.botonVolver.setCursor(QCursor(Qt.PointingHandCursor))
        # Layouts
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        mainLayout.addWidget(self.labelTitulo)

        rutaLayout = QHBoxLayout()
        rutaLayout.addWidget(self.inputRuta)
        rutaLayout.addWidget(self.botonSeleccionar)
        mainLayout.addLayout(rutaLayout)

        mainLayout.addWidget(self.labelEstado)

        botonesLayout = QHBoxLayout()
        botonesLayout.addStretch()
        botonesLayout.addWidget(self.botonVisualizar)
        botonesLayout.addWidget(self.botonVolver)
        mainLayout.addLayout(botonesLayout)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        self.botonSeleccionar.clicked.connect(self.openCSV)
        self.botonVisualizar.clicked.connect(self.seeTabla)
        self.botonVolver.clicked.connect(self.volverMenu)

    def setControlador(self, c):
        self.__controlador = c

    def openCSV(self):
        a, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo CSV", "", "Archivos CSV (*.csv)"
        )
        if a:
            r= self.__controlador.procesarCSV(a)
            if r== "OK":
                self.inputRuta.setText(a)
                self.labelEstado.setText("Archivo CSV cargado correctamente.")
                self.labelEstado.setStyleSheet("color: #44DD44; font-weight: bold;")
            else:
                self.labelEstado.setText("Error al cargar el CSV.")
                self.labelEstado.setStyleSheet("color: #FF5555; font-weight: bold;")
        else:
            self.labelEstado.setText("Selección cancelada.")
            self.labelEstado.setStyleSheet("color: #FF5555; font-weight: bold;")

    def seeTabla(self):
        if self.__controlador:
            datos = self.__controlador.obtenerDatosCSV()
            columnas = self.__controlador.obtenerColumnasCSV()
            if datos is not None:
                self.__controlador.TablaEnNueva(datos, columnas)
            else:
                QMessageBox.warning(self, "Error", "No hay datos cargados.")
        else:
            QMessageBox.warning(self, "Error", "Controlador no asignado.")

    def volverMenu(self):
        self.close()
        if self.parent:
            self.parent.show()


class TablaCSV(QMainWindow):
    def __init__(self, datos, columnas=None, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.datos = datos
        self.columnas = columnas

        self.setWindowTitle(" 🐱Visualizador de Datos Tabulares (.csv)")
        self.setGeometry(400, 150, 800, 600)
        self.setFixedSize(800, 600)
        palette = QPalette()
        self.scatterColor = 'cyan'
        self.colorOptions = ['cyan', 'magenta', 'yellow', 'red', 'green', 'blue', 'orange', 'purple', 'white', 'grey']
        palette.setColor(QPalette.Window, QColor("#1E1E2F"))
        palette.setColor(QPalette.WindowText, QColor("#F0F0F0"))
        self.setPalette(palette)
        self.setStyleSheet("""
            QLabel {
                color: #F0F0F0;
                font-size: 14px;
            }
            QTableWidget {
                background-color: #2E2E3A;
                color: #F0F0F0;
                gridline-color: #555;
            }
            QComboBox {
                background-color: #2E2E3A;
                color: #F0F0F0;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #00A8CC;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #007EA7;
            }
        """)

        self.central = QWidget()
        self.layout = QVBoxLayout()
        self.central.setLayout(self.layout)
        self.setCentralWidget(self.central)

        self.labelTitulo = QLabel("Visualizador de Datos Tabulares (.csv)")
        self.labelTitulo.setAlignment(Qt.AlignCenter)
        self.labelTitulo.setFont(QFont("Segoe UI", 16))
        self.layout.addWidget(self.labelTitulo)

        # Tabla de datos
        self.tabla = QTableWidget()
        self.layout.addWidget(self.tabla)

        # Selector de columnas
        selectorLayout = QHBoxLayout()
        self.comboX = QComboBox()
        self.comboY = QComboBox()

        selectorLayout.addWidget(QLabel("Columna X:"))
        selectorLayout.addWidget(self.comboX)
        selectorLayout.addWidget(QLabel("Columna Y:"))
        selectorLayout.addWidget(self.comboY)
        self.layout.addLayout(selectorLayout)

        # Botón para graficar
        self.botonGraficar = QPushButton("Graficar dispersión")
        
        self.layout.addWidget(self.botonGraficar)
        colorLayout = QHBoxLayout()
        self.labelColor = QLabel("🐱Color de puntos:")
        self.comboColor = QComboBox()
        self.comboColor.addItems(self.colorOptions)
        self.comboColor.setCurrentText(self.scatterColor)
        colorLayout.addWidget(self.labelColor)
        colorLayout.addWidget(self.comboColor)
        self.layout.addLayout(colorLayout)
        # Botón volver
        self.botonVolver = QPushButton("Volver")
        self.layout.addWidget(self.botonVolver)

        # Conexiones
        self.botonGraficar.clicked.connect(self.graficar)
        self.botonVolver.clicked.connect(self.volver)
        self.comboColor.currentIndexChanged.connect(self.cambiarColor)
        self.cargarDatos()
    def cambiarColor(self):
        self.scatterColor = self.comboColor.currentText()

    def cargarDatos(self):
        if hasattr(self.datos, 'shape'):
            rows, cols = self.datos.shape
            self.tabla.setRowCount(rows)
            self.tabla.setColumnCount(cols)

            if self.columnas is not None:
                self.tabla.setHorizontalHeaderLabels(self.columnas)
                self.comboX.addItems(self.columnas)
                self.comboY.addItems(self.columnas)
            else:
                labels = [f"Columna {i+1}" for i in range(cols)]
                self.tabla.setHorizontalHeaderLabels(labels)
                self.comboX.addItems(labels)
                self.comboY.addItems(labels)

            for i in range(rows):
                for j in range(cols):
                    item = QTableWidgetItem(str(self.datos[i, j]))
                    self.tabla.setItem(i, j, item)
        else:
            self.tabla.setRowCount(0)
            self.tabla.setColumnCount(0)

    def graficar(self):
        try:
            colX = self.comboX.currentIndex()
            colY = self.comboY.currentIndex()

            x = self.datos[:, colX]
            y = self.datos[:, colY]

            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.scatter(x, y, color=self.scatterColor, alpha=0.7)
            ax.set_xlabel(self.comboX.currentText(), color='white', fontsize=12)
            ax.set_ylabel(self.comboY.currentText(), color='white', fontsize=12)
            ax.set_title("Gráfico de dispersión", color='white', fontsize=14)
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')

            ax.grid(True, color='#555')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print("Error al graficar:", e)


    def volver(self):
        self.close()
        if self.parent:
            self.parent.show()
