import wx
import threading
import requests
from reproductor import Reproductor

class FrameRadios(wx.Frame):
    def __init__(self, parent, main_frame):
        super(FrameRadios, self).__init__(parent, title=main_frame.GetTitle(), size=(800, 600))
        self.main_frame = main_frame
        self.Centre()
        if main_frame.IsMaximized():
            self.Maximize()

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Cuadro de búsqueda
        etiqueta_busqueda = wx.StaticText(panel, label="Ingresa una búsqueda:")
        sizer.Add(etiqueta_busqueda, 0, wx.ALL | wx.EXPAND, 10)

        self.texto_busqueda = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.texto_busqueda, 0, wx.ALL | wx.EXPAND, 10)

        # ComboBox para elegir el criterio
        etiqueta_criterio = wx.StaticText(panel, label="Selecciona el tipo de búsqueda:")
        sizer.Add(etiqueta_criterio, 0, wx.ALL, 5)

        self.combo_criterio = wx.ComboBox(panel, choices=["Por nombre", "Por etiqueta", "Por país"], style=wx.CB_READONLY)
        self.combo_criterio.SetSelection(0)
        sizer.Add(self.combo_criterio, 0, wx.ALL | wx.EXPAND, 10)

        # Botón Buscar
        boton_buscar = wx.Button(panel, label="Buscar")
        sizer.Add(boton_buscar, 0, wx.ALL | wx.CENTER, 10)

        # Lista de resultados
        self.lista_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.lista_ctrl.InsertColumn(0, "Estación", width=400)
        self.lista_ctrl.InsertColumn(1, "País", width=180)
        self.lista_ctrl.InsertColumn(2, "Ciudad", width=180)
        sizer.Add(self.lista_ctrl, 1, wx.EXPAND | wx.ALL, 10)

