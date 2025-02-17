import wx
import wx.lib.dialogs
from mi_logging import logger

class MarcoPrincipal(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MarcoPrincipal, self).__init__(*args, **kwargs)
        self.SetTitle("El poder del aburrimiento")
        self.SetSize((800, 600))
        self.Centre()
        self.crear_menu()
        self.Maximize()
        

        # Panel principal (opcional)
        panel = wx.Panel(self)
        texto = wx.StaticText(panel, label="Bienvenido a la aplicación. Usa el menú para acceder a las funciones.")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(texto, 0, wx.ALL | wx.CENTER, 20)
        panel.SetSizer(sizer)
    
    def crear_menu(self):
        menu_bar = wx.MenuBar()
        menu_archivo = wx.Menu()
        
        # Submenú YouTube
        submenu_youtube = wx.Menu()
        item_buscar = submenu_youtube.Append(wx.ID_ANY, "Buscar por nombre, canal o playlist", "Busca en youtube")
        item_descargar = submenu_youtube.Append(wx.ID_ANY, "Descargar videos de YouTube", "Descarga videos de YouTube")
        item_subtitulos = submenu_youtube.Append(wx.ID_ANY, "Extraer subtítulos de videos de YouTube", "Extrae subtítulos de videos de YouTube")
        menu_archivo.AppendSubMenu(submenu_youtube, "YouTube")
        
        # Opción Ir al menú de radios
        item_radios = menu_archivo.Append(wx.ID_ANY, "Ir al menú de radios", "Acceder al menú de radios")
        
        # Opción Salir
        item_salir = menu_archivo.Append(wx.ID_EXIT, "Salir", "Salir de la aplicación")
        
        menu_bar.Append(menu_archivo, "Archivo")
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.busqueda, item_buscar)
        self.Bind(wx.EVT_MENU, self.on_descargar_videos, item_descargar)
        self.Bind(wx.EVT_MENU, self.on_extraer_subtitulos, item_subtitulos)
        self.Bind(wx.EVT_MENU, self.on_ir_radios, item_radios)
        self.Bind(wx.EVT_MENU, self.on_salir, item_salir)
    
    def on_descargar_videos(self, event):
        try:
            from youtube.descargas.frame_descargas import FrameDescargas
            logger.info("Importado el módulo frame_descargas")
        except ImportError as e:
            logger.critical("Error al importar el módulo frame_descargas: %s", e)
            wx.MessageBox("Error al importar el módulo de descargas", "Error", wx.OK | wx.ICON_ERROR)
            return
        # Ocultar el frame principal y abrir el frame de descargas
        frame_descargas = FrameDescargas(None, self)
        frame_descargas.Show()
        self.Hide()
    
    def on_extraer_subtitulos(self, event):
        try:
            from youtube.subtitulos.frame_subtitulos import FrameSubtitulos
            logger.info("Importado el módulo frame_subtitulos")
        except ImportError as e:
            logger.critical("Error al importar el módulo frame_subtitulos: %s", e)
            wx.MessageBox("Error al importar el módulo de subtítulos", "Error", wx.OK | wx.ICON_ERROR)
            return
        frame_sub = FrameSubtitulos(None, self)
        frame_sub.Show()
        self.Hide()

    def busqueda(self, event):
        try:
            from frame_busqueda import FrameBusqueda
            logger.info("importado el módulo para realizar búsquedas")
        except ImportError as e:
            logger.critical("Error al importar el módulo frame_subtitulos: %s", e)
            return
        frame_busqueda = FrameBusqueda(self, self)
        frame_busqueda.Show()
        self.Hide()

    def on_ir_radios(self, event):
        wx.MessageBox("Funcionalidad de radios no implementada.", "Información", wx.OK | wx.ICON_INFORMATION)
    
    def on_salir(self, event):
        self.Close()

if __name__ == "__main__":
    app = wx.App(False)
    marco = MarcoPrincipal(None)
    marco.Show()
    app.MainLoop()
