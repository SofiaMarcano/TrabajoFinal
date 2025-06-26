class ModeloBase:
    def __init__(self, conexion_mongo):
        self.__conexion = conexion_mongo
    def val_usuario(self, usuario, password):
        return self.__conexion.verf_usu(usuario, password)
    def fallos(self, usuario):
        return self.__conexion.fallos(usuario)
    def reg_acceso(self, usuario, exito):
        self.__conexion.reg_acceso(usuario, exito)
