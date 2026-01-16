import json
import os

def merge_player_data():
    merged_players = []
    # Lista de los archivos generados por las 4 partes
    source_files = ['data_p1.json', 'data_p2.json', 'data_p3.json', 'data_p4.json']
    
    print("--- Iniciando unión de datos ---")

    for file_name in source_files:
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Verificamos que el archivo tenga la clave 'players' y sea una lista
                    if 'players' in data and isinstance(data['players'], list):
                        players_count = len(data['players'])
                        merged_players.extend(data['players'])
                        print(f"✅ {file_name} cargado: {players_count} jugadores encontrados.")
                    else:
                        print(f"⚠️ {file_name} no tiene el formato esperado (falta clave 'players').")
            except Exception as e:
                print(f"❌ Error al leer {file_name}: {e}")
        else:
            print(f"❌ Archivo no encontrado: {file_name}")

    # Estructura final del JSON
    final_data = {
        "players": merged_players,
        "last_update": "2026-01-16" # Puedes usar datetime para esto
    }

    # Guardar el resultado final
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    total_final = len(merged_players)
    print(f"--- Unión finalizada ---")
    print(f"📊 ¡Éxito! data.json generado con {total_final} jugadores en total.")

if __name__ == "__main__":
    merge_player_data()