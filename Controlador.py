from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
# from Vista import ImagenVista
# from Vista import SenalVista
class LoginControlador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.vista.boton_login.clicked.connect(self.ver_login) ## Conectar el botón de login con el método que valida el acceso

    def ver_login(self):
        self.vista.espera()
        try:
            usuario = self.vista.input_usuario.text()
            password = self.vista.input_password.text()

            if not usuario or not password:
                self.vista.error("Por favor, ingrese usuario y contraseña.")
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
                QTimer.singleShot(3000, self.vista.close)  # Espera 3 segundos antes de cerrar

                # Aquí abrirías la vista correspondiente, por ejemplo:
                # if tipo == "imagen":
                #     self.panel = ImagenVista()
                # else:
                #     self.panel = SenalVista()
                # self.panel.show()
            else:
                self.vista.error(f"Usuario o contraseña incorrectos.\nIntentos fallidos recientes: {fallos}/5")
                self.vista.clear()

        except Exception as e:
            self.vista.error(f"Error: {str(e)}")

        finally:
            self.vista.normal()
    def see_inicio(self, mensajes):
        # Mostrar mensajes de inicio como la creación de base de datos con tiempo
        delay = 1000
        for msg in mensajes:
            QTimer.singleShot(delay, lambda m=msg: self.vista.error(m))
            delay += 2000
