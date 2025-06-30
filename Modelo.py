import numpy as np
import scipy.io as sio
from scipy.signal import butter, filtfilt
from scipy import signal
from scipy.signal import find_peaks
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
    
    def devolverData(self,llave):
        self.__data = self.__archivo[llave]
        c, m, e = self.__data.shape
        self.__continua = np.reshape(self.__data,(c,m*e), order = "F")
        return self.__data, self.__continua, c, m, e
    
    def recibirDatos(self,datos):
        self.data = datos
        self.canales = datos.shape[0]
        self.muestras = datos.shape[1]
        

    def devolverSegmento(self, x_min, x_max, c = None):
        try:
            if x_min >= x_max:
                return False
            if c == None:
                return self.data[:,x_min:x_max]
            else:
                return self.data[:c,x_min:x_max]
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
        return np.mean(datos_epoca, axis=1)