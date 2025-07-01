import sys
import numpy as np
import pydicom
import nibabel as nib
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from db import ConexionMongo #Lo importé acá para probar, pero lo mejor sería integrar el script db y el script modelo



# Modelo 🦎 *****************************************************************************

import os
import pydicom
import numpy as np

class ModeloImagenes:
    def cargar_dicom(self, carpeta):
        archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith(".dcm")]
        slices = [pydicom.dcmread(f) for f in archivos]
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        volumen = np.stack([s.pixel_array for s in slices])

        # Metadatos detallados (usa .get para campos que podrían no existir)
        s0 = slices[0]
        info = {
            "PatientName": f"{s0.get('PatientName','')} (Nombre)",
            "PatientID": f"{s0.get('PatientID','')} (ID del Paciente)",
            "PatientSex": f"{s0.get('PatientSex','')} (Sexo)",
            "StudyDate": f"{s0.get('StudyDate','')} (Fecha del Estudio)",
            "Modality": f"{s0.get('Modality','')} (Modalidad)",
            "StudyDescription": f"{s0.get('StudyDescription','')} (Descripción del Estudio)",
            "SeriesDescription": f"{s0.get('SeriesDescription','')} (Descripción de la Serie)",
            "Manufacturer": f"{s0.get('Manufacturer','')} (Fabricante)",
            "PixelSpacing": f"{s0.get('PixelSpacing','')} (Espaciado de Píxeles)",
            "SliceThickness": f"{s0.get('SliceThickness','')} (Grosor del Corte)"
        }
        return volumen, info


    def cargar_nifti(self, ruta):
        nifti = nib.load(ruta)
        volumen = nifti.get_fdata()
        hdr = nifti.header
        info = {
            "dim (Dimensiones del Volumen)": str(hdr.get('dim', 'N/A')),
            "pixdim (Tamaño del Voxel)": str(hdr.get('pixdim', 'N/A')),
            "sform_code / qform_code (Código de Orientación)": f"{hdr.get('sform_code', 'N/A')} / {hdr.get('qform_code', 'N/A')}",
            "descrip (Descripción)": str(hdr.get('descrip', 'N/A')),
            "datatype (Tipo de Dato)": str(hdr.get('datatype', 'N/A')),
            "bitpix (Bits por Píxel)": str(hdr.get('bitpix', 'N/A')),
            "slice_code (Código de Adquisición de Corte)": str(hdr.get('slice_code', 'N/A')),
        }
        return volumen, info

    
    def dicom_a_nifti(self, carpeta, salida):
        volumen, info = self.cargar_dicom(carpeta)
        img_nifti = nib.Nifti1Image(volumen, affine=np.eye(4))
        nib.save(img_nifti, salida)
        return info
    
    def guardar_estudio(self, metadatos):
        mongo = ConexionMongo()
        mongo.guardar_estudio(metadatos)
# ----------------------------------------------------------------------------------------


# Vista 🦎 *****************************************************************************

