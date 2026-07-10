import os
import base64
from flask import Flask, render_template, jsonify, send_from_directory
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC

app = Flask(__name__)

# Carpeta donde se guardarán los archivos MP3
MUSIC_DIR = os.path.join(os.path.dirname(__file__), 'canciones')
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

def metadata_extractor(file_path):
    """Extrae metadatos y carátula de un archivo MP3."""
    datos = {
        "titulo": "Canción Desconocida",
        "artista": "Artista Desconocido",
        "album": "Álbum Desconocido",
        "anio": "----",
        "duracion": 0,
        "caratula": ""
    }
    
    try:
        # Obtener duración
        audio = MP3(file_path)
        datos["duracion"] = int(audio.info.length)
        
        # Obtener etiquetas ID3
        id3 = ID3(file_path)
        
        if 'TIT2' in id3: datos["titulo"] = str(id3['TIT2'])
        if 'TPE1' in id3: datos["artista"] = str(id3['TPE1'])
        if 'TALB' in id3: datos["album"] = str(id3['TALB'])
        if 'TDRC' in id3: datos["anio"] = str(id3['TDRC'])
        
        # Extraer carátula (APIC)
        for key in id3.keys():
            if key.startswith('APIC'):
                apic = id3[key]
                mime = apic.mime
                b64_data = base64.b64encode(apic.data).decode('utf-8')
                datos["caratula"] = f"data:{mime};base64,{b64_data}"
                break
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        
    return datos

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/api/canciones')
def listar_canciones():
    """Devuelve la lista de canciones con sus metadatos."""
    lista = []
    for archivo in os.listdir(MUSIC_DIR):
        if archivo.lower().endswith('.mp3'):
            ruta_completa = os.path.join(MUSIC_DIR, archivo)
            meta = metadata_extractor(ruta_completa)
            meta["archivo"] = archivo
            lista.append(meta)
    return jsonify(lista)

@app.route('/musica/<path:filename>')
def servir_musica(filename):
    """Ruta para hacer streaming del archivo de audio."""
    return send_from_directory(MUSIC_DIR, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)