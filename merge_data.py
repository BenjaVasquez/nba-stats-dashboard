import json

def merge():
    merged_players = []
    for part in ['p1', 'p2', 'p3', 'p4']:
        try:
            with open(f'data_{part}.json', 'r', encoding='utf-8') as f:
                merged_players.extend(json.load(f)['players'])
        except FileNotFoundError:
            print(f"⚠️ Saltando {part}, archivo no encontrado.")
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump({"players": merged_players}, f, indent=4, ensure_ascii=False)
    print(f"🔥 ¡Éxito! data.json generado con {len(merged_players)} jugadores.")

if __name__ == "__main__": merge()