try:
    import yt_dlp
    import os
except ImportError:
    print("Por favor, instala el módulo yt-dlp con pip install yt-dlp")


def configurar_spotify():
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    CLIENT_ID = '79220c1558cb410c9bdb102f77d67447'
    CLIENT_SECRET = '3b9aa57d9c7143728611a584889abab8'
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def descargar_audio(url, formato, calidad, ruta_guardado, hook_progreso, ruta_ffmpeg):
    """
    Descarga y convierte el audio de un video de YouTube usando yt_dlp.

    :param url: URL del video.
    :param formato: Formato de salida (ej. "mp3", "wav", "aac").
    :param calidad: Calidad del audio (ej. "192", "256", "320").
    :param ruta_guardado: Carpeta donde se guardará el audio.
    :param hook_progreso: Función de callback para actualizar el progreso.
    :param ruta_ffmpeg: Ruta donde se encuentra ffmpeg (y ffprobe).
    """
    opciones = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': formato,
            'preferredquality': calidad,
        }],
        'outtmpl': os.path.join(ruta_guardado, '%(title)s.%(ext)s'),
        'ffmpeg_location': ruta_ffmpeg,
        'progress_hooks': [hook_progreso],
        'noplaylist': False,  # Descarga la lista de reproducción completa
        'ignoreerrors': True,  # Maneja errores en videos individuales
    }
    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])
