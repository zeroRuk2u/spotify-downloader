from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Página principal con formulario
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        playlist_url = request.form.get("playlist_url")
        if not playlist_url:
            return "⚠️ Ingresa una URL de playlist", 400
        
        canciones = obtener_nombres_playlist(playlist_url)
        resultados = [descargar_cancion(c) for c in canciones]

        return render_template_string(PAGE_TEMPLATE, mensaje="Proceso terminado", resultados=resultados)

    return render_template_string(PAGE_TEMPLATE, mensaje=None, resultados=[])

# Plantilla HTML con formulario
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

if __name__ == "_main_":
    app.run(debug=True, host="0.0.0.0", port=5000)
