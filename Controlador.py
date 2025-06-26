from PyQt5.QtWidgets import QMessageBox
from Vista import ImagenVista
from Vista import SenalVista

class LoginControlador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.vista.boton_login.clicked.connect(self._verificar_login)

    def ver_login(self):
        usuario = self.vista.input_usuario.text()
        password = self.vista.input_password.text()
        tipo = self.modelo.validar_usuario(usuario, password)

        if tipo:
            self.vista.close()
            if tipo == "imagen":
                self.panel = ImagenVista()
            else:
                self.panel = SenalVista()
            self.panel.show()
        else:
            QMessageBox.critical(self.vista, "Error", "Usuario o contraseña inválidos.")