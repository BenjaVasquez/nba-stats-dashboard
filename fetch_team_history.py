import json
import time
import pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder

def fetch_team_history():
    print("--- Extrayendo Historial de Equipos (Desde 2023) ---")
    nba_teams = teams.get_teams()
    history_db = {}

    for team in nba_teams:
        t_id = team['id']
        t_abb = team['abbreviation']
        print(f"📊 Obteniendo juegos de: {team['full_name']}...")

        # Buscamos juegos desde la temporada 2023-24 en adelante
        game_finder = leaguegamefinder.LeagueGameFinder(
            team_id_nullable=t_id,
            season_type_nullable='Regular Season'
        )
        games = game_finder.get_data_frames()[0]

        # Filtramos por fecha (Desde el 1 de enero de 2023)
        games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])
        filtered_games = games[games['GAME_DATE'] >= '2023-01-01'].sort_values('GAME_DATE', ascending=False)

        team_games = []
        for _, row in filtered_games.iterrows():
            team_games.append({
                "date": row['GAME_DATE'].strftime('%Y-%m-%d'),
                "matchup": row['MATCHUP'],
                "wl": row['WL'],
                "pts": row['PTS'],
                "opp_pts": row['PTS'] - row['PLUS_MINUS'],
                "margin": row['PLUS_MINUS']
            })
        
        history_db[t_abb] = team_games
        time.sleep(3.0) # Pausa de seguridad para evitar bloqueos

    with open('team_history.json', 'w', encoding='utf-8') as f:
        json.dump(history_db, f, indent=4, ensure_ascii=False)
    
    print("✅ Historial de equipos guardado en team_history.json")

if __name__ == "__main__":
    fetch_team_history()