from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import threading

app = Flask(__name__)
CORS(app) # Permite que tu index.html se comunique con el servidor

def run_full_update():
    print("🚀 Iniciando actualización masiva de estadísticas...")
    try:
        # Ejecutamos secuencialmente para no colapsar la señal de la NBA
        scripts = ["fetch_nba_p1.py", "fetch_nba_p2.py", "fetch_nba_p3.py", "fetch_nba_p4.py"]
        
        for script in scripts:
            print(f"⏳ Ejecutando {script}...")
            subprocess.run(["python", script], check=True)
        
        print("🔗 Uniendo archivos JSON...")
        subprocess.run(["python", "merge_data.py"], check=True)
        print("✅ ¡Actualización completa terminada!")
        
    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")

@app.route('/update-stats', methods=['GET'])
def update_stats():
    # Iniciamos el proceso en un "hilo" aparte para que la web no se quede pegada
    thread = threading.Thread(target=run_full_update)
    thread.start()
    return jsonify({"status": "started", "message": "Proceso iniciado en segundo plano. Tardará unos 15-20 minutos."})

if __name__ == '__main__':
    app.run(port=5000)