import scipy.io as sio
class ModeloBase:
    def __init__(self, conexion_mongo):
        self.__conexion = conexion_mongo
    def val_usuario(self, usuario, password):
        return self.__conexion.verf_usu(usuario, password)
    def fallos(self, usuario):
        return self.__conexion.fallos(usuario)
    def reg_acceso(self, usuario, exito):
        self.__conexion.reg_acceso(usuario, exito)

    #######MAT######
    def recibirRuta(self,r):
        self.__rutaMAT = r
        print("RUTA EN MODELO "+ self.__rutaMAT)
        ##Añadir a db??

    def devolverLlaves(self):
        archivo = sio.loadmat(self.__rutaMAT)
        ll = archivo.keys()
        return ll
