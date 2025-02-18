import wx
import vlc
import sys

class Reproductor(wx.Panel):
    def __init__(self, parent, media_path, volumen):
        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()
        self.media_path = media_path
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.play_media(self.media_path)
        self.player.audio_set_volume(volumen)  # Ajustar el volumen

    def on_resize(self, event):
        if sys.platform.startswith('win'):
            self.player.set_hwnd(self.GetHandle())
        elif sys.platform.startswith('linux'):
            self.player.set_xwindow(self.GetHandle())
        elif sys.platform.startswith('darwin'):
            self.player.set_nsobject(self.GetHandle())
        event.Skip()

    def play_media(self, media_path):
        media = self.Instance.media_new(media_path)
        self.player.set_media(media)
        self.player.play()

    def stop(self):
        self.player.stop()

    def mute(self):
        self.player.audio_toggle_mute()

    def set_volume(self, volumen):
        self.player.audio_set_volume(volumen)