# Botón Detener
        self.boton_detener = wx.Button(panel, label="Detener")
        self.boton_detener.Hide()  # Ocultar inicialmente
        sizer.Add(self.boton_detener, 0, wx.ALL | wx.CENTER, 10)

        # Botón Silenciar
        self.boton_silenciar = wx.Button(panel, label="Silenciar")
        self.boton_silenciar.Hide()  # Ocultar inicialmente
        sizer.Add(self.boton_silenciar, 0, wx.ALL | wx.CENTER, 10)
        # Controles de volumen
        etiqueta_volumen = wx.StaticText(panel, label="&Volumen:")
        sizer.Add(etiqueta_volumen, 0, wx.ALL, 5)
        self.slider_volumen = wx.Slider(panel, value=50, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        sizer.Add(self.slider_volumen, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)

        # Eventos
        boton_buscar.Bind(wx.EVT_BUTTON, self.on_buscar)
        self.texto_busqueda.Bind(wx.EVT_TEXT_ENTER, self.on_buscar)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.lista_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        self.lista_ctrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_list_item_right_click)
        self.lista_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)  # <- Añadir este binding
        self.boton_detener.Bind(wx.EVT_BUTTON, self.on_detener)
        self.boton_silenciar.Bind(wx.EVT_BUTTON, self.on_silenciar)
        self.slider_volumen.Bind(wx.EVT_SLIDER, self.on_volumen_cambiado)

        

        # Variables
        self.video_urls = []
        self.selected_index = -1
        self.reproductor = None  # Inicializar el reproductor como None

    def on_buscar(self, event):
        busqueda = self.texto_busqueda.GetValue().strip()
        criterio = self.combo_criterio.GetValue().strip().lower()

        if not busqueda or not criterio:
            wx.MessageBox("Por favor, ingresa una búsqueda y selecciona un criterio.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Construir la URL según el criterio
        base_url = "https://de1.api.radio-browser.info/json/stations"
        if "nombre" in criterio:
            endpoint = f"{base_url}/byname/{busqueda}"
        elif "etiqueta" in criterio:
            endpoint = f"{base_url}/bytag/{busqueda}"
        elif "país" in criterio:
            busqueda_ingles = self.traducir_pais(busqueda)
            endpoint = f"{base_url}/bycountry/{busqueda_ingles}"
        else:
            endpoint = f"{base_url}/byname/{busqueda}"

        # Ejecutar la búsqueda en un hilo
        threading.Thread(target=self.realizar_busqueda, args=(endpoint,), daemon=True).start()

    def realizar_busqueda(self, endpoint):
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                resultados = response.json()

                # Para cada estación, extraer nombre, país y ciudad
                video_titles = []
                video_paises = []
                video_ciudades = []
                video_urls = []
                for estacion in resultados:
                    nombre = estacion.get("name", "Sin nombre")
                    pais = estacion.get("country", "Desconocido")
                    ciudad = estacion.get("state", "Desconocida")
                    video_titles.append(nombre)
                    video_paises.append(pais)
                    video_ciudades.append(ciudad)
                    video_urls.append(estacion.get("url_resolved", ""))

                wx.CallAfter(self.mostrar_resultados, video_titles, video_paises, video_ciudades, video_urls)
            else:
                wx.CallAfter(wx.MessageBox, "No se pudo obtener información de Radio Browser.", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.CallAfter(wx.MessageBox, f"Error al realizar la búsqueda: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def mostrar_resultados(self, video_titles, video_paises, video_ciudades, video_urls):
        self.lista_ctrl.DeleteAllItems()  # Limpiar la lista antes de agregar nuevos resultados
        self.video_urls = video_urls  # Guardar URLs para usarlas más tarde
        for titulo, pais, ciudad in zip(video_titles, video_paises, video_ciudades):
            index = self.lista_ctrl.InsertItem(self.lista_ctrl.GetItemCount(), titulo)
            self.lista_ctrl.SetItem(index, 1, pais)
            self.lista_ctrl.SetItem(index, 2, ciudad)


    def on_list_item_right_click(self, event):
        index = event.GetIndex()
        self.selected_index = index
        menu = wx.Menu()
        item_reproducir = menu.Append(wx.ID_ANY, "Reproducir")
        item_copiar = menu.Append(wx.ID_ANY, "Copiar URL del stream")
        item_guardar = menu.Append(wx.ID_ANY, "Guardar Radio (No implementado)")
        self.Bind(wx.EVT_MENU, self.on_reproducir, item_reproducir)
        self.Bind(wx.EVT_MENU, self.copiar_url, item_copiar)
        self.Bind(wx.EVT_MENU, self.guardar_radio, item_guardar)
        self.PopupMenu(menu)

    def on_reproducir(self, event):
        if self.selected_index == -1:
            wx.MessageBox("Selecciona una estación primero.", "Error", wx.OK | wx.ICON_ERROR)
            return
        if self.reproductor: # verificar si alguna reproducción está en curso
            self.reproductor.stop()
            self.reproductor.Destroy()
        media_path = self.video_urls[self.selected_index]
        self.reproductor = Reproductor(self, media_path, self.slider_volumen.GetValue())
        self.boton_detener.Show()
        self.boton_silenciar.Show()
        self.Layout()  # Refrescar la interfaz para que se muestren los botones.
        self.lista_ctrl.SetFocus()  # Mantener el foco en la lista

    def on_detener(self, event):
        if self.reproductor:
            self.reproductor.stop()
            # deshabilitar botones
            self.boton_detener.Hide()
            self.boton_silenciar.Hide()
            self.Layout()  # Refrescar la interfaz para que se oculten los botones.
            self.lista_ctrl.SetFocus()  # Mantener el foco en la lista

    def on_silenciar(self, event):
        if self.reproductor:
            self.reproductor.mute()


    def copiar_url(self, event):
        if self.selected_index < len(self.video_urls):
            url = self.video_urls[self.selected_index]
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(url))
                wx.TheClipboard.Close()
                wx.MessageBox("URL copiada al portapapeles.", "Éxito", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("No se pudo copiar la URL.", "Error", wx.OK | wx.ICON_ERROR)

    def on_item_activated(self, event):
        # Este evento se dispara al presionar Enter o hacer doble clic
        self.mostrar_menu_contextual()

    def guardar_radio(self, event):
        wx.MessageBox("Funcionalidad aún no implementada.", "Información", wx.OK | wx.ICON_INFORMATION)


    def mostrar_menu_contextual(self):
        index = self.lista_ctrl.GetFirstSelected()  # Obtener el ítem seleccionado
        if index == -1:
            return
        self.selected_index = index  # Actualizar el índice seleccionado
        
        menu = wx.Menu()
        item_reproducir = menu.Append(wx.ID_ANY, "Reproducir")
        item_copiar = menu.Append(wx.ID_ANY, "Copiar URL del stream")
        item_guardar = menu.Append(wx.ID_ANY, "Guardar Radio (No implementado)")
        
        self.Bind(wx.EVT_MENU, self.on_reproducir, item_reproducir)
        self.Bind(wx.EVT_MENU, self.copiar_url, item_copiar)
        self.Bind(wx.EVT_MENU, self.guardar_radio, item_guardar)
        
        self.lista_ctrl.PopupMenu(menu)
        menu.Destroy()  # Asegurar que el menú se elimine

    def on_list_key_down(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN:
            self.mostrar_menu_contextual()
        else:
            event.Skip()


    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            if self.reproductor:
                self.reproductor.stop()
                self.reproductor.Destroy()
            self.main_frame.Show()
            self.Close()
        else:
            event.Skip()

    def traducir_pais(self, pais):
        traducciones = {
            "Ecuador": "Ecuador",
            "España": "Spain",
            # Agregar más traducciones según sea necesario
        }
        return traducciones.get(pais, pais)

    def on_volumen_cambiado(self, event):
        if self.reproductor:
            self.reproductor.set_volume(self.slider_volumen.GetValue())
            self.reproductor.update_volume_bar()
