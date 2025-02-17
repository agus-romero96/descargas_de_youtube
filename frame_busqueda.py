import wx
import threading
import yt_dlp

class FrameBusqueda(wx.Frame):
    def __init__(self, parent, main_frame):
        super(FrameBusqueda, self).__init__(parent, title=main_frame.GetTitle(), size=(400, 300))
        self.main_frame = main_frame
        self.Centre()

        if main_frame.IsMaximized():
            self.Maximize()

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        etiqueta_busqueda = wx.StaticText(panel, label="Ingresa una búsqueda:")
        sizer.Add(etiqueta_busqueda, 0, wx.ALL | wx.EXPAND, 10)
        self.texto_busqueda = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.texto_busqueda, 0, wx.ALL | wx.EXPAND, 10)

        etiqueta_criterio = wx.StaticText(panel, label="Criterio:")
        sizer.Add(etiqueta_criterio, 0, wx.ALL | wx.EXPAND, 10)
        self.combo_criterio = wx.ComboBox(panel, choices=["Canal", "Playlist", "Video"], style=wx.CB_READONLY)
        self.combo_criterio.SetSelection(2)  # Establecer "Video" como selección por defecto
        sizer.Add(self.combo_criterio, 0, wx.ALL | wx.EXPAND, 10)
        
        # Botones Aceptar y Cancelar
        sizer_botones = wx.BoxSizer(wx.HORIZONTAL)
        boton_aceptar = wx.Button(panel, label="Aceptar")
        boton_cancelar = wx.Button(panel, label="Cancelar")
        sizer_botones.Add(boton_aceptar, 0, wx.RIGHT, 10)
        sizer_botones.Add(boton_cancelar, 0, wx.LEFT, 10)
        sizer.Add(sizer_botones, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(sizer)
        
        # Eventos
        boton_aceptar.Bind(wx.EVT_BUTTON, self.on_aceptar)
        boton_cancelar.Bind(wx.EVT_BUTTON, self.on_cancelar)
        self.texto_busqueda.Bind(wx.EVT_TEXT_ENTER, self.on_aceptar)
        self.combo_criterio.Bind(wx.EVT_TEXT_ENTER, self.on_aceptar)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

    def on_aceptar(self, event):
        # Lógica de búsqueda
        busqueda = self.texto_busqueda.GetValue().strip()
        criterio = self.combo_criterio.GetValue().strip().lower()
        
        if not busqueda or not criterio:
            wx.MessageBox("Por favor, ingresa una búsqueda y selecciona un criterio.", "Error", wx.OK | wx.ICON_ERROR)
            return

        def realizar_busqueda():
            try:
                ydl_opts = {
                    'quiet': True,
                    'default_search': 'ytsearch10',  # Limitar a los 10 primeros resultados
                }

                if criterio == "canal":
                    query = f"ytsearch10:{busqueda} channel"
                elif criterio == "playlist":
                    query = f"ytsearch10:{busqueda} playlist"
                else:
                    query = f"ytsearch10:{busqueda} video"

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    video_titles = [entry['title'] for entry in info['entries']]
                    video_urls = [entry['webpage_url'] for entry in info['entries']]
                    wx.CallAfter(self.mostrar_resultados, video_titles, video_urls)
            except Exception as e:
                wx.CallAfter(wx.MessageBox, f"Error al realizar la búsqueda: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

        # Ejecutar en un hilo para no bloquear la GUI
        threading.Thread(target=realizar_busqueda).start()

    def mostrar_resultados(self, video_titles, video_urls):
        dialogo_resultados = wx.Dialog(self, title="Resultados de la búsqueda", size=(600, 400))
        sizer_principal = wx.BoxSizer(wx.VERTICAL)

        lista_ctrl = wx.ListCtrl(dialogo_resultados, style=wx.LC_REPORT)
        lista_ctrl.InsertColumn(0, "Título", width=450)
        lista_ctrl.InsertColumn(1, "URL", width=150)

        for titulo, url in zip(video_titles, video_urls):
            index = lista_ctrl.InsertItem(lista_ctrl.GetItemCount(), titulo)
            lista_ctrl.SetItem(index, 1, url)

        sizer_principal.Add(lista_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        
        # Botón para cerrar el diálogo
        boton_cerrar = wx.Button(dialogo_resultados, label="Cerrar")
        boton_cerrar.Bind(wx.EVT_BUTTON, lambda evt: dialogo_resultados.Destroy())
        sizer_principal.Add(boton_cerrar, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        dialogo_resultados.SetSizer(sizer_principal)
        dialogo_resultados.Centre()
        dialogo_resultados.ShowModal()

    def on_cancelar(self, event):
        self.main_frame.Show()
        self.Close()

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.on_cancelar(event)
        elif keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            self.on_aceptar(event)
        else:
            event.Skip()
