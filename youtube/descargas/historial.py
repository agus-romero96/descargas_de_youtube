import wx
import os

class InfoDescargas(wx.Panel):
    def __init__(self, parent):
        super(InfoDescargas, self).__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.texto_historial = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.sizer.Add(self.texto_historial, 1, wx.ALL | wx.EXPAND, 5)
        self.boton_abrir_carpeta = wx.Button(self, label="&Abrir carpeta de descargas")
        self.sizer.Add(self.boton_abrir_carpeta, 0, wx.ALL | wx.CENTER, 5)
        self.boton_abrir_carpeta.Bind(wx.EVT_BUTTON, self.abrir_carpeta)
        self.SetSizer(self.sizer)
    
    def abrir_carpeta(self, event):
        ruta_descargas = os.path.join(os.getcwd(), "descargas")
        if os.path.exists(ruta_descargas):
            os.startfile(ruta_descargas)
        else:
            wx.MessageBox("No se han realizado descargas aún", "Error", wx.OK | wx.ICON_ERROR)
    
    def agregar_mensaje(self, mensaje):
        contenido = self.texto_historial.GetValue().splitlines()
        if mensaje.startswith("Descargando:") or mensaje.startswith("Convirtiendo:"):
            if contenido:
                ultimo_mensaje = contenido[-1]
                if (mensaje.startswith("Descargando:") and ultimo_mensaje.startswith("Descargando:")) or \
                   (mensaje.startswith("Convirtiendo:") and ultimo_mensaje.startswith("Convirtiendo:")):
                    contenido[-1] = mensaje
                else:
                    contenido.append(mensaje)
            else:
                contenido.append(mensaje)
        else:
            contenido.append(mensaje)
        nuevo_texto = "\n".join(contenido)
        self.texto_historial.SetValue(nuevo_texto)
        self.texto_historial.ShowPosition(self.texto_historial.GetLastPosition())
