import numpy as np
import scipy.io as sio
import pandas as pd
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
        self.__archivo = sio.loadmat(self.__rutaMAT)
        ll = self.__archivo.keys()
        return ll
    
    def verLlave(self,llave):
        valor = self.__archivo[llave]
        if isinstance(valor, np.ndarray):
            return "OK"
        else:
            return "Clave no válida"
    
    def devolverData(self):
        return self.__archivo
    
    def recibirDatos(self,datos):
        self.data = datos
        self.canales = datos.shape[0]
        self.muestras = datos.shape[1]

    def devolverSegmento(self, x_min, x_max):
        if x_min >= x_max:
            return None
        return self.data[:,x_min:x_max]
    def guardarCSV(self, nombre, ruta):
        return self.__conexion.guardar_csv(nombre, ruta)


    def listarCSVs(self):
        return self.__conexion.listar_csvs()


    def cargarCSVporID(self, id_archivo):
        ruta = self.__conexion.obtener_csv_por_id(id_archivo)
        if ruta is None:
            return "ERROR"

        try:
            df = pd.read_csv(ruta)
            columnas = list(df.columns)
            datos = df.to_numpy()
            return datos, columnas
        except Exception as e:
            print(f"Error al leer CSV desde ruta guardada: {e}")
            return "ERROR"
    
    def guardarImagen(self, nombre, ruta, proceso, parametros):
        return self.__conexion.guardar_imagen(nombre, ruta, proceso, parametros)




