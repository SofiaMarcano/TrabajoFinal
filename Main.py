from PyQt5.QtWidgets import QApplication
from Vista import LoginVista

import sys

class AppBioMedica:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.vista = LoginVista()

    def ejecute(self):
        self.vista.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    aplicacion = AppBioMedica()
    aplicacion.ejecute()
