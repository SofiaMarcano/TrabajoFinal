from PyQt5.QtWidgets import QMessageBox, QInputDialog, QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtMultimedia import QSound
import pandas as pd
from Vista import CCSV,TablaCSV, ProcesamientoImagenVista, senalesMenuVista, ImagenMenuVista
import numpy as np
import os
from datetime import datetime

# from Vista import ImagenVista

class LoginControlador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self._datosCSV = None
        self._columnasCSV = []
        self._rutaCSV = None 
        self._cargadoDesdeBase = False

        self.vista.boton_login.clicked.connect(self.ver_login) ## Conectar el botón de login con el método que valida el acceso

##########################################LOGIN###############################################################

    def ver_login(self):
        self.vista.espera()
        try:
            usuario = self.vista.input_usuario.text()
            password = self.vista.input_password.text()

            if not usuario or not password:
                self.vista.error("Por favor, ingrese usuario y contraseña.")
                self.cositas()
                return

            fallos = self.modelo.fallos(usuario)
            if fallos >= 5:
                self.modelo.reg_acceso(usuario, False)
                self.vista.error("Ha superado el número de intentos permitidos.\nEspere unos minutos antes de volver a intentarlo.")
                self.vista.clear()
                return

            tipo = self.modelo.val_usuario(usuario, password)
            self.modelo.reg_acceso(usuario, tipo is not None)

            if tipo:
                self.vista.error(f" 🐱Bienvenido, acceso como usuario tipo: {tipo}")
                self.vista.normal()
                QTimer.singleShot(3000, lambda: self.abrirVista(tipo))  # Espera 3 segundos antes de cerrar

            else:
                self.vista.error(f"Usuario o contraseña incorrectos.\nIntentos fallidos recientes: {fallos}/5")
                self.vista.clear()
        except Exception as e:
            self.vista.error(f"Error: {str(e)}")

        finally:
            self.vista.normal()
            
    def abrirVista(self,tipo):
        self.vista.close()
        if tipo == "imagen":
            self.panel = ImagenMenuVista(self.vista)
            self.panel.setControlador(self)
            self.panel.show()
        elif tipo == "senal":
            self.panel = senalesMenuVista(self.vista)
            self.panel.setControlador(self)
            self.panel.show()

    def see_inicio(self, mensajes):
        # Mostrar mensajes de inicio como la creación de base de datos con tiempo
        delay = 1000
        for msg in mensajes:
            QTimer.singleShot(delay, lambda m=msg: self.vista.error(m))
            delay += 2000
        QTimer.singleShot(delay, lambda: (self.vista.clear(), self.vista.error(""))) 
    def cositas(self):
        self.easteregg_window = QWidget()
        self.easteregg_window.setWindowTitle("Ingresa bien!!!")
        self.easteregg_window.setGeometry(600, 250, 550, 440)
        self.easteregg_window.setStyleSheet("""
            background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #1A0023, stop:1 #FF44CC
            );
            border: 4px solid #FF00CC;
        """)

        # Saludo por hora
        hora_actual = QTime.currentTime().hour()
        if hora_actual < 6:
            saludo = "¡Muy temprano para fallar!"
        elif hora_actual < 12:
            saludo = "¡Buenos días, intenta bien!"
        elif hora_actual < 18:
            saludo = "¡Vamos hazlo bien, aún es de día!"
        else:
            saludo = "¡De noche y aún errando!"

        # Texto animado
        self.texto_label = QLabel(saludo)
        self.texto_label.setFont(QFont("Consolas", 18, QFont.Bold))
        self.texto_label.setAlignment(Qt.AlignCenter)
        self.texto_label.setStyleSheet("""
            color: #00FFFF;
            background-color: rgba(0,0,0,180);
            border: 2px dashed #39FF14;
            padding: 12px;
            border-radius: 10px;
        """)

        # Imagen con glow
        label_img = QLabel()
        pixmap = QPixmap(r"img\Img22.jpg")
        if pixmap.isNull():
            label_img.setText("Imagen no encontrada.")
            label_img.setAlignment(Qt.AlignCenter)
        else:
            label_img.setPixmap(pixmap.scaled(420, 270, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label_img.setAlignment(Qt.AlignCenter)
            label_img.setStyleSheet("""
                border: 3px solid #FF00FF;
                padding: 6px;
                background-color: black;
            """)
            glow = QGraphicsDropShadowEffect()
            glow.setBlurRadius(30)
            glow.setColor(QColor("#00FFFF"))
            glow.setOffset(0)
            label_img.setGraphicsEffect(glow)

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(self.texto_label)
        layout.addWidget(label_img)
        self.easteregg_window.setLayout(layout)

        # Mostrar y cerrar login
        self.vista.close()
        self.easteregg_window.show()

        # 🔊 Sonido arcade
        self.sonido_easteregg = QSound(r"img\img56.wav")
        self.sonido_easteregg.play()
        self.colores = ["#00FFFF", "#FF00FF", "#FFFF00", "#FF4444", "#00FF00", "#FFA500"]
        self.color_index = 0
        self.timer_color = QTimer()
        self.timer_color.timeout.connect(self.cambiar_color_texto)
        self.timer_color.start(300)

        # Reabrir login
        QTimer.singleShot(4000, self.reabrir_login)

    def cambiar_color(self):
        color = self.colores[self.color_index]
        estilo = f"""
            color: {color};
            background-color: rgba(0,0,0,180);
            border: 2px dashed #39FF14;
            padding: 12px;
            border-radius: 10px;
        """
        self.texto_label.setStyleSheet(estilo)
        self.color_index = (self.color_index + 1) % len(self.colores)

    def reabrir_login(self):
        if hasattr(self, "sonido_easteregg"):
            self.sonido_easteregg.stop()
        self.easteregg_window.close()
        self.vista.clear()
        self.vista.show()


####################################################MAT#########################################################

    def recibirRuta(self,ruta):
        self.modelo.recibirRuta(ruta)
    
    def llevarLlaves(self):
        return self.modelo.devolverLlaves()
    
    def verificarLlave(self,llave):
        return self.modelo.verLlave(llave)
    
    def llevarDatos(self, llave):
        return self.modelo.devolverData(llave)

    def devolverDatosSenal(self,min,max,c=None):
        return self.modelo.devolverSegmento(min, max,c)
    
    def devolverDatosSenalProm(self, a, c):
        return self.modelo.dDatosSenalProm(a, c)
    
    def getEstSenal(self, c=0):
        return self.modelo.getEst(c)

    def llevarFiltro(self,s, fs=1000, fc=10):
        return self.modelo.filtroSenal(s, fs, fc)
    
    def llevarPicos(self, c=0):
        return self.modelo.picosSenal(c)
    
    def llevarHist(self, e=0):
        return self.modelo.histSenal(e)
    
    def guardar(self, fig):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"grafico_{timestamp}.png"
            carpeta_salida = "graficosMAT"
            os.makedirs(carpeta_salida, exist_ok=True)
            ruta = os.path.join(carpeta_salida, nombre_archivo)
            fig.savefig(ruta)
            return True

        except Exception as e:
            print("Error al guardar gráfico:", e)
            return False
            
    def listarMATs(self):
        return self.modelo.listarMATs()
    
    def devolverRutaMAT(self):
        return self.modelo.verRutaMAT()
    
    def guardarBD(self, nombre, ruta):
        resultado = self.modelo.guardarMAT(nombre, ruta)
        return resultado
    
####################################################CSV######################################################

    def setCargadoDesdeBase(self, valor: bool):
        self._cargadoDesdeBase = valor
    def setNombreCSV(self, nombre_csv):
        self._nombreCSV = nombre_csv

    
    def procesarCSV(self, ruta):
        try:
            df = pd.read_csv(ruta)
            self._datosCSV = df.to_numpy()
            self._columnasCSV = list(df.columns)
            self._rutaCSV = ruta       
            return "OK"
        except Exception as e:
            print("Error al procesar CSV:", e)
            return "ERROR"

    def getRutaCSV(self):
        return os.path.relpath(self._rutaCSV)
    
    def cargarCSVporID(self, id_archivo):
        nombre, datos, columnas = self.modelo.cargarCSVporID(id_archivo)
        if nombre is None or datos is None or columnas is None:
            return "ERROR"

        self._datosCSV = datos
        self._columnasCSV = columnas
        self._nombreCSV = nombre
        self._cargadoDesdeBase = True

        print(f"✅ CSV cargado desde base (ID: {id_archivo}), nombre: {nombre}")
        return (nombre, datos, columnas)


    def obtenerDatosCSV(self):
        return self._datosCSV

    def obtenerColumnasCSV(self):
        return self._columnasCSV

    def listarCSVs(self):
        return self.modelo.listarCSVs()
    
    def TablaEnNueva(self,datos,columnas,parent,ventana):
        import os
        if self._nombreCSV:
            nombre_csv_base = os.path.splitext(os.path.basename(self._nombreCSV))[0]
        elif self._rutaCSV:
            nombre_csv_base = os.path.splitext(os.path.basename(self._rutaCSV))[0]

        else:
            nombre_csv_base = "grafico"

        self.vistaTabla = TablaCSV(
            datos, columnas,
            parent=parent,
            controlador=self,
            desdeBase=self._cargadoDesdeBase,
            nombreCSV=nombre_csv_base,
            ventana=ventana
        )
        self.vistaTabla.show()
        
    def guardarCSV(self, nombre, ruta):
        resultado = self.modelo.guardarCSV(nombre, ruta)
        return resultado
    def getDatosColumnas(self):
        return self._datosCSV, self._columnasCSV

    def guardarImagen(self, nombre, ruta, proceso, parametros):
        resultado = self.modelo.guardarImagen(nombre, ruta, proceso, parametros)
        return resultado







    



    



