import numpy as np
import os
import cv2
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor, QIntValidator
from PyQt5.QtCore import Qt,QTimer
from PyQt5.uic import loadUi
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QWidget, QFileDialog, QMessageBox,QFrame, QCheckBox, QSizePolicy,
    QTableWidget, QSlider, QTableWidgetItem,QComboBox,QInputDialog,QDialog, QDialogButtonBox, QFormLayout
)
from Img import bgPrueba_rc

#########################################LOGIN#############################################
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
    

###########################################EXPERTO EN SEÑALES MENU###########################################
class senalesMenuVista(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        loadUi("archivosUI/senalesVentana.ui",self)
        self.setGeometry(500, 150, 600, 480)
        self.setFixedSize(509, 415)
        self.setup()

    def setup(self):
        self.senalesBoton.clicked.connect(self.elegirSenalVista)
        self.tabularesBoton.clicked.connect(self.elegirTablaVista)
        self.volverBoton.clicked.connect(self.volverMenu)

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

############################################MAT#########################################################
class elegirSenalVentana(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        loadUi("archivosUI/elegirSenalVentana.ui",self)
        self.setGeometry(500, 150, 600, 480)
        self.setFixedSize(755, 465)
        self.setup()

    def setup(self):
        self.abrirSenal.clicked.connect(self.cargarSenal)
        self.cargarMAT.clicked.connect(self.subirdeDB)
        self.volverBoton.clicked.connect(self.volverMenu)

    def setControlador(self,c):
        self.__controlador = c
        self.listarMat()
        
    def listarMat(self):
        self.comboBoxDBMAT.clear()
        listadbmats = self.__controlador.listarMATs()
        for item in listadbmats:
                self.comboBoxDBMAT.addItem(f"{item['id']} - {item['nombre_archivo']}", item['ruta'])

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
            self.seleccioneTexto.setText("Archivo no válido")
            self.seleccioneTexto.repaint()

    def volverMenu(self):
        self.close()
        self.parent.show()

    def subirdeDB(self):
        try:
            ruta = self.comboBoxDBMAT.currentData()
            if ruta !='':
                self.__controlador.recibirRuta(ruta)
                vistaElegirSenal = ElegirLlave(self)
                vistaElegirSenal.setControlador(self.__controlador)
                vistaElegirSenal.listarLlaves()
                self.close()
                vistaElegirSenal.show()
            else:
                self.seleccioneTexto.setText("Archivo no válido")
                self.seleccioneTexto.repaint()
        except Exception as e:
            print(str(e))
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Ha ocurrido un error al cargar el archivo")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            
class ElegirLlave(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        loadUi("archivosUI/elegirLlaveVentana.ui",self)
        self.setGeometry(500, 150, 600, 480)
        self.setFixedSize(755, 465)
        self.setup()

    def setup(self):
        self.continuarLlave.clicked.connect(self.verificar)
        self.volverBoton.clicked.connect(self.volverMenu)
    
    def listarLlaves(self):
        self.__llaves = self.__controlador.llevarLlaves()
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
        self.parent.listarMat()
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

    def graficar(self, datos, min=0):
        self.axes.clear()
        try:
            eje_x = np.arange(min, min + datos.shape[1])
            for c in range(datos.shape[0]):
                self.axes.plot(eje_x, datos[c,:] + c*10)

            self.axes.set_xlabel('Muestras')
            self.axes.set_ylabel('Voltaje (uV)')
            self.axes.set_title('Señal')
            self.fig.patch.set_facecolor('none')
            self.fig.tight_layout()
            try:
                self.axes.set_xlim(min, min + datos.shape[1] - 1)
            except:
                pass
            self.draw() 
        except:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Ha ocurrido un error al graficar la señal")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

class MyGraphCanvas2(FigureCanvas):
    def __init__(self, parent = None, width=5, height=5, dpi=60):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self,self.fig)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        

    def graficarPromedio(self, datos):
        self.axes.clear()
        self.axes.stem(datos)
        self.axes.set_xlabel("Canales")
        self.axes.set_ylabel("Promedio")
        self.axes.set_title("Promedio canales")
        self.fig.tight_layout()
        self.draw()  

    def graficarSenal(self, datos, min=0, picos=None, canal=0):
        self.axes.clear()
        try:
            eje_x = np.arange(min, min + datos.shape[1])
            if picos is None:
                for c in range(datos.shape[0]):
                    self.axes.plot(eje_x, datos[c,:] + c*10)
            else:
                self.axes.vlines(picos, ymin=datos.min(), ymax=datos.max(), linestyle='--',
                                color='dodgerblue', label='Peak')
                self.axes.plot(eje_x, datos[canal,:])

            self.axes.set_xlabel('Muestras')
            self.axes.set_ylabel('Voltaje (uV)')
            self.axes.set_title('Señales')
            self.fig.patch.set_facecolor('none')
            try:
                self.axes.set_xlim(min, min + datos.shape[1] - 1)
            except:
                pass
            self.fig.tight_layout()
            self.draw() 
        except:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Ha ocurrido un error al graficar la señal")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def graficarHistograma(self, datos, epoca):
        self.axes.clear()
        self.axes.hist(datos, bins=30, color='skyblue', edgecolor='black')
        self.axes.set_xlabel('Amplitud')
        self.axes.set_ylabel('Frecuencia')
        self.axes.set_title(f"Histograma de época {epoca}")
        self.fig.tight_layout()
        self.draw()  

class senalVista(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("archivosUI/senales.ui",self)
        self.setGeometry(500, 150, 600, 480)
        self.setFixedSize(755, 465)
        self.parent = parent
        self.setup()

    def setup(self):
        self.layout = QVBoxLayout()
        self.senalPpal.setLayout(self.layout)
        self.sc = MyGraphCanvas(self.senalPpal, width=5, height=4, dpi=60)
        self.layout.addWidget(self.sc)
        self.min.setValidator(QIntValidator())
        self.max.setValidator(QIntValidator())

        self.layout2 = QVBoxLayout()
        self.graficoEst.setLayout(self.layout2)
        self.sc2 = MyGraphCanvas2(self.graficoEst)
        self.layout2.addWidget(self.sc2)
        

        self.volverBoton.clicked.connect(self.volverMenu)
        self.canalesBoton.clicked.connect(self.numCanales)
        self.segmentarBoton.clicked.connect(self.segmentar)
        self.promedioBoton.clicked.connect(self.prom)
        self.estBoton.clicked.connect(self.est)
        self.filtradoBoton.clicked.connect(self.filtrar)
        self.picosBoton.clicked.connect(self.picos)
        self.histBoton.clicked.connect(self.histogramar)
        self.adelante.clicked.connect(self.adelantar)
        self.atras.clicked.connect(self.atrasar)
        self.guardarBoton.clicked.connect(self.guardar)

    def setControlador(self,c):
        self.__controlador = c
        self.guardarEnBase()


    def cargarDatos(self,llave):
        self.__arch, continua, self.__c, self.__m, self.__e = self.__controlador.llevarDatos(llave)

        #Datos predeterminados
        self.x_min = 0
        self.x_max = 2000

        self.sc.graficar(self.__controlador.devolverDatosSenal(self.x_min, self.x_max))
        self.shapeTexto.setText(f"Canales: {str(self.__c)}, muestas: {str(self.__m)}, épocas: {str(self.__e)}")
        self.shapeTexto.repaint()
        self.spinBox.setMaximum(self.__c)
        self.spinBoxCanal.setMaximum(self.__c)
        self.epocaSpinbox.setMaximum(self.__e)
        self.spinBox.setValue(self.__c)
        #fm = frecuencia muestreo, fc = frecuencia corte
        #valores predeterminados
        self.fmSpinBox.setValue(1000)
        self.fcSpinBox.setValue(10)

    def numCanales(self):
        c = self.spinBox.value()
        self.sc.graficar(self.__controlador.devolverDatosSenal(self.x_min, self.x_max,c), self.x_min)

    def segmentar(self):
        try:
            self.x_min = int(self.min.text())
            self.x_max = int(self.max.text())
            self.numCanales()
        except:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"No ha ingresado bien los valores")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def prom(self):
        c = self.spinBox.value()
        self.sc2.graficarPromedio(self.__controlador.devolverDatosSenalProm(self.__arch, c))
    
    def est(self):
        c = self.spinBoxCanal.value()
        promedio, desviacion = self.__controlador.getEstSenal(c)
        self.resEstTexto.setText(f"Pro.: {str(promedio)} \nDE: {str(desviacion)}")
        self.resEstTexto.repaint()

    def filtrar(self):
        c = self.spinBox.value()
        fs = self.fmSpinBox.value()
        fc = self.fcSpinBox.value()
        datos = self.__controlador.devolverDatosSenal(self.x_min, self.x_max,c)
        try:
            filtrada = self.__controlador.llevarFiltro(datos, fs, fc)
            self.sc2.graficarSenal(filtrada, self.x_min)
        except:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Hay un valor no válido")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def picos(self):
        c = self.spinBox.value()
        cPicos = self.canalPicos.value()
        picos = self.__controlador.llevarPicos(cPicos)
        self.sc2.graficarSenal(self.__controlador.devolverDatosSenal(self.x_min, self.x_max,c), self.x_min, picos, cPicos)
        self.picosTexto.setText(f"Picos Total: {str(len(picos))}")
        self.picosTexto.repaint()

    def histogramar(self):
        e = self.epocaSpinbox.value()
        if 0 <= e < self.__e:
            datos = self.__controlador.llevarHist(e)
            self.sc2.graficarHistograma(datos, e)
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Fuera de rango")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def adelantar(self):
        self.x_min = self.x_min + 100
        self.x_max = self.x_max + 100
        self.numCanales()
    
    def atrasar(self):
        self.x_min = self.x_min - 100
        self.x_max = self.x_max - 100
        self.numCanales()

    def guardar(self):
        if self.__controlador.guardar(self.sc.fig) == True:
            self.guardarTexto.setText(f"Guardado")
            self.guardarTexto.repaint()
        else:
            self.guardarTexto.setText("Error")
            self.guardarTexto.repaint()

    def volverMenu(self):
        self.close()
        self.parent.show()


    def guardarEnBase(self):
        if not self.__controlador or not self.__controlador.devolverRutaMAT():
            QMessageBox.warning(self, "Error", "No se conoce la ruta del archivo MAT original.")
            return

        ruta_mat = self.__controlador.devolverRutaMAT()
        nombre_archivo = os.path.basename(ruta_mat)
        exito = self.__controlador.guardarBD(nombre_archivo, ruta_mat)
        if exito:
            print(self, "Guardado", f"MAT '{nombre_archivo}' guardado en base de datos.")
        else:
            print(self, "Duplicado", f"Ya existe un registro con la ruta '{ruta_mat}' en la base de datos.")

###################################################CSV##############################################################
class CCSV(QMainWindow):
    def __init__(self, parent=None,ventana=None):
        super().__init__(parent)
        self.parent= parent
        self.ventana=ventana
        self.__controlador = None

        self.setWindowTitle("🐱 Cargar Datos Tabulares (.csv)")
        self.setGeometry(450, 200, 600, 400)
        self.setFixedSize(600, 400)

        # Modo oscuro
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
                padding: 8px;
                color: #F0F0F0;
            }
            QPushButton {
                background-color: #00A8CC;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007EA7;
            }
        """)

        # ---------- Widgets ----------
        self.labelTitulo = QLabel("🐱 Cargar Datos Tabulares (.csv)")
        self.labelTitulo.setFont(QFont("Segoe UI", 16))
        self.labelTitulo.setAlignment(Qt.AlignCenter)

        self.labelEstado = QLabel("No hay archivo cargado.")
        self.labelEstado.setAlignment(Qt.AlignCenter)
        self.labelEstado.setStyleSheet("color: #FF5555; font-weight: bold;")

        # Entrada de ruta local
        self.inputRuta = QLineEdit()
        self.inputRuta.setPlaceholderText("Ruta del archivo CSV")
        self.inputRuta.setReadOnly(True)

        self.botonSeleccionar = QPushButton("Seleccionar CSV")
        self.botonSeleccionar.setCursor(QCursor(Qt.PointingHandCursor))

        # Selector de CSV guardados en base
        self.comboDB = QComboBox()
        self.botonCargarDB = QPushButton("Cargar de DB")
        self.botonCargarDB.setCursor(QCursor(Qt.PointingHandCursor))

        # Botón para visualizar
        self.botonVisualizar = QPushButton("Visualizar tabla")
        self.botonVisualizar.setCursor(QCursor(Qt.PointingHandCursor))

        # Botón volver
        self.botonVolver = QPushButton("Volver")
        self.botonVolver.setCursor(QCursor(Qt.PointingHandCursor))

        # ---------- Layout ----------
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        mainLayout.addWidget(self.labelTitulo)

        # Cargar desde disco
        rutaLayout = QHBoxLayout()
        rutaLayout.addWidget(self.inputRuta)
        rutaLayout.addWidget(self.botonSeleccionar)
        mainLayout.addLayout(rutaLayout)

        # Línea divisoria
        mainLayout.addWidget(QLabel("—" * 50))

        # Cargar desde base
        dbLayout = QHBoxLayout()
        dbLayout.addWidget(QLabel("CSV en BD:"))
        dbLayout.addWidget(self.comboDB)
        dbLayout.addWidget(self.botonCargarDB)
        mainLayout.addLayout(dbLayout)

        # Estado
        mainLayout.addWidget(self.labelEstado)

        # Botones abajo
        botonesLayout = QHBoxLayout()
        botonesLayout.addStretch()
        botonesLayout.addWidget(self.botonVisualizar)
        botonesLayout.addWidget(self.botonVolver)
        mainLayout.addLayout(botonesLayout)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        # ---------- Conexiones ----------
        self.botonSeleccionar.clicked.connect(self.openCSV)
        self.botonCargarDB.clicked.connect(self.cargarDesdeBase)
        self.botonVisualizar.clicked.connect(self.seeTabla)
        self.botonVolver.clicked.connect(self.volverMenu)

    def setControlador(self, c):
        self.__controlador = c
        self.__controlador.vista = self
        if self.__controlador:
            # Al asignar el controlador, pedirle los CSV guardados
            lista = self.__controlador.listarCSVs()
            self.comboDB.clear()
            for item in lista:
                self.comboDB.addItem(f"{item['id']} - {item['nombre_archivo']}", item['id'])

    def openCSV(self):
        a, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo CSV", "", "Archivos CSV (*.csv)"
        )
        if a:
            r = self.__controlador.procesarCSV(a)
            if r == "OK":
                self.inputRuta.setText(a)
                self.labelEstado.setText("Archivo CSV cargado desde disco.")
                self.labelEstado.setStyleSheet("color: #44DD44; font-weight: bold;")
                self.__controlador.setCargadoDesdeBase(False)
                nombre_archivo = os.path.basename(a)
                self.__controlador.setNombreCSV(nombre_archivo)

                # ✅ Abrir TablaCSV con este CSV
                datos, columnas = self.__controlador.getDatosColumnas()

                # ✅ Cerrar la ventana actual (CCSV)
                self.close()
                self.__controlador.TablaEnNueva(datos, columnas,parent=self,ventana=self.parent)
        else:
            self.labelEstado.setText("Selección cancelada.")
            self.labelEstado.setStyleSheet("color: #FF5555; font-weight: bold;")

    def cargarDesdeBase(self):
        if not self.__controlador:
            QMessageBox.warning(self, "Error", "Controlador no asignado.")
            return

        id_archivo = self.comboDB.currentData()
        if not id_archivo:
            QMessageBox.warning(self, "Error", "No hay selección.")
            return

        resultado = self.__controlador.cargarCSVporID(id_archivo)
        if resultado == "ERROR":
            self.labelEstado.setText("Error al cargar desde base.")
            self.labelEstado.setStyleSheet("color: #FF5555; font-weight: bold;")
            return

        nombre_archivo, datos, columnas = resultado

        self.labelEstado.setText(f"Archivo CSV cargado desde base (ID: {id_archivo}).")
        self.labelEstado.setStyleSheet("color: #44DD44; font-weight: bold;")

    
        self.__controlador.setNombreCSV(nombre_archivo)
        self.__controlador.setCargadoDesdeBase(True)

        self.close()
        self.__controlador.TablaEnNueva(datos, columnas, parent=self,ventana=self.parent)


    def seeTabla(self):
        if self.__controlador:
            datos = self.__controlador.obtenerDatosCSV()
            columnas = self.__controlador.obtenerColumnasCSV()
            if datos is not None:
                self.__controlador.TablaEnNueva(datos, columnas,parent=self,ventana=self.parent)
            else:
                QMessageBox.warning(self, "Error", "No hay datos cargados.")
        else:
            QMessageBox.warning(self, "Error", "Controlador no asignado.")

    def volverMenu(self):
        self.close()
        if self.parent:
            self.parent.show()

class TablaCSV(QMainWindow):
    def __init__(self, datos, columnas=None, parent=None, controlador=None, desdeBase=False,nombreCSV="grafico",ventana=None):
        super().__init__(parent)
        self.parent = parent
        self.datos = datos
        self.ventana=ventana
        self.columnas = columnas
        self.__controlador = controlador
        self.desdeBase = desdeBase
        self.nombreCSV = nombreCSV

        self.setWindowTitle("Visualizador de Datos Tabulares (.csv)")
        self.setGeometry(400, 150, 800, 600)
        self.setFixedSize(800, 600)

        # --- MODO OSCURO ---
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1E1E2F"))
        palette.setColor(QPalette.WindowText, QColor("#F0F0F0"))
        self.setPalette(palette)
        self.setStyleSheet("""
            QLabel, QComboBox, QTableWidget {
                color: #F0F0F0;
                background-color: #2E2E3A;
                font-size: 14px;
            }
            QPushButton {
                background-color: #00A8CC;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
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

        # --- TABLA ---
        self.tabla = QTableWidget()
        self.layout.addWidget(self.tabla)

        # --- Selector de columnas para graficar ---
        selectorLayout = QHBoxLayout()
        self.comboX = QComboBox()
        self.comboY = QComboBox()

        selectorLayout.addWidget(QLabel("Columna X:"))
        selectorLayout.addWidget(self.comboX)
        selectorLayout.addWidget(QLabel("Columna Y:"))
        selectorLayout.addWidget(self.comboY)
        self.layout.addLayout(selectorLayout)

        # --- Selector de color de puntos ---
        colorLayout = QHBoxLayout()
        self.labelColor = QLabel("Color de puntos:")
        self.comboColor = QComboBox()
        self.colorOptions = ['cyan', 'red', 'green', 'yellow', 'magenta', 'blue', 'orange', 'purple', 'lime', 'pink']
        self.comboColor.addItems(self.colorOptions)
        colorLayout.addWidget(self.labelColor)
        colorLayout.addWidget(self.comboColor)
        self.layout.addLayout(colorLayout)

        # --- Botones de análisis estadístico ---
        self.botonEstadistica = QPushButton("Calcular Estadística")
        self.layout.addWidget(self.botonEstadistica)

        # --- Botones acción ---
        self.botonGraficar = QPushButton("Graficar dispersión")
        self.layout.addWidget(self.botonGraficar)

        self.botonGuardar = QPushButton("Guardar en Base de Datos")
        self.botonGuardar.setEnabled(not self.desdeBase)
        self.layout.addWidget(self.botonGuardar)

        self.botonVolver = QPushButton("Volver")
        self.layout.addWidget(self.botonVolver)

        # --- Conexiones ---
        self.botonGraficar.clicked.connect(self.graficarScatter)
        self.botonGuardar.clicked.connect(self.guardarEnBase)
        self.botonVolver.clicked.connect(self.volver)
        self.botonEstadistica.clicked.connect(self.mostrarEstadisticaDialog)

        # --- Cargar datos iniciales ---
        self.cargarDatosEnTabla()
    def mostrarEstadisticaDialog(self):
        if not self.columnas:
            QMessageBox.warning(self, "Error", "No hay columnas disponibles.")
            return
        dialog = EstadisticaDialog(self.columnas, self)
        if dialog.exec_() == QDialog.Accepted:
            columna, operacion = dialog.getValues()
            idx = self.columnas.index(columna)
            datos_col = self.datos[:, idx]

            # Intentar convertir a float
            try:
                datos_col_float = datos_col.astype(float)
            except ValueError:
                QMessageBox.warning(self, "Error", "La columna seleccionada contiene valores no numéricos o vacíos.")
                return

            # Calcular la estadística
            if operacion == "Promedio":
                resultado = np.mean(datos_col_float)
            elif operacion == "Suma":
                resultado = np.sum(datos_col_float)
            else:
                resultado = "Operación desconocida."

            QMessageBox.information(self, "Resultado", f"{operacion} de '{columna}': {resultado:.2f}")

    def cargarDatosEnTabla(self):
        if hasattr(self.datos, 'shape'):
            rows, cols = self.datos.shape
            self.tabla.setRowCount(rows)
            self.tabla.setColumnCount(cols)
            if self.columnas:
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
                    self.tabla.setItem(i, j, QTableWidgetItem(str(self.datos[i, j])))

    def graficarScatter(self):
        try:
            colX = self.comboX.currentIndex()
            colY = self.comboY.currentIndex()
            x = self.datos[:, colX]
            y = self.datos[:, colY]
            color = self.comboColor.currentText()

            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.scatter(x, y, color=color, alpha=0.7)
            ax.set_xlabel(self.comboX.currentText(), color='white')
            ax.set_ylabel(self.comboY.currentText(), color='white')
            ax.set_title("Gráfico de dispersión", color='white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.grid(True, color='#555')
            nombre_colX = self.comboX.currentText()
            nombre_colY = self.comboY.currentText()
            plt.tight_layout()
            # --- NUEVA VENTANA DE DIÁLOGO ---
            dialog = QDialog(self)
            dialog.setWindowTitle("Vista previa del gráfico")
            dialog.setFixedSize(700, 500)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1E1E2F;
                }
                QPushButton {
                    background-color: #00A8CC;
                    color: white;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #007EA7;
                }
            """)

            layout = QVBoxLayout()
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

            # Botones
            botones = QHBoxLayout()
            btnGuardar = QPushButton("Guardar ")
            btnVolver = QPushButton("Volver")
            btnCerrar = QPushButton("Cerrar")

            botones.addWidget(btnGuardar)
            botones.addWidget(btnVolver)
            botones.addWidget(btnCerrar)
            layout.addLayout(botones)

            dialog.setLayout(layout)

            # Conexiones
            btnGuardar.clicked.connect(lambda: self.__accionGuardarImagen(fig,dialog))
            btnVolver.clicked.connect(dialog.accept)
            btnCerrar.clicked.connect(self.__accionCerrarTodo(dialog))

            # Cerrar la ventana de tabla (self) mientras se abre esta
            self.hide()
            dialog.exec_()
            self.show()
        except Exception as e:
            print("Error al graficar:", e)

    def mostrarPromedio(self):
        try:
            promedios = np.mean(self.datos, axis=0)
            texto = "\n".join(f"{col}: {val:.2f}" for col, val in zip(self.columnas, promedios))
            QMessageBox.information(self, "Promedio de columnas", texto)
        except Exception as e:
            print("Error en promedio:", e)

    def mostrarSuma(self):
        try:
            sumas = np.sum(self.datos, axis=0)
            texto = "\n".join(f"{col}: {val:.2f}" for col, val in zip(self.columnas, sumas))
            QMessageBox.information(self, "Suma de columnas", texto)
        except Exception as e:
            print("Error en suma:", e)
            
    def guardarEnBase(self):
        if not self.__controlador or not self.__controlador.getRutaCSV():
            QMessageBox.warning(self, "Error", "No se conoce la ruta del archivo CSV original.")
            return

        ruta_csv = self.__controlador.getRutaCSV()
        ruta_rel = os.path.relpath(ruta_csv)
        nombre_archivo = os.path.basename(ruta_rel)  # Obtener solo el nombre del archivo

        exito = self.__controlador.guardarCSV(nombre_archivo, ruta_rel)
        if exito:
            QMessageBox.information(self, "Guardado", f"CSV '{nombre_archivo}' guardado en base de datos.")
        else:
            QMessageBox.warning(self, "Duplicado", f"Ya existe un registro con la ruta '{ruta_csv}' en la base de datos.")
    def volver(self):
        self.close()
        if self.ventana:
            self.ventana.show()
    def __accionGuardarImagen(self, fig,dialog):
        try:
            # Crear carpeta si no existe
            carpeta = "img"
            os.makedirs(carpeta, exist_ok=True)

            # Limpiar nombres
            nombre_archivo_base = self.nombreCSV.replace(" ", "_")
            nombre_colX = self.comboX.currentText().replace(" ", "_")
            nombre_colY = self.comboY.currentText().replace(" ", "_")

            # Construir nombre del archivo
            archivo_nombre = f"{nombre_archivo_base}_{nombre_colX}vs{nombre_colY}.png"
            ruta_completa = os.path.join(carpeta, archivo_nombre)

            # Guardar la figura
            fig.savefig(ruta_completa)
            self.__mostrarToast("Imagen guardada correctamente en img/")
            QTimer.singleShot(3000, lambda: self.__volverDesdeToast(dialog))
        except Exception as e:
            QMessageBox.warning(self, "Error al guardar imagen", str(e))
    def __volverDesdeToast(self, dialog):
        dialog.accept()
        self.show()

    def __mostrarToast(self, mensaje):
        # Crear un QLabel temporal
        toast = QLabel(mensaje, self)
        toast.setStyleSheet("""
            background-color: #323232;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
        """)
        toast.setWindowFlags(Qt.ToolTip)

        # Centrarlo o ponerlo abajo
        toast.adjustSize()
        x = (self.width() - toast.width()) // 2
        y = self.height() - toast.height() - 30
        toast.move(x, y)
        toast.show()

        # Quitar después de 3 segundos
        QTimer.singleShot(3000, toast.close)
    def __accionCerrarTodo(self,dialog):
        dialog.accept()
        if self.ventana:
            self.ventana.show()

class EstadisticaDialog(QDialog):
    def __init__(self, columnas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calcular Estadística")
        self.setFixedSize(300, 150)

        self.columnaSeleccionada = None
        self.operacionSeleccionada = None

        layout = QFormLayout()

        self.comboColumna = QComboBox()
        self.comboColumna.addItems(columnas)
        layout.addRow("Columna:", self.comboColumna)

        self.comboOperacion = QComboBox()
        self.comboOperacion.addItems(["Promedio", "Suma"])
        layout.addRow("Operación:", self.comboOperacion)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def getValues(self):
        return self.comboColumna.currentText(), self.comboOperacion.currentText()
 
###################PROCESAMIENTO DE IMAGENES##########################
class ProcesamientoImagenVista(QMainWindow):
    def __init__(self, parent=None, usuario="Desconocido"):
        super().__init__(parent)
        self.parent = parent
        self.usuario = usuario  
        self.setWindowTitle("Procesamiento de Imágenes")
        self.setGeometry(500, 200, 800, 600)
        self.setFixedSize(800, 600)
        self.controlador = None
        self.ruta_imagen = None
        self.imagen_original = None
        self.imagen_procesada = None

        self.setupUI()

    def setControlador(self, c):
        self.controlador = c

    def setupUI(self):
        # Canvas de Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # ComboBox de procesos
        self.comboProceso = QComboBox()
        self.comboProceso.addItems([
            "Conversión a grises",
            "Ecualización",
            "Binarización",
            "Apertura",
            "Cierre",
            "Canny",
            "Conteo de células"
        ])

        self.sliderKernel = QSlider(Qt.Horizontal)
        self.sliderKernel.setRange(1, 20)
        self.sliderKernel.setValue(3)
        self.labelKernel = QLabel("Kernel: 3")

        # Checkbox mostrar/ocultar original
        self.checkboxMostrar = QCheckBox("Mostrar imagen original")
        self.botonCargar = QPushButton("Cargar Imagen")
        self.botonAplicar = QPushButton("Aplicar Proceso")
        self.botonVolver = QPushButton("Volver")

        # Conexiones
        self.botonCargar.clicked.connect(self.cargarImagen)
        self.botonAplicar.clicked.connect(self.aplicarProceso)
        self.botonVolver.clicked.connect(self.volver)
        self.sliderKernel.valueChanged.connect(lambda: self.labelKernel.setText(f"Kernel: {self.sliderKernel.value()}"))
        self.comboProceso.currentTextChanged.connect(self.verificarVisibilidadKernel)
        self.checkboxMostrar.stateChanged.connect(self.actualizarImagenMostrada)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        controles = QHBoxLayout()
        controles.addWidget(QLabel("Proceso:"))
        controles.addWidget(self.comboProceso)
        controles.addWidget(self.sliderKernel)
        controles.addWidget(self.labelKernel)
        controles.addWidget(self.checkboxMostrar)

        botones = QHBoxLayout()
        botones.addWidget(self.botonCargar)
        botones.addWidget(self.botonAplicar)
        botones.addWidget(self.botonVolver)

        layout.addLayout(controles)
        layout.addLayout(botones)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        

    def cargarImagen(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Cargar Imagen", "", "Imágenes (*.jpg *.png)"
        )
        if ruta:
            self.ruta_imagen = ruta
            self.imagen_original = cv2.imread(ruta)
            self.mostrarImagen(self.imagen_original, titulo="Imagen Original")

    def aplicarProceso(self):
        if self.imagen_original is None:
            QMessageBox.warning(self, "Error", "Primero cargue una imagen.")
            return

        proceso = self.comboProceso.currentText()
        kernel_size = self.sliderKernel.value()
        img = self.imagen_original.copy()

        if proceso == "Conversión a grises":
            img_proc = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        elif proceso == "Ecualización":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_proc = cv2.equalizeHist(gray)

        elif proceso == "Binarización":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, img_proc = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        elif proceso == "Apertura":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            img_proc = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

        elif proceso == "Cierre":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            img_proc = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

        elif proceso == "Contornos de imagen":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_proc = cv2.Canny(gray, 100, 200)

        elif proceso == "Conteo de células":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            img_proc = cv2.drawContours(gray.copy(), contours, -1, (255, 0, 0), 2)
            QMessageBox.information(self, "Conteo", f"Células detectadas: {len(contours)}")

        else:
            QMessageBox.warning(self, "Error", "Proceso no reconocido.")
            return

        self.imagen_procesada = img_proc
        if self.checkboxMostrar.isChecked():
            self.mostrarImagen(self.imagen_original, titulo="Imagen Original")
        else: 
            self.mostrarImagen(img_proc, titulo=proceso)
        self.mostrarImagen(img_proc, titulo=proceso)

        # Registro 
        nombre = os.path.basename(self.ruta_imagen) 
        ruta = self.ruta_imagen
        parametros = {"kernel": kernel_size}

        resultado = self.controlador.guardarImagen(
            nombre, ruta, proceso, parametros
        )

        QMessageBox.information(self, "Registro", "Procesamiento guardado correctamente.")
        
    def mostrarImagen(self, img, titulo="Imagen"):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if len(img.shape) == 2:
            ax.imshow(img, cmap="gray")
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ax.imshow(img_rgb)
        ax.set_title(titulo)
        ax.axis("off")
        self.figure.tight_layout()
        self.canvas.draw()

    def volver(self):
        self.close()
        if self.parent:
            self.parent.show()
            
    def verificarVisibilidadKernel(self):
        proceso = self.comboProceso.currentText()
        if proceso in ["Apertura", "Cierre"]:
            self.sliderKernel.show()
            self.labelKernel.show()
        else:
            self.sliderKernel.hide()
            self.labelKernel.hide()

    def actualizarImagenMostrada(self):
    
        if self.imagen_procesada is None:
            return 
        if self.checkboxMostrar.isChecked():
            self.mostrarImagen(self.imagen_original, titulo="Imagen Original")
        else:
            self.mostrarImagen(self.imagen_procesada, titulo="Último Proceso")
