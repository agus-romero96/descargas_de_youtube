import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC

# Configuración de Spotify API
CLIENT_ID = '79220c1558cb410c9bdb102f77d67447'
CLIENT_SECRET = '3b9aa57d9c7143728611a584889abab8'
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

def descargar_cancion(track_info):
    # Obtener metadatos de Spotify
    nombre = track_info['name']
    artista = track_info['artists'][0]['name']
    album = track_info['album']['name']
    portada_url = track_info['album']['images'][0]['url']

    # Buscar en YouTube
    query = f"{artista} {nombre} audio"
    with YoutubeDL({'format': 'bestaudio/best', 'quiet': True}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        url_youtube = info['entries'][0]['url']

    # Descargar audio
    with YoutubeDL({
        'format': 'bestaudio/best',
        'outtmpl': f'{artista} - {nombre}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }) as ydl:
        ydl.download([url_youtube])

    # Añadir metadatos y portada
    audio = ID3(f'{artista} - {nombre}.mp3')
    audio.add(TIT2(encoding=3, text=nombre))
    audio.add(TPE1(encoding=3, text=artista))
    audio.add(TALB(encoding=3, text=album))

    # Descargar portada
    import requests
    portada = requests.get(portada_url).content
    audio.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=portada))
    audio.save()

def procesar_playlist(url_playlist):
    playlist = sp.playlist_tracks(url_playlist)
    for item in playlist['items']:
        track_info = item['track']
        descargar_cancion(track_info)

# Ejecución
url = input("Ingresa la URL de Spotify (canción/playlist): ")
if "playlist" in url:
    procesar_playlist(url)
else:
    track_info = sp.track(url)
    descargar_cancion(track_info)
