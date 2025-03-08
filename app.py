from flask import Flask, request, jsonify
import os
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(_name_)

# Credenciales de Spotify
CLIENT_ID = "c5f9d259f8ba4a448c9055cc0befa4df"
CLIENT_SECRET = "c060f93e1a3f4321a386e995f31151fe"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Carpeta donde se guardarán las canciones
MUSIC_FOLDER = "musica"
os.makedirs(MUSIC_FOLDER, exist_ok=True)

def obtener_nombres_playlist(playlist_url, limite=100):
    """Obtiene los nombres de las canciones de una playlist de Spotify."""
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    canciones = []
    offset = 0
    while len(canciones) < limite:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=100)
        if not results or 'items' not in results or not results['items']:
            break
        for item in results['items']:
            track = item.get('track')
            if track:
                nombre = track.get('name', 'Desconocido')
                artista = track['artists'][0]['name'] if track.get('artists') else 'Desconocido'
                canciones.append(f"{nombre} - {artista}")
        offset += 100
    return canciones[:limite]

def descargar_cancion(nombre_cancion):
    """Busca la canción en YouTube y la descarga en MP3 si no existe."""
    nombre_archivo = os.path.join(MUSIC_FOLDER, f"{nombre_cancion}.mp3")
    if os.path.exists(nombre_archivo):
        return f"⚠️ {nombre_cancion} ya existe."

    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': nombre_archivo,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'quiet': False
    }
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([f"ytsearch:{nombre_cancion}"])
        return f"✅ Descargado: {nombre_cancion}"
    except Exception as e:
        return f"❌ Error con {nombre_cancion}: {str(e)}"

@app.route("/")
def home():
    return "🎵 API de Descarga de Música - Envia una URL de Playlist"

@app.route("/descargar", methods=["POST"])
def descargar():
    data = request.json
    playlist_url = data.get("playlist_url")

    if not playlist_url:
        return jsonify({"error": "Falta la URL de la playlist"}), 400

    canciones = obtener_nombres_playlist(playlist_url)
    resultados = [descargar_cancion(c) for c in canciones]

    return jsonify({"mensaje": "Proceso terminado", "resultados": resultados})

if _name_ == "_main_":
    app.run(debug=True, port=5000)