class VistaImagenes(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("archivosUI/imagenMedicaPanel_ventana.ui", self)

    def mostrar_info_estudio(self, info):
        texto = ""
        for k, v in info.items():
            texto += f"- <b>{k}:</b> {v}<br>"
        self.Info_Estudio.setText(texto)


    def mostrar_imagen(self, img, label):
        if img is None or np.max(img) == np.min(img):
            label.clear()
            return
        img = np.array(img)
        img = ((img - np.min(img)) / (np.max(img) - np.min(img)) * 255).astype(np.uint8)
        h, w = img.shape
        qimg = QImage(img.tobytes(), w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg).scaled(label.width(), label.height())
        label.setPixmap(pixmap)
# ----------------------------------------------------------------------------------------


# Controlador 🦎 *****************************************************************************
class ControladorImagenes:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.volumen = None
        self.info_metadatos = {}
        
        # Conexiones
        self.vista.boton_SubirArchivo.clicked.connect(self.cargar_archivo)
        self.vista.Slider_Axial.valueChanged.connect(self.actualizar_axial)
        self.vista.Slider_Sagital.valueChanged.connect(self.actualizar_sagital)
        self.vista.Slider_Coronal.valueChanged.connect(self.actualizar_coronal)

        self.vista.spinBox_Axial.valueChanged.connect(lambda v: self.vista.Slider_Axial.setValue(v))
        self.vista.spinBox_Sagital.valueChanged.connect(lambda v: self.vista.Slider_Sagital.setValue(v))
        self.vista.spinBox_Coronal.valueChanged.connect(lambda v: self.vista.Slider_Coronal.setValue(v))

        self.vista.boton_Limpiar.clicked.connect(self.limpiar_pantalla)
        self.vista.boton_transf_dcm_nii.clicked.connect(self.transformar_dicom_a_nifti)
        self.vista.boton_GuardarEstudio.clicked.connect(self.guardar_estudio)


    def cargar_archivo(self):
        carpeta = QFileDialog.getExistingDirectory(self.vista, "Seleccionar carpeta DICOM")
        if not carpeta:
            return

        if any(f.endswith(".dcm") for f in os.listdir(carpeta)):
            self.volumen, info = self.modelo.cargar_dicom(carpeta)
        else:
            ruta, _ = QFileDialog.getOpenFileName(self.vista, "Seleccionar NIfTI", "", "NIfTI (*.nii *.nii.gz)")
            if not ruta:
                return
            self.volumen, info = self.modelo.cargar_nifti(ruta)

        self.info_metadatos = info
        self.vista.mostrar_info_estudio(info)
        self.inicializar_sliders()
        self.actualizar_todos_planos()


    def inicializar_sliders(self):
        if self.volumen is None:
            return
        z, y, x = self.volumen.shape

        # Axial
        self.vista.Slider_Axial.setMaximum(z-1)
        self.vista.spinBox_Axial.setMaximum(z-1)
        self.vista.Slider_Axial.setValue(z//2)
        self.vista.spinBox_Axial.setValue(z//2)

        # Sagital
        self.vista.Slider_Sagital.setMaximum(x-1)
        self.vista.spinBox_Sagital.setMaximum(x-1)
        self.vista.Slider_Sagital.setValue(x//2)
        self.vista.spinBox_Sagital.setValue(x//2)

        # Coronal
        self.vista.Slider_Coronal.setMaximum(y-1)
        self.vista.spinBox_Coronal.setMaximum(y-1)
        self.vista.Slider_Coronal.setValue(y//2)
        self.vista.spinBox_Coronal.setValue(y//2)

    def actualizar_todos_planos(self):
        self.actualizar_axial()
        self.actualizar_sagital()
        self.actualizar_coronal()

    def actualizar_axial(self):
        if self.volumen is None:
            return
        idx = self.vista.Slider_Axial.value()
        corte = self.volumen[idx, :, :]
        self.vista.mostrar_imagen(corte, self.vista.plano_Axial)

    def actualizar_sagital(self):
        if self.volumen is None:
            return
        idx = self.vista.Slider_Sagital.value()
        corte = self.volumen[:, :, idx]
        self.vista.mostrar_imagen(corte, self.vista.plano_Sagital)

    def actualizar_coronal(self):
        if self.volumen is None:
            return
        idx = self.vista.Slider_Coronal.value()
        corte = self.volumen[:, idx, :]
        self.vista.mostrar_imagen(corte, self.vista.plano_Coronal)
    
    def limpiar_pantalla(self):
        self.volumen = None
        self.vista.plano_Axial.setText("Plano Axial")
        self.vista.plano_Sagital.setText("Plano Sagital")
        self.vista.plano_Coronal.setText("Plano Coronal")
        self.vista.Info_Estudio.setText("Información del Estudio (metadatos ordenados)\n")
        self.vista.Slider_Axial.setMaximum(0)
        self.vista.Slider_Axial.setValue(0)
        self.vista.spinBox_Axial.setMaximum(0)
        self.vista.spinBox_Axial.setValue(0)
        self.vista.Slider_Sagital.setMaximum(0)
        self.vista.Slider_Sagital.setValue(0)
        self.vista.spinBox_Sagital.setMaximum(0)
        self.vista.spinBox_Sagital.setValue(0)
        self.vista.Slider_Coronal.setMaximum(0)
        self.vista.Slider_Coronal.setValue(0)
        self.vista.spinBox_Coronal.setMaximum(0)
        self.vista.spinBox_Coronal.setValue(0)
        
    def transformar_dicom_a_nifti(self):
        carpeta = QFileDialog.getExistingDirectory(self.vista, "Seleccionar carpeta DICOM a convertir")
        if not carpeta:
            return
        nombre_carpeta = os.path.basename(carpeta)
        ruta_salida = QFileDialog.getSaveFileName(self.vista, "Guardar NIfTI", f"{nombre_carpeta}.nii", "NIfTI (*.nii *.nii.gz)")[0]
        if not ruta_salida:
            return
        try:
            info = self.modelo.dicom_a_nifti(carpeta, ruta_salida)
            self.mostrar_mensaje("Conversión exitosa", "El archivo se creó exitosamente 🦎.")
        except Exception as e:
            self.mostrar_mensaje("Error", f"Ocurrió un error durante la conversión:\n{e}")
    
    def mostrar_mensaje(self, titulo, mensaje):
        mbox = QMessageBox(self.vista)
        mbox.setWindowTitle(titulo)
        mbox.setText(mensaje)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.setIcon(QMessageBox.Information)
        mbox.exec_()
        
    def guardar_estudio(self):
        # Verificar existencia de PatientName en metadatos
        if "PatientName" not in self.info_metadatos or not self.info_metadatos["PatientName"]:
            QMessageBox.warning(None, "Guardar estudio", 
                "No se puede guardar el estudio porque no contiene los metadatos necesarios.\n"
                "Es posible que cargaste un archivo NIfTI que no tiene PatientName.\n"
                "Presiona Limpiar y selecciona un archivo DICOM para continuar😊.")
            return
        # Si pasa la validación, guarda en MongoDB
        self.modelo.guardar_estudio(self.info_metadatos)
        QMessageBox.information(None, "Guardar estudio", "Estudio guardado exitosamente en la base de datos.")
# ----------------------------------------------------------------------------------------
    

# ================================
# MAIN
# ================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vista = VistaImagenes()
    modelo = ModeloImagenes()
    controlador = ControladorImagenes(vista, modelo)
    vista.show()
    sys.exit(app.exec_())


