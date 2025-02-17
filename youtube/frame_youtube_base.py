import wx

class FrameYouTubeBase(wx.Frame):
    def __init__(self, parent, main_frame, titulo=None):
        super().__init__(parent, title=titulo or main_frame.GetTitle(), size=(800,600))
        self.main_frame = main_frame
        if main_frame.IsMaximized():
            self.Maximize()
        
        self.sizer_principal = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_principal)
        
        # Botón volver creado pero NO añadido al sizer aquí
        self.boton_volver = wx.Button(self, label="&Volver al Menú Principal")
        self.boton_volver.Bind(wx.EVT_BUTTON, self.on_volver)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        
        self.Centre()

    def on_volver(self, event):
        """Cierra este frame y vuelve a mostrar el menú principal."""
        self.Close()
        self.main_frame.Show()
    
    def on_key(self, event):
        """Si se presiona Escape, se llama a on_volver."""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.on_volver(event)
        else:
            event.Skip()
