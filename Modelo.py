class ModeloBase:
    def __init__(self, conexion_mongo):
        self._conexion = conexion_mongo

    def validar_usuario(self, usuario, password):
        return self._conexion.verificar_credenciales(usuario, password)