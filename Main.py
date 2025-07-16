####### LINK GITHUB #####
##### INTEGRANTES
### https://github.com/SofiaMarcano/TrabajoFinal.git

def rev_num(msj):
    while True:
        try:
            x=int(input(msj))
            return x
        except:
            print("Ingrese un numero entero.")


import sys
from PyQt5.QtWidgets import QApplication
from Vista import LoginVista, Loro
from db import ConexionMongo
from Modelo import ModeloBase
from Controlador import Controlador

class AppBioMedica:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Conexión MongoDB
        # Conexión MongoDB
        self.mongo = ConexionMongo()

        # Crear una sola vez el MVC para Login
        # Crear una sola vez el MVC para Login
        self.vista = LoginVista()
        self.modelo = ModeloBase(self.mongo)
        self.controlador = Controlador(self.vista, self.modelo)
        self.vista.set_controlador(self.controlador)

        # Mostrar INTRO primero
        self.intro = Loro()
        self.intro.terminado.connect(self.iniciar_login)
        self.intro.show()

    def iniciar_login(self):
        # Verifica en Mongo si hay sesión previa
        m = self.mongo.ver_o_create()


        # Mostrar INTRO primero
        self.intro = Loro()
        self.intro.terminado.connect(self.iniciar_login)
        self.intro.show()

    def iniciar_login(self):
        # Verifica en Mongo si hay sesión previa
        m = self.mongo.ver_o_create()

        if m:
            self.controlador.see_inicio(m)

        self.vista.show()

    def ejecute(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app_biomedica = AppBioMedica()
    app_biomedica.ejecute()
    app_biomedica = AppBioMedica()
    app_biomedica.ejecute()

