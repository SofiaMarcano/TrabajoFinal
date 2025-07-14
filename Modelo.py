import os
import numpy as np
import scipy.io as sio
from scipy.signal import butter, filtfilt
from scipy import signal
from scipy.signal import find_peaks
import pandas as pd
import pydicom
import nibabel as nib
from nibabel.orientations import aff2axcodes, io_orientation, axcodes2ornt, ornt_transform, apply_orientation, inv_ornt_aff

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
    
    
    ####################################### IMAGEN MÉDICAS ##############################################
    def cargar_dicom(self, carpeta):
        archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith(".dcm")]
        slices = [pydicom.dcmread(f) for f in archivos]
        slices = [s for s in slices if 'PixelData' in s]
        if all(hasattr(s, 'ImagePositionPatient') for s in slices):
            slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        elif all(hasattr(s, 'InstanceNumber') for s in slices):
            slices.sort(key=lambda x: int(x.InstanceNumber))
        volumen = np.stack([s.pixel_array for s in slices])
        s0 = slices[0]
        info = {
            "PatientName": s0.get('PatientName', ''),
            "PatientID": s0.get('PatientID', ''),
            "PatientSex": s0.get('PatientSex', ''),
            "StudyDate": s0.get('StudyDate', ''),
            "Modality": s0.get('Modality', ''),
            "StudyDescription": s0.get('StudyDescription', ''),
            "SeriesDescription": s0.get('SeriesDescription', ''),
            "Manufacturer": s0.get('Manufacturer', ''),
            "PixelSpacing": s0.get('PixelSpacing', ''),
            "SliceThickness": s0.get('SliceThickness', '')
        }
        iop = s0.get('ImageOrientationPatient', None)
        if iop:
            row_cosines = np.array(iop[:3])
            col_cosines = np.array(iop[3:])
            if col_cosines[1] < 0:
                volumen = volumen[:, ::-1, :]
            if row_cosines[0] < 0:
                volumen = volumen[:, :, ::-1]

        return volumen, info

    def cargar_nifti(self, ruta):
        nifti = nib.load(ruta)
        nifti_canon = nib.as_closest_canonical(nifti)
        volumen = nifti_canon.get_fdata()
        if volumen.shape[0] == volumen.shape[1]: # Validar forma y reorganizar si es (x,y,z) en lugar de (z,y,x)
            volumen = np.transpose(volumen, (2,1,0))
            volumen = volumen[::-1, ::-1, :]        
        hdr = nifti_canon.header
        affine = nifti_canon.affine
        from nibabel.orientations import aff2axcodes
        actual_ornt = aff2axcodes(affine)
        info = {
            "dim": str(hdr.get('dim', 'N/A')),
            "pixdim": str(hdr.get('pixdim', 'N/A')),
            "orientacion": str(actual_ornt),
            "sform_code": f"{hdr.get('sform_code', 'N/A')} / {hdr.get('qform_code', 'N/A')}",
            "descrip": str(hdr.get('descrip', 'N/A')),
            "datatype": str(hdr.get('datatype', 'N/A')),
            "bitpix": str(hdr.get('bitpix', 'N/A')),
            "slice_code": str(hdr.get('slice_code', 'N/A'))
        }
        return volumen, info

    def dicom_a_nifti(self, carpeta, salida, metadatos_actualizados=None):
        volumen, info = self.cargar_dicom(carpeta)
        img_nifti = nib.Nifti1Image(volumen, affine=np.eye(4))
        nib.save(img_nifti, salida)
        info["ruta_dicom"] = os.path.abspath(carpeta)
        info["ruta_nifti"] = os.path.abspath(salida)
        if metadatos_actualizados:
            info.update(metadatos_actualizados)
        return info, True, ""
        
    def guardar_estudio(self, metadatos):
        for key, value in metadatos.items():
            if not isinstance(value, (str, int, float, bool, type(None))):
                metadatos[key] = str(value)
        mongo = self.__conexion
        mongo.guardar_estudio(metadatos)
        
    def guardar_estudio_dicom_completo(self, volumen, info_metadatos, sliders, carpeta_base="Img"):
        import os
        import matplotlib.pyplot as plt
        # Validación de metadatos clave
        if "PatientName" not in info_metadatos or not info_metadatos["PatientName"]:
            return False
        
        nombre_estudio = str(info_metadatos["PatientName"])
        carpeta_guardado = os.path.join(carpeta_base, nombre_estudio)
        os.makedirs(carpeta_guardado, exist_ok=True)

        spacing_x = spacing_y = thickness = 1.0
        if "PixelSpacing" in info_metadatos:
            sp = info_metadatos["PixelSpacing"]
            if isinstance(sp, str):
                
                if "[" in sp and "]" in sp:
                    import ast
                    sp = ast.literal_eval(sp)
                else:
                    sp = sp.split("\\")
            spacing_y, spacing_x = map(float, sp)
        if "SliceThickness" in info_metadatos:
            try:
                thickness = float(info_metadatos["SliceThickness"])
            except:
                pass
        cortes = {
            "Axial": volumen[sliders["axial"], :, :],
            "Sagital": volumen[:, :, sliders["sagital"]],
            "Coronal": volumen[:, sliders["coronal"], :]
        }

        # Normalizar y guardar imágenes
        for plano, img in cortes.items():
            img_norm = ((img - img.min()) / (img.max() - img.min()) * 255).astype('uint8')
            if plano == "Axial":
                extent = [0, img.shape[1]*spacing_x, 0, img.shape[0]*spacing_y]
            elif plano == "Sagital":
                extent = [0, img.shape[1]*spacing_y, 0, img.shape[0]*thickness]
            elif plano == "Coronal":
                extent = [0, img.shape[1]*spacing_x, 0, img.shape[0]*thickness]
            plt.imshow(img_norm, cmap='gray', extent=extent)
            plt.axis('off')
            plt.gca().set_aspect('equal')
            ruta = os.path.join(carpeta_guardado, f"{plano}.png")
            plt.savefig(ruta, bbox_inches='tight', pad_inches=0)
            plt.close()

        for key, value in info_metadatos.items():
            if not isinstance(value, (str, int, float, list, dict, bool)):
                info_metadatos[key] = str(value)

        try:
            self.guardar_estudio(info_metadatos)
            return True, carpeta_guardado
        except Exception as e:
            return False, f"Error al guardar en DB: {str(e)}"

    def guardar_estudio_nifti_completo(self, volumen, info_metadatos, sliders, carpeta_base="Img"):
        import matplotlib.pyplot as plt
        if "descrip" not in info_metadatos or not info_metadatos["descrip"]:
            return False
        from datetime import datetime
        base_name = os.path.splitext(os.path.basename(info_metadatos.get("ruta_nifti", "NIfTI.nii")))[0]
        nombre_estudio = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        carpeta_guardado = os.path.join(carpeta_base, nombre_estudio)
        os.makedirs(carpeta_guardado, exist_ok=True)

        spacing_x = spacing_y = spacing_z = 1.0
        cortes = {
            "Axial": volumen[sliders["axial"], :, :],
            "Sagital": volumen[:, :, sliders["sagital"]],
            "Coronal": volumen[:, sliders["coronal"], :]
        }

        for plano, img in cortes.items():
            img_norm = ((img - img.min()) / (img.max() - img.min()) * 255).astype('uint8')
            plt.imshow(img_norm, cmap='gray')
            plt.axis('off')
            plt.gca().set_aspect('equal')
            ruta = os.path.join(carpeta_guardado, f"{plano}.png")
            plt.savefig(ruta, bbox_inches='tight', pad_inches=0)
            plt.close()

        info_metadatos["ruta_cortes"] = carpeta_guardado
        for key, value in info_metadatos.items():
            if not isinstance(value, (str, int, float, list, dict, bool)):
                info_metadatos[key] = str(value)

        try:
            self.guardar_estudio(info_metadatos)
            return True, carpeta_guardado
        except Exception as e:
            return False, f"Error al guardar NIfTI en DB: {str(e)}"



