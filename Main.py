import sys
from PyQt5.QtWidgets import QApplication
from Vista import LoginVista
from db import ConexionMongo
from Modelo import ModeloBase
from Controlador import LoginControlador

class AppBioMedica:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Conexión e inicialización de MongoDB
        self.mongo = ConexionMongo()
        self.mongo.ver_o_create()

        # MVC
        self.vista = LoginVista()
        self.modelo = ModeloBase(self.mongo)
        self.vista = LoginVista()
        self.controlador = LoginControlador(self.vista, self.modelo)
        self.vista.set_controlador(self.controlador)

    def ejecute(self):
        self.vista.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    aplicacion = AppBioMedica()
    aplicacion.ejecute()

