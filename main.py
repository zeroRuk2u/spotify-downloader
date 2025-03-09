import os
import spotipy
import yt_dlp
from flask import Flask, jsonify, request, render_template_string
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Credenciales de Spotify (asegúrate de usar tus valores reales)
CLIENT_ID = os.environ.get("CLIENT_ID", "c5f9d259f8ba4a448c9055cc0befa4df")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "c060f93e1a3f4321a386e995f31151fe")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# Carpeta donde se guardarán las canciones
MUSIC_FOLDER = "musica"
os.makedirs(MUSIC_FOLDER, exist_ok=True)

# ================================
# 1. Función para obtener canciones de la playlist
# ================================
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

#
# 2. Función para descargar canción desde YouTube
#

def descargar_cancion(nombre_cancion):
    """Busca la canción en YouTube y la descarga en MP3 si no existe."""
    nombre_archivo = os.path.join(MUSIC_FOLDER, f"{nombre_cancion}.mp3")
    if os.path.exists(nombre_archivo):
        return f"⚠️ {nombre_cancion} ya existe."

    opciones = {
    'format': 'bestaudio/best',
    'outtmpl': nombre_archivo,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    'cookies': 'cookies.txt',  # Usa el archivo de cookies
    'quiet': False
    }
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([f"ytsearch:{nombre_cancion}"])
        return f"✅ Descargado: {nombre_cancion}"
    except Exception as e:
        return f"❌ Error con {nombre_cancion}: {str(e)}"

#
# 3. Página principal con formulario
# 
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Spotify Downloader</title>
</head>
<body>
    <h2>🎵 Descargar Playlist de Spotify</h2>
    <form method="POST">
        <label for="playlist_url">URL de la Playlist:</label>
        <input type="text" name="playlist_url" required>
        <button type="submit">Descargar</button>
    </form>
    {% if mensaje %}
        <h3>{{ mensaje }}</h3>
        <ul>
            {% for r in resultados %}
                <li>{{ r }}</li>
            {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        playlist_url = request.form.get("playlist_url")
        if not playlist_url:
            return "⚠️ Ingresa una URL de playlist", 400
        
        canciones = obtener_nombres_playlist(playlist_url)
        resultados = [descargar_cancion(c) for c in canciones]
        return render_template_string(PAGE_TEMPLATE, mensaje="Proceso terminado", resultados=resultados)
    
    # GET: muestra el formulario
    return render_template_string(PAGE_TEMPLATE, mensaje=None, resultados=[])

# 
# 4. Arrancar la aplicación
# 
if __name__ == "_main_":
    # Usa el puerto 5000 (Render suele usar 10000, pero Gunicorn lo sobreescribe)
    app.run(host="0.0.0.0", port=5000, debug=True)
