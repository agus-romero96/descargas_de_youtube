import wx
from youtube.frame_youtube_base import FrameYouTubeBase
from youtube.subtitulos.panel_subtitulos import PanelSubtitulos

class FrameSubtitulos(FrameYouTubeBase):
    def __init__(self, parent, main_frame):
        super().__init__(parent, main_frame)  # Usar super() estilo Python 3
        
        self.panel_subtitulos = PanelSubtitulos(self)
        
        # Añadir elementos en orden correcto
        self.sizer_principal.Add(self.panel_subtitulos, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer_principal.Add(self.boton_volver, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Ajustar orden de tabulación
        self.panel_subtitulos.MoveBeforeInTabOrder(self.boton_volver)
        
        # Establecer foco inicial en el campo de URL
        wx.CallAfter(self.panel_subtitulos.texto_url.SetFocus)
        self.Layout()