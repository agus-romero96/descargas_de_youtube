# -*- coding: utf-8 -*-
try:
    import wx
    import wx.lib.dialogs
    from youtube.subtitulos.extraccion_subtitulos import obtener_id_video, obtener_nombre_video, obtener_subtitulos, guardar_subtitulos_en_archivo
    from mi_logging import logger
    logger.info("Módulos importados en interfaz.py")
except ImportError as e:
    logger.error("Error al importar módulosen interfaz.py: %s", e)
    raise

class PanelSubtitulos(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.video_title = None
        self.crear_widgets()
    
    def crear_widgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.etiqueta_url = wx.StaticText(self, label="Ingresa la URL del video de YouTube:")
        self.texto_url = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.texto_url.Bind(wx.EVT_TEXT_ENTER, self.al_extraer_subtitulos)
        vbox.Add(self.etiqueta_url, 0, wx.ALL, 5)
        vbox.Add(self.texto_url, 0, wx.EXPAND | wx.ALL, 5)

        self.etiqueta_idioma = wx.StaticText(self, label="Idioma de los subtítulos:")
        self.idiomas = ['es', 'en', 'fr', 'it']
        self.eleccion_idioma = wx.Choice(self, choices=self.idiomas)
        self.eleccion_idioma.SetSelection(0)
        vbox.Add(self.etiqueta_idioma, 0, wx.ALL, 5)
        vbox.Add(self.eleccion_idioma, 0, wx.EXPAND | wx.ALL, 5)

        self.boton_extraer = wx.Button(self, label="Extraer subtítulos")
        self.boton_extraer.Bind(wx.EVT_BUTTON, self.al_extraer_subtitulos)
        vbox.Add(self.boton_extraer, 0, wx.EXPAND | wx.ALL, 5)

        self.boton_limpiar = wx.Button(self, label="Limpiar campos")
        self.boton_limpiar.Bind(wx.EVT_BUTTON, self.limpiar_campos)
        vbox.Add(self.boton_limpiar, 0, wx.EXPAND | wx.ALL, 5)

        self.texto_subtitulos = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.texto_subtitulos.Disable()
        vbox.Add(self.texto_subtitulos, 1, wx.EXPAND | wx.ALL, 5)

        self.boton_guardar = wx.Button(self, label="Guardar subtítulos")
        self.boton_guardar.Disable()
        self.boton_guardar.Bind(wx.EVT_BUTTON, self.al_guardar_subtitulos)
        vbox.Add(self.boton_guardar, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(vbox)


    def al_guardar_subtitulos(self, event):
        logger.info("el usuario intenta guardar un subtítulo.")
        subtitulos = self.texto_subtitulos.GetValue()
        if not subtitulos:
            wx.MessageBox("No hay subtítulos para guardar.", "Error", wx.OK | wx.ICON_ERROR)
            logger.error("Intento de guardar sin subtítulos.")
            return

        default_filename = f"{self.video_title}.txt" if self.video_title else "subtitulos.txt"
        with wx.FileDialog(self, "Guardar subtítulos", defaultFile=default_filename,
                           wildcard="Text files (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                logger.info("El usuario canceló el guardado.")
                return

            path = dialog.GetPath()
            mensaje = guardar_subtitulos_en_archivo(subtitulos, path)
            wx.MessageBox(mensaje, "Información", wx.OK | wx.ICON_INFORMATION)
            self.limpiar_campos(event)

    def al_extraer_subtitulos(self, event):
        url = self.texto_url.GetValue().strip()
        idioma = self.idiomas[self.eleccion_idioma.GetSelection()]
        id_video = obtener_id_video(url)
        if not id_video:
            wx.MessageBox("URL de YouTube no válida.", "Error", wx.OK | wx.ICON_ERROR)
            logger.error("Intento de extracción con URL no válida: %s", url)
            return

        # Mostrar un indicador de carga
        busy = wx.BusyInfo("Extrayendo subtítulos, por favor espere...")
        wx.Yield()  # Permite actualizar la interfaz mientras se muestra el indicador

        subtitulos = obtener_subtitulos(id_video, idioma)
        self.video_title = obtener_nombre_video(id_video)

        self.texto_subtitulos.SetValue(subtitulos)
        self.texto_subtitulos.Enable()
        self.boton_guardar.Enable()
        self.texto_url.SetValue('')
        self.texto_subtitulos.SetFocus()
        logger.info("Extracción completada para el video ID: %s", id_video)

    def limpiar_campos(self, event):
        self.texto_url.SetValue('')
        self.texto_subtitulos.SetValue('')
        self.texto_subtitulos.Disable()
        self.boton_guardar.Disable()
        self.texto_url.SetFocus()
        logger.info("Campos limpiados por el usuario.")

