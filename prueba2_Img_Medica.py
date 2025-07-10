# ========================
# modelo.py
# ========================

import os
import numpy as np
import pydicom
import nibabel as nib
from db import ConexionMongo  # Asegúrate de tener tu clase de conexión


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
        nifti = nib.load(ruta)
        volumen = nifti.get_fdata()
        hdr = nifti.header
        affine = nifti.affine
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
        mongo = ConexionMongo()
        mongo.guardar_estudio(metadatos)
        
    def guardar_estudio_completo(self, volumen, info_metadatos, sliders, carpeta_base="Img"):
        import os
        import matplotlib.pyplot as plt
        # Validación de metadatos clave
        if "PatientName" not in info_metadatos or not info_metadatos["PatientName"]:
            return False, 
        """No se puede guardar el estudio porque no contiene los metadatos necesarios.
        Posiblemente cargaste un archivo NIfTI que no tiene por ejemplo PatientName,
        Presiona Limpiar y selecciona un archivo DICOM para continuar😊."""

        nombre_estudio = str(info_metadatos["PatientName"])
        carpeta_guardado = os.path.join(carpeta_base, nombre_estudio)
        os.makedirs(carpeta_guardado, exist_ok=True)

        spacing_x = spacing_y = thickness = 1.0
        if "PixelSpacing" in info_metadatos:
            sp = info_metadatos["PixelSpacing"]
            if isinstance(sp, str):
                
                if "[" in sp and "]" in sp:
                    import ast
                    sp = ast.literal_eval(sp) #Verifica si es un string de lista python y evalúalo con ast.literal_eval
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

        # Guardar en base de datos
        for key, value in info_metadatos.items():
            if not isinstance(value, (str, int, float, list, dict, bool)):
                info_metadatos[key] = str(value)

        try:
            self.guardar_estudio(info_metadatos)
            return True, carpeta_guardado
        except Exception as e:
            return False, f"Error al guardar en DB: {str(e)}"


# ========================
# vista.py
# ========================

import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

