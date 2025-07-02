
def rev_num(msj):
    while True:
        try:
            x=int(input(msj))
            return x
        except:
            print("Ingrese un numero entero.")

# class AppBioMedica:
#     def __init__(self):
#         self.app = QApplication(sys.argv)

#         # Conexión e inicialización de MongoDB
#         self.mongo = ConexionMongo()
#         m = self.mongo.ver_o_create()

#         # MVC
#         self.vista = LoginVista()
#         self.modelo = ModeloBase(self.mongo)
#         self.controlador = LoginControlador(self.vista, self.modelo)
#         self.vista.set_controlador(self.controlador)
#         if m:
#             self.controlador.see_inicio(m)

#     def ejecute(self):
#         self.vista.show()
#         sys.exit(self.app.exec_())

# if __name__ == "__main__":
#     aplicacion = AppBioMedica()
#     aplicacion.ejecute()
import sys
from PyQt5.QtWidgets import QApplication
from Vista import LoginVista,Loro
from db import ConexionMongo
from Modelo import ModeloBase
from Controlador import LoginControlador
class AppBioMedica:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Conexión MongoDB
        self.mongo = ConexionMongo()

        # Mostrar INTRO primero
        self.intro = Loro()
        self.intro.terminado.connect(self.iniciar_login)
        self.intro.show()

    def iniciar_login(self):
        m = self.mongo.ver_o_create()

        # Crear MVC para Login
        self.vista = LoginVista()
        self.modelo = ModeloBase(self.mongo)
        self.controlador = LoginControlador(self.vista, self.modelo)
        self.vista.set_controlador(self.controlador)

        if m:
            self.controlador.see_inicio(m)

        self.vista.show()

    def ejecute(self):
        sys.exit(self.app.exec_())
if __name__ == "__main__":
    app_biomedica = AppBioMedica()
    app_biomedica.ejecute()

