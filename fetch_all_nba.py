import json
import time
import pandas as pd
from datetime import datetime
from nba_api.stats.static import teams
from nba_api.stats.endpoints import (commonteamroster, playergamelog, 
                                     playercareerstats, commonplayerinfo)

# Configuración de estabilidad para evitar bloqueos
RETRY_COUNT = 3
SLEEP_TIME = 2.5 
TIMEOUT_NBA = 60

def safe_api_call(endpoint_func, **kwargs):
    for i in range(RETRY_COUNT):
        try:
            return endpoint_func(**kwargs, timeout=TIMEOUT_NBA).get_data_frames()[0]
        except Exception as e:
            print(f"⚠️ Reintento {i+1} por error: {e}")
            time.sleep(SLEEP_TIME * 2)
    return pd.DataFrame()

def count_doubles(row):
    """
    Calcula DD2 y TD3 estrictamente para Puntos, Rebotes y Asistencias.
    DD2: 10+ en al menos 2 categorías.
    TD3: 10+ en las 3 categorías.
    """
    # Solo consideramos estas tres categorías según tu solicitud
    stats = [row['PTS'], row['REB'], row['AST']]
    over_ten = sum(1 for s in stats if s >= 10)
    
    dd2 = 1 if over_ten >= 2 else 0
    td3 = 1 if over_ten >= 3 else 0
    return dd2, td3

def fetch_nba_full_data():
    start_time = time.time()
    all_nba_teams = teams.get_teams()
    final_data = {"players": []}
    
    for team in all_nba_teams:
        t_abb, t_full = team['abbreviation'], team['full_name']
        print(f"🏀 Procesando {t_full}...")
        
        roster = safe_api_call(commonteamroster.CommonTeamRoster, team_id=team['id'])
        if roster.empty: continue

        for _, p_row in roster.iterrows():
            p_id, p_name = p_row['PLAYER_ID'], p_row['PLAYER']
            
            # 1. Información Bio
            p_info_df = safe_api_call(commonplayerinfo.CommonPlayerInfo, player_id=p_id)
            bio = {"pos": "N/A", "height": "---", "weight": "---"}
            if not p_info_df.empty:
                info = p_info_df.iloc[0]
                bio = {"pos": info['POSITION'], "height": info['HEIGHT'], "weight": info['WEIGHT']}

            # 2. Historial y conteo de Dobles (Pts, Reb, Ast)
            log = safe_api_call(playergamelog.PlayerGameLog, player_id=p_id, season='2025-26')
            history = []
            season_dd2 = 0
            season_td3 = 0
            
            if not log.empty:
                # Recorremos la temporada completa para los contadores
                for _, r in log.iterrows():
                    dd2, td3 = count_doubles(r)
                    season_dd2 += dd2
                    season_td3 += td3
                
                # Guardamos los últimos 23 para el gráfico detallado
                for _, r in log.head(23).iterrows():
                    history.append({
                        "date": r['GAME_DATE'], 
                        "opponent": r['MATCHUP'].split()[-1],
                        "result": r['WL'], 
                        "margin": r['PLUS_MINUS'],
                        "pts": int(r['PTS']), 
                        "ast": int(r['AST']), 
                        "reb": int(r['REB']),
                        "stl": int(r['STL']),
                        "blk": int(r['BLK']),
                        "tpm": int(r['FG3M']), 
                        "tpa": int(r['FG3A']),
                        "ft_m": int(r['FTM']), 
                        "ft_a": int(r['FTA']),
                        "min": str(r['MIN'])
                    })
            history.reverse()

            # 3. Promedios de la Temporada
            career = safe_api_call(playercareerstats.PlayerCareerStats, player_id=p_id)
            season_avgs = {
                "pts": 0, "reb": 0, "ast": 0, "tpm": 0, "min": 0, 
                "dd2": season_dd2, "td3": season_td3
            }
            if not career.empty:
                s_df = career[career['SEASON_ID'] == '2025-26']
                if not s_df.empty:
                    s = s_df.iloc[0]
                    gp = s['GP'] if s['GP'] > 0 else 1
                    season_avgs.update({
                        "pts": round(s['PTS']/gp, 1),
                        "reb": round(s['REB']/gp, 1),
                        "ast": round(s['AST']/gp, 1),
                        "tpm": round(s['FG3M']/gp, 1),
                        "min": round(s['MIN']/gp, 1)
                    })

            final_data["players"].append({
                "id": p_id, "name": p_name, "team": t_abb,
                "bio": bio, "season_averages": season_avgs, "last_15": history 
            })
            
            print(f"   ✅ {p_name}: {season_dd2} DD2 | {season_td3} TD3")
            time.sleep(SLEEP_TIME)

        # Guardado incremental por equipo para evitar pérdida de datos
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Proceso finalizado. Archivo data.json actualizado.")

if __name__ == "__main__":
    fetch_nba_full_data()