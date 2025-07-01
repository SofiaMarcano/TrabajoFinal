from pymongo import MongoClient
import datetime

class ConexionMongo:
    def __init__(self, uri="mongodb://localhost:27017/", db_nombre="bioapp"):
        self.__cliente = MongoClient(uri)
        self.__db = self.__cliente[db_nombre]
        self.__usuarios = self.__db["usuarios"]

    def verf_usu(self, u, p):
        doc = self.__usuarios.find_one({"usuario": u, "password": p})
        if doc:
            return doc.get("tipo_usuario")
        return None

    def ver_o_create(self):
        print("Verificando base de datos 🐱...")
        m=[]
        # Crear usuarios
        if self.__db["usuarios"].count_documents({}) == 0:
            print("La base de datos no encontrada. Creando datos de ejemplo...")
            self.__db["usuarios"].insert_many([
                {"usuario": "WilliamMora", "password": "12345", "tipo_usuario": "imagen"},
                {"usuario": "CarmenLucia", "password": "Plumas1", "tipo_usuario": "senal"}
            ])
            m.append("Base de datos inicializada con usuarios.")

        # Crear estudio ejemplo
        if self.__db["estudios"].count_documents({}) == 0:
            self.__db["estudios"].insert_one({
                "paciente": {
                    "id": "PAC001",
                    "nombre": "Elizabeth Gonzales",
                    "edad": "30",
                    "sexo": "Femenino"
                },
                "tipo_archivo": "DICOM",
                "ruta_dicom": r"archivosDICOM\img1",
                "ruta_nifti": r"archivosNIFTI\img1.nii.gz",
                "fecha_carga":"25/06/2020"
            })
            m.append("Cargado estudio de prueba.")

        # Crear registro_archivos ejemplo
        if self.__db["registro_archivos"].count_documents({}) == 0:
            m.append("Cargados archivos de ejemplo (csv, mat).")
            self.__db["registro_archivos"].insert_many([
                {
                    "id": "ARCH001",
                    "tipo_archivo": "mat",
                    "nombre_archivo": "enfermo",
                    "fecha": "20/06/2021",
                    "ruta": r"archivosMAT\enfermo.mat"
                },
                {
                    "id": "ARCH002",
                    "tipo_archivo": "csv",
                    "nombre_archivo": "datos.csv",
                    "fecha": "20/07/2022",
                    "ruta": r"C:/archivos/datos.csv"
                }
            ])
        return m
    def reg_acceso(self, usuario, exito):
        self.__db["accesos"].insert_one({
            "usuario": usuario,
            "exito": exito,
            "fecha": datetime.datetime.now()
        })
    def fallos(self, usuario, minutos=10):
        #cuantos intentos fallidos de inicio de sesión ha hecho un usuario en los últimos 10 minutos
        limite = datetime.datetime.now() - datetime.timedelta(minutes=minutos) #si ahora es 14:20, limite será 14:10.
        return self.__db["accesos"].count_documents({
            "usuario": usuario,
            "exito": False,
            "fecha": {"$gte": limite} #La fecha es mayor o igual a limite
        })
    
    def guardar_estudio(self, info_dict):
        self.__db["estudios"].insert_one(info_dict)

