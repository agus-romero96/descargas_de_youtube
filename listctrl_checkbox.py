import wx

class ListCtrlConCheckbox(wx.ListCtrl):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=wx.LC_REPORT):
        super(ListCtrlConCheckbox, self).__init__(parent, id, pos, size, style)
        
        # Insertar columnas: "Canción" y "Estado" (opcional)
        self.InsertColumn(0, "Canción", width=350)
        self.InsertColumn(1, "Estado", width=150)
        
        # Intentar habilitar las casillas (disponible en wxPython 4.1+ en Windows)
        try:
            self.EnableCheckBoxes(True)
        except Exception as e:
            print("No se pudieron habilitar las casillas:", e)
    
    def agregar_item(self, cancion, estado="Pendiente", marcado=True):
        """Agrega un item al ListCtrl y marca la casilla si marcado es True."""
        index = self.InsertItem(self.GetItemCount(), cancion)
        self.SetItem(index, 1, estado)
        self.CheckItem(index, marcado)
        return index

    def obtener_items_checkeados(self):
        """Devuelve una lista de índices de los items que están marcados."""
        seleccionados = []
        for i in range(self.GetItemCount()):
            if self.IsItemChecked(i):
                seleccionados.append(i)
        return seleccionados
