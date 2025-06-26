class ModeloBase:
    def __init__(self, conexion_mongo):
        self.__conexion = conexion_mongo

    def validar_usuario(self, usuario, password):
        return self._conexion.verificar_usu(usuario, password)
    def reg_acceso(self, usuario, exito):
        self.__conexion.reg_acceso(usuario, exito)