class VistaImagenesMedicas(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        loadUi("archivosUI/imagenMedicaPanel_ventana.ui", self)
        self.__controlador = None
        self.mostrar_imagenes_por_defecto()

    def setControlador(self, c):
        self.__controlador = c
        self.setup_connections()

    def setup_connections(self):
        self.boton_SubirArchivo.clicked.connect(self.__controlador.cargar_archivo)
        self.Slider_Axial.valueChanged.connect(self.__controlador.actualizar_axial)
        self.Slider_Sagital.valueChanged.connect(self.__controlador.actualizar_sagital)
        self.Slider_Coronal.valueChanged.connect(self.__controlador.actualizar_coronal)
        self.spinBox_Axial.valueChanged.connect(lambda v: self.Slider_Axial.setValue(v))
        self.spinBox_Sagital.valueChanged.connect(lambda v: self.Slider_Sagital.setValue(v))
        self.spinBox_Coronal.valueChanged.connect(lambda v: self.Slider_Coronal.setValue(v))
        self.boton_volver.clicked.connect(self.volver)
        self.boton_Limpiar.clicked.connect(self.__controlador.limpiar_pantalla)
        self.boton_transf_dcm_nii.clicked.connect(self.__controlador.transformar_dicom_a_nifti)
        self.boton_GuardarEstudio.clicked.connect(self.__controlador.guardar_estudio)
        self.boton_ModificarMetadatos.clicked.connect(self.__controlador.modificar_metadatos)
        
        self.boton_ModificarMetadatos.setEnabled(False)
        self.boton_transf_dcm_nii.setEnabled(False) 

    def mostrar_info_estudio(self, info):
        traducciones = {
            "PatientName": "Nombre", "PatientID": "ID del Paciente",
            "PatientSex": "Sexo", "StudyDate": "Fecha del Estudio",
            "Modality": "Modalidad", "StudyDescription": "Descripción del Estudio",
            "SeriesDescription": "Descripción de la Serie", "Manufacturer": "Fabricante",
            "PixelSpacing": "Espaciado de Píxeles", "SliceThickness": "Grosor del Corte",
            "dim": "Dimensiones del Volumen", "pixdim": "Tamaño del Voxel",
            "sform_code": "Código de Orientación", "descrip": "Descripción",
            "datatype": "Tipo de Dato", "bitpix": "Bits por Píxel", "slice_code": "Código de Adquisición"
        }
        texto = ""
        for k, v in info.items():
            significado = traducciones.get(k, k)
            texto += f"- <b>{k} ({significado}):</b> {v}<br>"
        self.Info_Estudio.setText(texto)

    def mostrar_imagen(self, img, label):
        if img is None or np.max(img) == np.min(img):
            label.clear()
            return
        img = ((img - np.min(img)) / (np.max(img) - np.min(img)) * 255).astype(np.uint8)
        h, w = img.shape
        qimg = QImage(img.tobytes(), w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg).scaled(label.width(), label.height())
        label.setPixmap(pixmap)

    def inicializar_sliders(self, z, y, x):
        self.Slider_Axial.setMaximum(z - 1)
        self.spinBox_Axial.setMaximum(z - 1)
        self.Slider_Axial.setValue(z // 2)
        self.spinBox_Axial.setValue(z // 2)

        self.Slider_Sagital.setMaximum(x - 1)
        self.spinBox_Sagital.setMaximum(x - 1)
        self.Slider_Sagital.setValue(x // 2)
        self.spinBox_Sagital.setValue(x // 2)

        self.Slider_Coronal.setMaximum(y - 1)
        self.spinBox_Coronal.setMaximum(y - 1)
        self.Slider_Coronal.setValue(y // 2)
        self.spinBox_Coronal.setValue(y // 2)

    def mostrar_imagenes_por_defecto(self):
        ruta_base = os.path.dirname(__file__)
        self.mostrar_imagen_archivo(os.path.join(ruta_base, "img", "img_dummies_planosAnatomicos", "axial.jpg"), self.plano_Axial)
        self.mostrar_imagen_archivo(os.path.join(ruta_base, "img", "img_dummies_planosAnatomicos", "sagital.jpg"), self.plano_Sagital)
        self.mostrar_imagen_archivo(os.path.join(ruta_base, "img", "img_dummies_planosAnatomicos", "coronal.jpg"), self.plano_Coronal)

    def mostrar_imagen_archivo(self, ruta, label):
        pixmap = QPixmap(ruta)
        label.setPixmap(pixmap)

    def volver(self):
        self.close()
        if self.parent is not None:
            self.parent.show()

    def limpiar(self):
        self.mostrar_imagenes_por_defecto()
        self.boton_ModificarMetadatos.setEnabled(False)
        self.boton_transf_dcm_nii.setEnabled(False)
        self.Info_Estudio.setText("Información del Estudio (metadatos ordenados)\n")
        for s, sp in [(self.Slider_Axial, self.spinBox_Axial),
                      (self.Slider_Sagital, self.spinBox_Sagital),
                      (self.Slider_Coronal, self.spinBox_Coronal)]:
            s.setMaximum(0)
            s.setValue(0)
            sp.setMaximum(0)
            sp.setValue(0)

    def mostrar_mensaje(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)

    def mostrar_advertencia(self, titulo, mensaje):
        QMessageBox.warning(self, titulo, mensaje)
        
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

# -----------------------------

# ========================
# controlador.py
# ========================

import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class ControladorImagenesMedicas:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.volumen = None
        self.info_metadatos = {}
        self.ruta_dicom = None
        self.ruta_nifti = None

    def cargar_archivo(self):
        carpeta = QFileDialog.getExistingDirectory(self.vista, "Seleccionar carpeta DICOM")
        if carpeta and any(f.endswith(".dcm") for f in os.listdir(carpeta)):
            self.vista.boton_ModificarMetadatos.setEnabled(True)
            self.vista.boton_transf_dcm_nii.setEnabled(True) 
            self.volumen, info = self.modelo.cargar_dicom(carpeta)
            self.ruta_dicom = carpeta
            self.ruta_nifti = None
            
        else:
            ruta, _ = QFileDialog.getOpenFileName(self.vista, "Seleccionar NIfTI", "", "NIfTI (*.nii *.nii.gz)")
            if not ruta: return
            self.volumen, info = self.modelo.cargar_nifti(ruta)
            self.ruta_nifti = ruta
            self.ruta_dicom = None

        self.info_metadatos = info
        self.vista.mostrar_info_estudio(info)
        z, y, x = self.volumen.shape
        self.vista.inicializar_sliders(z, y, x)
        self.actualizar_todos_planos()

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
        self.ruta_dicom = None
        self.ruta_nifti = None
        self.vista.limpiar()

    def transformar_dicom_a_nifti(self):
        if not self.ruta_dicom:
            self.vista.mostrar_advertencia("Error", "Debes cargar un archivo DICOM primero.")
            return
        salida, _ = QFileDialog.getSaveFileName(self.vista, "¿Donde vas a guardar el NIfTI resultante?", "salida.nii", "NIfTI (*.nii *.nii.gz)")
        if not salida: return
        info, ok, msg = self.modelo.dicom_a_nifti(self.ruta_dicom, salida, self.info_metadatos)
        if ok:
            self.ruta_nifti = info.get("ruta_nifti")
            self.info_metadatos = info
            self.vista.mostrar_mensaje("Let's Go", "Conversión y guardado exitosos.")
        else:
            self.vista.mostrar_advertencia("Error", f"Error: {msg}")

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
        if self.ruta_nifti and not self.ruta_dicom:
            # Escenario 1: solo nii cargado
            self.vista.mostrar_mensaje("Guardar estudio", 
                "Se cargó un archivo NIfTI para visualización y análisis.\nNo se requiere guardado en base de datos.")
            return

        elif self.ruta_dicom:
            # Escenario 2 o 3
            sliders = {
                "axial": self.vista.Slider_Axial.value(),
                "sagital": self.vista.Slider_Sagital.value(),
                "coronal": self.vista.Slider_Coronal.value()
            }

            # Actualiza info_metadatos con rutas
            self.info_metadatos["ruta_dicom"] = os.path.abspath(self.ruta_dicom) if self.ruta_dicom else None
            self.info_metadatos["ruta_nifti"] = os.path.abspath(self.ruta_nifti) if self.ruta_nifti else None

            exito, resultado = self.modelo.guardar_estudio_completo(self.volumen, self.info_metadatos, sliders)
            if exito:
                self.vista.mostrar_mensaje("Guardar estudio", f"✅ Estudio guardado exitosamente.\nImágenes guardadas en: {resultado}")
            else:
                self.vista.mostrar_advertencia("Guardar estudio", f"❌ No se pudo guardar el estudio.\nDetalles: {resultado}")
        else:
            self.vista.mostrar_advertencia("Guardar estudio", "No has cargado ningún archivo válido para guardar.")



# ========================
# main.py
# ========================

import sys
from PyQt5.QtWidgets import QApplication
# from vista import VistaImagenesMedicas
# from modelo import ModeloImagenesMedicas
# from controlador import ControladorImagenesMedicas

if __name__ == "__main__":
    app = QApplication(sys.argv)
    vista = VistaImagenesMedicas()
    modelo = ModeloImagenesMedicas()
    controlador = ControladorImagenesMedicas(vista, modelo)
    vista.setControlador(controlador)
    vista.show()
    sys.exit(app.exec_())

