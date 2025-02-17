import wx
import wx.lib.filebrowsebutton as filebrowse
import os
import threading
from youtube.descargas.funciones_descarga import descargar_audio
from threading import Semaphore

MAX_CONCURRENT_DOWNLOADS = 3

class IniciarDescarga(wx.Panel):
    semaphore = Semaphore(MAX_CONCURRENT_DOWNLOADS)
    
    def __init__(self, parent, agregar_mensaje_callback=None):
        super(IniciarDescarga, self).__init__(parent)
        # Se espera que se pase el callback para actualizar el historial (de InfoDescargas)
        self.agregar_mensaje_callback = agregar_mensaje_callback
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Entrada de URL
        self.etiqueta_url = wx.StaticText(self, label="&Introduce la URL del video:")
        self.sizer.Add(self.etiqueta_url, 0, wx.ALL, 5)
        self.texto_url = wx.TextCtrl(self)
        self.sizer.Add(self.texto_url, 0, wx.ALL | wx.EXPAND, 5)

        self.etiqueta_formato = wx.StaticText(self, label="Selecciona el &formato:")
        self.sizer.Add(self.etiqueta_formato, 0, wx.ALL, 5)
        self.opciones_formato = ["mp3", "wav", "aac"]
        self.combo_formato = wx.ComboBox(self, choices=self.opciones_formato, style=wx.CB_READONLY)
        self.combo_formato.SetSelection(0)
        self.sizer.Add(self.combo_formato, 0, wx.ALL | wx.EXPAND, 5)

        self.etiqueta_calidad = wx.StaticText(self, label="Selecciona la &calidad:")
        self.sizer.Add(self.etiqueta_calidad, 0, wx.ALL, 5)
        self.opciones_calidad = ["192", "256", "320"]
        self.combo_calidad = wx.ComboBox(self, choices=self.opciones_calidad, style=wx.CB_READONLY)
        self.combo_calidad.SetSelection(0)
        self.sizer.Add(self.combo_calidad, 0, wx.ALL | wx.EXPAND, 5)

        self.etiqueta_guardar = wx.StaticText(self, label="Selecciona la ubicación donde se &guardadará las descargas:")
        self.sizer.Add(self.etiqueta_guardar, 0, wx.ALL, 5)
        self.boton_guardar_ruta = filebrowse.DirBrowseButton(self)
        self.sizer.Add(self.boton_guardar_ruta, 0, wx.ALL | wx.EXPAND, 5)

        self.boton_descargar = wx.Button(self, label="&Descargar")
        self.sizer.Add(self.boton_descargar, 0, wx.ALL | wx.CENTER, 5)
        self.boton_descargar.Bind(wx.EVT_BUTTON, self.iniciar_descarga)
        self.SetSizer(self.sizer)
        self.Layout()
        self.texto_url.SetFocus()

    def procesar_descarga(self, url, formato, calidad, ruta_guardado):
        with self.semaphore:
            # Extraer título del video
            titulo = "Desconocido"
            try:
                import yt_dlp
                with yt_dlp.YoutubeDL({}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    titulo = info.get('title', 'Desconocido')
            except Exception as e:
                if self.agregar_mensaje_callback:
                    wx.CallAfter(self.agregar_mensaje_callback, f"Error al obtener el título: {str(e)}")
            def format_seconds(segundos):
                segundos = int(segundos)
                m, s = divmod(segundos, 60)
                h, m = divmod(m, 60)
                return f"{h:02d}:{m:02d}:{s:02d}"
            def hook_progreso(info):
                if info['status'] == 'downloading':
                    total = info.get('total_bytes') or info.get('total_bytes_estimate')
                    if total:
                        porcentaje = int(info.get('downloaded_bytes', 0) * 100 / total)
                        mb_descargados = info.get('downloaded_bytes', 0) / (1024 * 1024)
                        eta_seconds = info.get('eta')
                        eta_formatted = format_seconds(eta_seconds) if eta_seconds is not None else "N/A"
                        mensaje = (f"Descargando: {porcentaje}% | {mb_descargados:.2f} MB | ETA: {eta_formatted} | {titulo}")
                        if self.agregar_mensaje_callback:
                            wx.CallAfter(self.agregar_mensaje_callback, mensaje)
                elif info['status'] == 'finished':
                    filename = info.get('filename', '')
                    nombre_archivo = os.path.basename(filename).replace('.webm', '')
                    mensaje_fin_descarga = "Descarga completada"
                    if self.agregar_mensaje_callback:
                        wx.CallAfter(self.agregar_mensaje_callback, mensaje_fin_descarga)
                    try:
                        filesize = os.path.getsize(filename) / (1024 * 1024)
                    except Exception:
                        filesize = 0.0
                    mensaje_final = f"Conversión completada: {nombre_archivo} | {formato} | {filesize:.2f} MB | {titulo}"
                    if self.agregar_mensaje_callback:
                        wx.CallAfter(self.agregar_mensaje_callback, mensaje_final)
            ruta_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg', 'bin')
            try:
                descargar_audio(url, formato, calidad, ruta_guardado, hook_progreso, ruta_ffmpeg)
                wx.Yield()
                final_msg = "¡Descarga y conversión completada!"
                if self.agregar_mensaje_callback:
                    wx.CallAfter(self.agregar_mensaje_callback, final_msg)
            except Exception as e:
                mensaje = f"Error: {str(e)}"
                if self.agregar_mensaje_callback:
                    wx.CallAfter(self.agregar_mensaje_callback, mensaje)
                wx.CallAfter(wx.MessageBox, mensaje, "Error", wx.OK | wx.ICON_ERROR)


    def iniciar_descarga(self, event):
        url = self.texto_url.GetValue().strip()
        formato = self.combo_formato.GetValue()
        calidad = self.combo_calidad.GetValue()
        ruta_guardado = self.boton_guardar_ruta.GetValue().strip()

        if not ruta_guardado:
            ruta_guardado = os.path.join(os.getcwd(), 'musica')
            if not os.path.exists(ruta_guardado):
                os.makedirs(ruta_guardado)

        if "youtube.com" not in url and "youtu.be" not in url:
            wx.MessageBox("La URL introducida no es de YouTube", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.texto_url.SetValue("")
        self.texto_url.SetFocus()
        
        # Verificar si es una playlist y extraer URLs y títulos de videos
        def obtener_videos():
            try:
                import yt_dlp
                ydl_opts = {
                    'quiet': True,
                    'extract_flat': 'in_playlist',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if '_type' in info and info['_type'] == 'playlist':
                        video_urls = [entry['url'] for entry in info['entries']]
                        video_titles = [entry['title'] for entry in info['entries']]
                        wx.CallAfter(self.mostrar_opciones_playlist, video_titles, video_urls, formato, calidad, ruta_guardado)
                    else:
                        hilo = threading.Thread(
                            target=self.procesar_descarga, 
                            args=(url, formato, calidad, ruta_guardado)
                        )
                        hilo.start()
            except Exception as e:
                wx.CallAfter(wx.MessageBox, f"Error al procesar la URL: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

        # Ejecutar en un hilo para no bloquear la GUI
        threading.Thread(target=obtener_videos).start()

    def mostrar_opciones_playlist(self, video_titles, video_urls, formato, calidad, ruta_guardado):
        total_canciones = len(video_titles)
        dialogo = wx.MessageDialog(
            self,
            f"La playlist contiene {total_canciones} canciones.\n¿Deseas descargar todas las canciones?",
            "Información",
            wx.YES_NO | wx.ICON_QUESTION
        )
        respuesta = dialogo.ShowModal()

        if respuesta == wx.ID_YES:
            for video_url in video_urls:
                hilo = threading.Thread(
                    target=self.procesar_descarga, 
                    args=(video_url, formato, calidad, ruta_guardado)
                )
                hilo.start()
        else:
            wx.CallAfter(self.mostrar_lista_canciones, video_titles, video_urls, formato, calidad, ruta_guardado)

    def mostrar_lista_canciones(self, video_titles, video_urls, formato, calidad, ruta_guardado):
        from listctrl_checkbox import ListCtrlConCheckbox
        dialogo_lista = wx.Dialog(self, title="Selecciona las canciones a descargar", size=(600, 400))
        sizer_principal = wx.BoxSizer(wx.VERTICAL)

        # Etiqueta y cuadro de búsqueda
        etiqueta_busqueda = wx.StaticText(dialogo_lista, label="Buscar:")
        sizer_principal.Add(etiqueta_busqueda, 0, wx.ALL, 5)
        cuadro_busqueda = wx.TextCtrl(dialogo_lista)
        sizer_principal.Add(cuadro_busqueda, 0, wx.EXPAND | wx.ALL, 10)

        # Etiqueta para la lista de canciones
        etiqueta_lista = wx.StaticText(dialogo_lista, label="Lista de canciones:")
        sizer_principal.Add(etiqueta_lista, 0, wx.ALL, 5)
    
        # Crear el ListCtrl con casillas de verificación
        lista_ctrl = ListCtrlConCheckbox(dialogo_lista, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
    
        # Guardar todas las canciones como lista de tuplas (título, estado) y guardar el estado inicial
        todas_canciones = [(titulo, "Pendiente") for titulo in video_titles]
        estado_casillas = {titulo: False for titulo, _ in todas_canciones}
    
        # Agregar cada título a la lista (por defecto, sin marcar)
        for titulo, estado in todas_canciones:
            lista_ctrl.agregar_item(titulo, estado, marcado=False)
    
        sizer_principal.Add(lista_ctrl, 1, wx.EXPAND | wx.ALL, 10)
    
        # Botones de control en un sizer horizontal
        sizer_botones = wx.BoxSizer(wx.HORIZONTAL)
        boton_sel_todas = wx.Button(dialogo_lista, label="Seleccionar todas")
        boton_desel_todas = wx.Button(dialogo_lista, label="Deseleccionar todas")
        boton_descargar = wx.Button(dialogo_lista, label="Descargar Seleccionadas")
    
        boton_sel_todas.Bind(wx.EVT_BUTTON, lambda evt: seleccionar_deseleccionar_todas(True))
        boton_desel_todas.Bind(wx.EVT_BUTTON, lambda evt: seleccionar_deseleccionar_todas(False))
    
        def seleccionar_deseleccionar_todas(marcar):
            termino_busqueda = cuadro_busqueda.GetValue().lower()
            for i in range(lista_ctrl.GetItemCount()):
                item_texto = lista_ctrl.GetItemText(i)
                if termino_busqueda in item_texto.lower() or termino_busqueda == "":
                    lista_ctrl.CheckItem(i, marcar)
                    estado_casillas[item_texto] = marcar
    
        def descargar_seleccionadas(evt):
            indices = lista_ctrl.obtener_items_checkeados()
            seleccionadas = [video_urls[i] for i in indices]
            if not seleccionadas:
                wx.MessageBox("No has seleccionado ninguna canción", "Aviso", wx.OK | wx.ICON_INFORMATION)
                return
            for video_url in seleccionadas:
                threading.Thread(target=self.procesar_descarga, args=(video_url, formato, calidad, ruta_guardado), daemon=True).start()
            dialogo_lista.Destroy()
    
        boton_descargar.Bind(wx.EVT_BUTTON, descargar_seleccionadas)
        sizer_botones.Add(boton_sel_todas, 0, wx.RIGHT, 5)
        sizer_botones.Add(boton_desel_todas, 0, wx.RIGHT, 5)
        sizer_botones.Add(boton_descargar, 0, wx.LEFT, 15)
        sizer_principal.Add(sizer_botones, 0, wx.ALIGN_CENTER | wx.ALL, 10)
    
        dialogo_lista.SetSizer(sizer_principal)
        dialogo_lista.Centre()
    
        # Función para filtrar la lista dinámicamente
        def filtrar_lista(evt):
            termino_busqueda = cuadro_busqueda.GetValue().lower()
            # Guardar el estado actual de cada item en la lista
            for i in range(lista_ctrl.GetItemCount()):
                item_texto = lista_ctrl.GetItemText(i)
                estado_casillas[item_texto] = lista_ctrl.IsItemChecked(i)
            # Borrar todos los items del ListCtrl (una sola vez)
            lista_ctrl.DeleteAllItems()
            # Agregar nuevamente los items que coincidan con el filtro, conservando su estado
            for titulo, estado in todas_canciones:
                if termino_busqueda in titulo.lower() or termino_busqueda == "":
                    lista_ctrl.agregar_item(titulo, estado, marcado=estado_casillas.get(titulo, False))
    
        cuadro_busqueda.Bind(wx.EVT_TEXT, filtrar_lista)
        dialogo_lista.ShowModal()
