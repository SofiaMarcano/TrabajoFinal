import sys
import numpy as np
import pydicom
import nibabel as nib
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from db import ConexionMongo #Lo importé acá para probar, pero lo mejor sería integrar el script db y el script modelo



# Modelo 🦎 *****************************************************************************

import os
import pydicom
import numpy as np

class ModeloImagenesMedicas:
    def cargar_dicom(self, carpeta):
        archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith(".dcm")]
        slices = [pydicom.dcmread(f) for f in archivos]
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))

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
        return volumen, info


    def cargar_nifti(self, ruta):
        import nibabel as nib
        from nibabel.orientations import aff2axcodes, io_orientation, axcodes2ornt, ornt_transform, apply_orientation, inv_ornt_aff
        import numpy as np

        nifti = nib.load(ruta)
        volumen = nifti.get_fdata()
        hdr = nifti.header
        affine = nifti.affine
        actual_ornt = aff2axcodes(affine)
        print("Orientación original:", actual_ornt)

        # Orientación objetivo estándar (RAS)
        target_ornt = ('R', 'A', 'S')
        ornt_current = io_orientation(affine)
        ornt_target = axcodes2ornt(target_ornt)
        transform = ornt_transform(ornt_current, ornt_target)

        # Solo aplica si la orientación actual no es RAS
        if actual_ornt != target_ornt:
            print(f"Reorientando de {actual_ornt} a {target_ornt}")
            volumen = apply_orientation(volumen, transform)
            affine = affine @ inv_ornt_aff(transform, volumen.shape)
            print("Reorientación aplicada.")
        else:
            print("La imagen ya está en RAS, no se aplica reorientación.")

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
        try:
            self.guardar_estudio(info)
            estado_guardado = True
            mensaje_error = ""
        except Exception as e:
            estado_guardado = False
            mensaje_error = str(e)
        return info, estado_guardado, mensaje_error
    
    def guardar_estudio(self, metadatos):
        for key, value in metadatos.items():
            if not isinstance(value, (str, int, float, bool, type(None))):
                metadatos[key] = str(value)
        mongo = ConexionMongo()
        mongo.guardar_estudio(metadatos)        

# ----------------------------------------------------------------------------------------


# Vista 🦎 *****************************************************************************

class VistaImagenesMedicas(QMainWindow):
    def __init__(self, parent= None):
        super().__init__()
        loadUi("archivosUI/imagenMedicaPanel_ventana.ui", self)
        self.mostrar_imagenes_por_defecto()
        self.parent = parent

    def mostrar_info_estudio(self, info):
        traducciones = {
            "PatientName": "Nombre",
            "PatientID": "ID del Paciente",
            "PatientSex": "Sexo",
            "StudyDate": "Fecha del Estudio",
            "Modality": "Modalidad",
            "StudyDescription": "Descripción del Estudio",
            "SeriesDescription": "Descripción de la Serie",
            "Manufacturer": "Fabricante",
            "PixelSpacing": "Espaciado de Píxeles",
            "SliceThickness": "Grosor del Corte",
            "dim": "Dimensiones del Volumen",
            "pixdim": "Tamaño del Voxel",
            "sform_code": "Código de Orientación",
            "descrip": "Descripción",
            "datatype": "Tipo de Dato",
            "bitpix": "Bits por Píxel",
            "slice_code": "Código de Adquisición de Corte" }
        texto = ""
        for k, v in info.items():
            significado = traducciones.get(k, k)
            texto += f"- <b>{k} ({significado}):</b> {v}<br>"
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
    def volver(self):
        self.close()
        if self.parent() is not None:
            self.parent().show()
    
    def mostrar_imagenes_por_defecto(self):
        ruta_base = os.path.dirname(__file__)
        ruta_axial = os.path.join(ruta_base, "img", "img_dummies_planosAnatomicos", "axial.jpg")
        ruta_sagital = os.path.join(ruta_base, "img", "img_dummies_planosAnatomicos", "sagital.jpg")
        ruta_coronal = os.path.join(ruta_base, "img", "img_dummies_planosAnatomicos", "coronal.jpg")
        self.mostrar_imagen_archivo(ruta_axial, self.plano_Axial)
        self.mostrar_imagen_archivo(ruta_sagital, self.plano_Sagital)
        self.mostrar_imagen_archivo(ruta_coronal, self.plano_Coronal)
    def mostrar_imagen_archivo(self, ruta, label):
        pixmap = QPixmap(ruta)#.scaled(label.width(), label.height(), Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        
    def mostrar_mensaje(self, titulo, mensaje):
        mbox = QMessageBox(self)
        mbox.setWindowTitle(titulo)
        mbox.setText(mensaje)
        mbox.setIcon(QMessageBox.Information)
        mbox.exec_()

    def mostrar_advertencia(self, titulo, mensaje):
        mbox = QMessageBox(self)
        mbox.setWindowTitle(titulo)
        mbox.setText(mensaje)
        mbox.setIcon(QMessageBox.Warning)
        mbox.exec_()
       
