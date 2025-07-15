from pymongo import MongoClient
import datetime
import pandas as pd
class ConexionMongo:

############################################LOGIN#######################################
    def __init__(self, uri="mongodb://localhost:27017/", db_nombre="Lorosbyte"):
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
                {"usuario": "DanielaLucia", "password": "12345", "tipo_usuario": "imagen"},
                {"usuario": "CarmenLucia", "password": "Plumas1", "tipo_usuario": "senal"},
                {"usuario": "WilliamMora", "password": "Gecko3", "tipo_usuario": "imagenMed"}
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
                    "nombre_archivo": "brain_stoke",
                    "fecha": "20/07/2022",
                    "ruta": r"ArchivosCSV\brain_stroke.csv"
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

    ######################################CSV############################################
    def guardar_csv(self, nombre_archivo, ruta_archivo):
        # Verificar si ya existe esa ruta
        existente = self.__db["registro_archivos"].find_one({
            "tipo_archivo": "csv",
            "ruta": ruta_archivo
        })

        if existente:
            print(f"⚠️ Ya existe en la base de datos con ruta: {ruta_archivo}")
            return False  # Indicar que NO se insertó porque ya existía

        # Insertar nuevo registro
        registro = {
            "id": "ARCH" + str(self.__db["registro_archivos"].count_documents({}) + 1).zfill(3),
            "tipo_archivo": "csv",
            "nombre_archivo": nombre_archivo,
            "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
            "ruta": ruta_archivo
        }
        self.__db["registro_archivos"].insert_one(registro)
        print(f"Insertado nuevo CSV en base con ruta: {ruta_archivo}")
        return True  # Indicar éxito

    def listar_csvs(self):
        cursor = self.__db["registro_archivos"].find({"tipo_archivo": "csv"})
        lista = list(cursor)
        print(f"Listados {len(lista)} CSV en base.")
        return lista

    def obtener_csv_por_id(self, id_archivo):
        doc = self.__db["registro_archivos"].find_one({"id": id_archivo})
        if not doc:
            return None
        return doc

    
#######################################MAT####################################
    def listar_mats(self):
        cursor = self.__db["registro_archivos"].find({"tipo_archivo": "mat"})
        lista = list(cursor)
        print(f"Listados {len(lista)} MAT en base de datos.")
        return lista
    
    def guardar_mat(self, nombre_archivo, ruta_archivo):
        existente = self.__db["registro_archivos"].find_one({
            "tipo_archivo": "mat",
            "ruta": ruta_archivo
        })

        if existente:
            print(f"⚠️ Ya existe en la base de datos con ruta: {ruta_archivo}")
            return False

        registro = {
            "id": "ARCH" + str(self.__db["registro_archivos"].count_documents({}) + 1).zfill(3),
            "tipo_archivo": "mat",
            "nombre_archivo": nombre_archivo,
            "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
            "ruta": ruta_archivo
        }
        self.__db["registro_archivos"].insert_one(registro)
        print(f"Insertado nuevo MAT en base con ruta: {ruta_archivo}")
        return True
    
    def guardar_imagen(self, nombre_archivo, ruta_archivo, proceso, parametros):
        existente = self.__db["registro_archivos_imagenes"].find_one({
            "ruta": ruta_archivo,
            "proceso": proceso
        })

        if existente:
            print("Imagen ya registrada con ese proceso.")
            return False

        registro = {
            "tipo_archivo": "imagen",
            "nombre_archivo": nombre_archivo,
            "ruta": ruta_archivo,
            "proceso": proceso,
            "parametros": parametros
        }

        self.__db["registro_archivos_imagenes"].insert_one(registro)
        print(f"Imagen registrada correctamente en base con ruta: {ruta_archivo}")
        return True
