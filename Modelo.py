import os
import numpy as np
import scipy.io as sio
from scipy.signal import butter, filtfilt
from scipy import signal
from scipy.signal import find_peaks
import pandas as pd
class ModeloBase:
    def __init__(self, conexion_mongo):
        self.__conexion = conexion_mongo

############################################LOGIN###################################################
    def val_usuario(self, usuario, password):
        return self.__conexion.verf_usu(usuario, password)
    def fallos(self, usuario):
        return self.__conexion.fallos(usuario)
    def reg_acceso(self, usuario, exito):
        self.__conexion.reg_acceso(usuario, exito)

#############################################MAT#####################################################
    def recibirRuta(self,ruta):
        self.__rutaMAT = ruta

    def devolverLlaves(self):
        self.__archivo = sio.loadmat(self.__rutaMAT)
        llaves = self.__archivo.keys()
        return llaves
    
    def verLlave(self,llave):
        valor = self.__archivo[llave]
        if isinstance(valor, np.ndarray):
            return "OK"
        else:
            return "Clave no válida"
    
    def devolverData(self,llave):
        self.__data = self.__archivo[llave]
        self.canales, self.muestras, e = self.__data.shape
        self.__continua = np.reshape(self.__data,(self.canales,self.muestras*e), order = "F")
        return self.__data, self.__continua, self.canales, self.muestras, e

    def devolverSegmento(self, x_min, x_max, c = None):
        try:
            if x_min >= x_max:
                return False
            if c == None:
                return self.__continua[:,x_min:x_max]
            else:
                return self.__continua[:c,x_min:x_max]
        except:
            return None
        
    def dDatosSenalProm(self, a,c):
        self.__promedio = np.mean(a[:c, :, :], axis=1)
        self.__promedio = np.mean(self.__promedio, axis=1)
        return self.__promedio

    def getEst(self, c):
        recorte = self.__data[c,:, :]
        señal = recorte.flatten(order='F') 
        promedio = np.round(np.mean(señal), 3)
        desviacion = np.round(np.std(señal), 3)
        return promedio, desviacion
    
    def filtroSenal(self, senal, fs, fc):
        orden = 4
        b, a = butter(orden, fc / (0.5 * fs), btype='low')
        senal_filtrada = filtfilt(b, a, senal)
        return senal_filtrada
    
    def picosSenal(self, c):
        peak_locations, _ = signal.find_peaks(self.__continua[c,:], prominence=0.01)
        return peak_locations
    
    def histSenal(self, epoca):
        datos_epoca = self.__data[:, :, epoca]
        return np.mean(datos_epoca, axis=0)
    
    def listarMATs(self):
        return self.__conexion.listar_mats()
    
    def verRutaMAT(self):
        return os.path.relpath(self.__rutaMAT)
    
    def guardarMAT(self, nombre, ruta):
        return self.__conexion.guardar_mat(nombre, ruta)
    
##################################################CSV################################################
    def guardarCSV(self, nombre, ruta):
        return self.__conexion.guardar_csv(nombre, ruta)

    def listarCSVs(self):
        return self.__conexion.listar_csvs()

    def cargarCSVporID(self, id_archivo):
        registro = self.__conexion.obtener_csv_por_id(id_archivo)
        if registro is None:
            return None, None, None

        ruta = registro["ruta"]
        nombre_archivo = registro["nombre_archivo"]

        try:
            df = pd.read_csv(ruta)
            columnas = list(df.columns)
            datos = df.to_numpy()
            return nombre_archivo, datos, columnas
        except Exception as e:
            print(f"Error al leer CSV desde ruta guardada: {e}")
            return "ERROR"
    
    def guardarImagen(self, nombre, ruta, proceso, parametros):
        return self.__conexion.guardar_imagen(nombre, ruta, proceso, parametros)




