import wx
from youtube.descargas.descarga import IniciarDescarga
from youtube.descargas.historial import InfoDescargas
from youtube.frame_youtube_base import FrameYouTubeBase

class FrameDescargas(FrameYouTubeBase):
    def __init__(self, parent, main_frame):
        super(FrameDescargas, self).__init__(parent, main_frame)
        
        self.notebook = wx.Notebook(self)
        # Pasa el callback a IniciarDescarga para que envíe mensajes al historial
        self.panel_descarga = IniciarDescarga(self.notebook, self.actualizar_historial)
        self.notebook.AddPage(self.panel_descarga, "Descarga")
        
        # InfoDescargas solo necesita el parent
        self.panel_historial = InfoDescargas(self.notebook)
        self.notebook.AddPage(self.panel_historial, "Historial")
        
        self.sizer_principal.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer_principal.Add(self.boton_volver, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.notebook.MoveBeforeInTabOrder(self.boton_volver)
        wx.CallAfter(self.panel_descarga.texto_url.SetFocus)
        self.Layout()
    
    def actualizar_historial(self, mensaje):
        """Callback para actualizar el historial de descargas."""
        self.panel_historial.agregar_mensaje(mensaje)