class ModificarMetadatos(QDialog):
    def __init__(self, info_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Metadatos")
        self.resize(300, 200)

        # Crear widgets manualmente sin .ui
        from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox

        layout = QVBoxLayout()

        # Nombre
        layout_nombre = QHBoxLayout()
        layout_nombre.addWidget(QLabel("Nombre:"))
        self.lineEdit_Nombre = QLineEdit(str(info_actual.get("PatientName", "")))
        layout_nombre.addWidget(self.lineEdit_Nombre)
        layout.addLayout(layout_nombre)

        # ID
        layout_id = QHBoxLayout()
        layout_id.addWidget(QLabel("ID:"))
        self.lineEdit_ID = QLineEdit(str(info_actual.get("PatientID", "")))
        layout_id.addWidget(self.lineEdit_ID)
        layout.addLayout(layout_id)

        # Sexo
        layout_sexo = QHBoxLayout()
        layout_sexo.addWidget(QLabel("Sexo:"))
        self.comboBox_Sexo = QComboBox()
        self.comboBox_Sexo.addItems(["M", "F", "O"])
        self.comboBox_Sexo.setCurrentText(str(info_actual.get("PatientSex", "")))
        layout_sexo.addWidget(self.comboBox_Sexo)
        layout.addLayout(layout_sexo)

        # Descripción
        layout_descrip = QHBoxLayout()
        layout_descrip.addWidget(QLabel("Descripción:"))
        self.lineEdit_descrip = QLineEdit(str(info_actual.get("StudyDescription", "")))
        layout_descrip.addWidget(self.lineEdit_descrip)
        layout.addLayout(layout_descrip)

        # Botones
        layout_botones = QHBoxLayout()
        self.boton_Guardar = QPushButton("Guardar")
        self.boton_Cancelar = QPushButton("Cancelar")
        layout_botones.addWidget(self.boton_Guardar)
        layout_botones.addWidget(self.boton_Cancelar)
        layout.addLayout(layout_botones)

        self.setLayout(layout)

        # Conexiones
        self.boton_Guardar.clicked.connect(self.accept)
        self.boton_Cancelar.clicked.connect(self.reject)

    def obtener_datos(self):
        return {
            "PatientName": self.lineEdit_Nombre.text(),
            "PatientID": self.lineEdit_ID.text(),
            "PatientSex": self.comboBox_Sexo.currentText(),
            "StudyDescription": self.lineEdit_descrip.text()
        }

# ----------------------------------------------------------------------------------------


# Controlador 🦎 *****************************************************************************

class ControladorImagenesMedicas:
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
        
        self.vista.boton_volver.clicked.connect(self.vista.volver)
        self.vista.boton_Limpiar.clicked.connect(self.limpiar_pantalla)
        self.vista.boton_transf_dcm_nii.clicked.connect(self.transformar_dicom_a_nifti)
        self.vista.boton_GuardarEstudio.clicked.connect(self.guardar_estudio)
        self.vista.boton_ModificarMetadatos.clicked.connect(self.modificar_metadatos)
        
        self.vista.boton_ModificarMetadatos.setEnabled(False)
        self.vista.boton_transf_dcm_nii.setEnabled(False) 

    def cargar_archivo(self):
        carpeta = QFileDialog.getExistingDirectory(self.vista, "Seleccionar carpeta DICOM")
        if not carpeta:
            return

        if any(f.endswith(".dcm") for f in os.listdir(carpeta)):
            self.volumen, info = self.modelo.cargar_dicom(carpeta)
            self.ruta_dicom = os.path.abspath(carpeta)
            self.ruta_nifti = None    
            self.vista.boton_ModificarMetadatos.setEnabled(True)
            self.vista.boton_transf_dcm_nii.setEnabled(True)                 
        else:
            ruta, _ = QFileDialog.getOpenFileName(self.vista, "Seleccionar NIfTI", "", "NIfTI (*.nii *.nii.gz)")
            if not ruta:
                return
            self.volumen, info = self.modelo.cargar_nifti(ruta)
            self.ruta_nifti = os.path.abspath(ruta)    
            self.ruta_dicom = None   
            self.vista.boton_ModificarMetadatos.setEnabled(False) 
            self.vista.boton_transf_dcm_nii.setEnabled(False)                   

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
        self.vista.mostrar_imagenes_por_defecto()
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
        if not self.ruta_dicom:
            QMessageBox.warning(None, "Transformación DICOM-NIfTI", 
                "Debes cargar primero un archivo DICOM antes de convertirlo a NIfTI.")
            return

        nombre_carpeta = os.path.basename(self.ruta_dicom)
        ruta_salida, _ = QFileDialog.getSaveFileName(self.vista, "Guardar NIfTI", f"{nombre_carpeta}.nii", "NIfTI (*.nii *.nii.gz)")
        if not ruta_salida:
            return

        try:
            info, guardado, mensaje_error = self.modelo.dicom_a_nifti(self.ruta_dicom, ruta_salida, self.info_metadatos)
            
            if guardado:
                msg = (f"✅ Conversión exitosa.\n\n"
                    f"🗂 Ruta carpeta DICOM:\n{info['ruta_dicom']}\n\n"
                    f"🧠 Ruta NIfTI generado:\n{info['ruta_nifti']}")
                self.vista.mostrar_mensaje("Conversión y guardado exitoso", msg)
            else:
                msg = (f"✅ La conversión a NIfTI se realizó correctamente.\n\n"
                    f"❌ Sin embargo, no se pudieron guardar los metadatos en MongoDB.\n\n"
                    f"Detalles del error:\n{mensaje_error}")
                self.vista.mostrar_advertencia("Error al guardar en MongoDB", msg)
        
        except Exception as e:
            self.vista.mostrar_advertencia("Error durante la conversión", f"Ocurrió un error inesperado:\n{str(e)}")
        
    def modificar_metadatos(self):
        if not self.ruta_dicom:
            QMessageBox.warning(None, "Modificar metadatos", 
                "Solo puedes modificar metadatos si cargaste un archivo DICOM.")
            return

        dialogo = ModificarMetadatos(self.info_metadatos, self.vista)
        if dialogo.exec_():  # Si presionó Guardar
            nuevos_datos = dialogo.obtener_datos()
            self.info_metadatos.update(nuevos_datos)  # Actualiza en memoria
            self.vista.mostrar_info_estudio(self.info_metadatos)  # Actualiza en pantalla

        
    def guardar_estudio(self):
        if "PatientName" not in self.info_metadatos or not self.info_metadatos["PatientName"]:
            QMessageBox.warning(None, "Guardar estudio", 
                "No se puede guardar el estudio porque no contiene los metadatos necesarios.\n"
                "Posiblemente cargaste un archivo NIfTI que no tiene por ejemplo PatientName,\n"
                "Presiona Limpiar y selecciona un archivo DICOM para continuar😊.")
            return
        self.info_metadatos["ruta_dicom"] = self.ruta_dicom if hasattr(self, "ruta_dicom") else None
        self.info_metadatos["ruta_nifti"] = self.ruta_nifti if hasattr(self, "ruta_nifti") else None
        nombre_estudio = str(self.info_metadatos["PatientName"])
        carpeta_guardado = os.path.join("Img", nombre_estudio)
        os.makedirs(carpeta_guardado, exist_ok=True)
        spacing_x = spacing_y = thickness = 1.0  
        if "PixelSpacing" in self.info_metadatos:
            sp = self.info_metadatos["PixelSpacing"]
            if isinstance(sp, str):
                sp = sp.split("\\")
            spacing_y, spacing_x = map(float, sp)
        if "SliceThickness" in self.info_metadatos:
            try:
                thickness = float(self.info_metadatos["SliceThickness"])
            except:
                pass
        cortes = {
            "Axial": self.volumen[self.vista.Slider_Axial.value(), :, :],
            "Sagital": self.volumen[:, :, self.vista.Slider_Sagital.value()],
            "Coronal": self.volumen[:, self.vista.Slider_Coronal.value(), :]
        }
        for key, value in self.info_metadatos.items():
            if not isinstance(value, (str, int, float, list, dict, bool)):
                self.info_metadatos[key] = str(value)
        import matplotlib.pyplot as plt
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
        try:
            self.modelo.guardar_estudio(self.info_metadatos)
            QMessageBox.information(None, "Guardar estudio", 
                f"Estudio guardado exitosamente en la base de datos y cortes guardados en:\n{carpeta_guardado}")
        except Exception as e:
            QMessageBox.warning(None, "Guardar estudio", 
                f"✅ Las imágenes se guardaron en:\n{carpeta_guardado}\n\n"
                "❌ No se pudieron subir los metadatos a MongoDB o ocurrió otro error.\n"
                f"\nDetalles:\n{str(e)}")
# ----------------------------------------------------------------------------------------
    

# ================================
# MAIN
# ================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vista = VistaImagenesMedicas()
    modelo = ModeloImagenesMedicas()
    controlador = ControladorImagenesMedicas(vista, modelo)
    vista.show()
    sys.exit(app.exec_())


