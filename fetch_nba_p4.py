# Equipos: ATL, BOS, BKN, CHA, CHI, CLE, DAL, DEN
import json, time, pandas as pd
from datetime import datetime
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster, playergamelog, playercareerstats, commonplayerinfo

RETRY_COUNT, SLEEP_TIME, TIMEOUT_NBA = 3, 3.0, 60
TEAM_LIST = ['POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']


def safe_api_call(func, **kwargs):
    """Intenta llamar a la API con reintentos automáticos"""
    for i in range(RETRY_COUNT):
        try:
            return func(**kwargs, timeout=TIMEOUT_NBA).get_data_frames()[0]
        except Exception as e:
            time.sleep(1.5)
    return pd.DataFrame()


def format_date(date_str):
    """Convierte fechas raras de la NBA a YYYY-MM-DD"""
    try:
        # La NBA suele enviar "OCT 29, 2025" o formatos similares
        return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except:
        return date_str
    

def calculate_doubles(pts, reb, ast):
    """Calcula si hubo Doble-Doble o Triple-Doble"""
    stats = [pts, reb, ast]
    over_ten = sum(1 for s in stats if s >= 10)
    dd = 1 if over_ten >= 2 else 0
    td = 1 if over_ten >= 3 else 0
    return dd, td

def run():
    # 1. Filtramos los equipos de esta parte
    all_teams = [t for t in teams.get_teams() if t['abbreviation'] in TEAM_LIST]
    data = {"players": []}
    
    print(f"🚀 Iniciando Parte 1: {len(all_teams)} equipos")

    for team in all_teams:
        print(f"🏀 Procesando: {team['full_name']}...")
        
        # Obtenemos la plantilla completa (incluye ID y POSICIÓN)
        roster = safe_api_call(commonteamroster.CommonTeamRoster, team_id=team['id'])
        
        if roster.empty:
            print(f"⚠️ Error cargando roster de {team['abbreviation']}")
            continue

        for _, player_row in roster.iterrows():
            try:
                p_id = player_row['PLAYER_ID']
                p_name = player_row['PLAYER']
                # Optimización: Sacamos la posición de aquí, no de CommonPlayerInfo
                p_pos = player_row.get('POSITION', '---')
                
                # Solo llamamos al GameLog (1 llamada por jugador en lugar de 3)
                log = safe_api_call(playergamelog.PlayerGameLog, player_id=p_id, season='2025-26')
                
                history = []
                # Acumuladores para promedios de temporada
                total_pts = total_reb = total_ast = total_tpm = total_min = total_dd = total_td = 0
                games_played = len(log)

                if not log.empty:
                    # Procesamos cada partido
                    for _, r in log.iterrows():
                        pts = int(r['PTS'])
                        reb = int(r['REB'])
                        ast = int(r['AST'])
                        tpm = int(r['FG3M'])
                        try:
                            min_played = float(r['MIN'])
                        except:
                            min_played = 0.0

                        dd, td = calculate_doubles(pts, reb, ast)
                        
                        # Sumar para promedios
                        total_pts += pts
                        total_reb += reb
                        total_ast += ast
                        total_tpm += tpm
                        total_min += min_played
                        total_dd += dd
                        total_td += td

                        # Guardamos partido individual
                        # Solo guardamos los últimos 25 para el gráfico (ahorra espacio)
                        if len(history) < 25:
                            history.append({
                                "date": format_date(r['GAME_DATE']),
                                "opponent": r['MATCHUP'].split()[-1], # Solo el rival (ej. LAL)
                                "result": r['WL'],
                                "margin": int(r['PLUS_MINUS']) if r['PLUS_MINUS'] else 0,
                                "pts": pts,
                                "reb": reb,
                                "ast": ast,
                                "tpm": tpm,
                                "tpa": int(r['FG3A']),
                                "ft_m": int(r['FTM']),
                                "ft_a": int(r['FTA']),
                                "stl": int(r['STL']),
                                "blk": int(r['BLK']),
                                "min": str(r['MIN']),
                                "dd2": dd,
                                "dd3": td
                            })
                
                # Ordenamos cronológicamente para el gráfico (antiguo -> nuevo)
                history.reverse()

                # Calculamos promedios matemáticamente (ahorra llamada a CareerStats)
                if games_played > 0:
                    avgs = {
                        "pts": round(total_pts / games_played, 1),
                        "reb": round(total_reb / games_played, 1),
                        "ast": round(total_ast / games_played, 1),
                        "tpm": round(total_tpm / games_played, 1),
                        "min": round(total_min / games_played, 1),
                        "dd2": total_dd,
                        "td3": total_td,
                        "gp": games_played
                    }
                else:
                    avgs = {"pts": 0, "reb": 0, "ast": 0, "tpm": 0, "min": 0, "dd2": 0, "td3": 0}

                # Estructura Final del Jugador
                player_obj = {
                    "id": p_id,
                    "name": p_name,
                    "team": team['abbreviation'],
                    "bio": {
                        "pos": p_pos,
                        # Altura/Peso/Salario se llenan luego con fetch_bios_salaries.py
                    },
                    "season_averages": avgs,
                    "last_15": history
                }

                data["players"].append(player_obj)
                print(f"   ✅ {p_name} ({games_played} games)")
                
                # Pausa pequeña para no saturar
                time.sleep(SLEEP_TIME)

            except Exception as e:
                print(f"   ❌ Error con {p_name}: {e}")
                continue

    # Guardado final
    with open('data_p1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("✅ Parte 1 completada exitosamente.")

if __name__ == "__main__":
    run()