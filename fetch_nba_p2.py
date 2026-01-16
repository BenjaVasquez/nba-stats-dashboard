# Equipos: ATL, BOS, BKN, CHA, CHI, CLE, DAL, DEN
import json, time, pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster, playergamelog, playercareerstats, commonplayerinfo

RETRY_COUNT, SLEEP_TIME, TIMEOUT_NBA = 3, 3.0, 60
TEAM_LIST = ['DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA']

def safe_api_call(func, **kwargs):
    for i in range(RETRY_COUNT):
        try: return func(**kwargs, timeout=TIMEOUT_NBA).get_data_frames()[0]
        except: time.sleep(SLEEP_TIME * 2)
    return pd.DataFrame()

def count_doubles(row):
    stats = [row['PTS'], row['REB'], row['AST']]
    over_ten = sum(1 for s in stats if s >= 10)
    return (1 if over_ten >= 2 else 0), (1 if over_ten >= 3 else 0)

def run():
    all_teams = [t for t in teams.get_teams() if t['abbreviation'] in TEAM_LIST]
    data = {"players": []}
    for team in all_teams:
        print(f"🏀 Part 2: {team['full_name']}")
        roster = safe_api_call(commonteamroster.CommonTeamRoster, team_id=team['id'])
        for _, p in roster.iterrows():
            p_id, p_name = p['PLAYER_ID'], p['PLAYER']
            # Bio
            info = safe_api_call(commonplayerinfo.CommonPlayerInfo, player_id=p_id)
            bio = {"pos": info.iloc[0]['POSITION'] if not info.empty else "---"}
            # Log & Doubles
            log = safe_api_call(playergamelog.PlayerGameLog, player_id=p_id, season='2025-26')
            history, dd2, td3 = [], 0, 0
            if not log.empty:
                for _, r in log.iterrows():
                    d, t = count_doubles(r)
                    dd2 += d; td3 += t
                for _, r in log.head(23).iterrows():
                    partido_dd2, partido_td3 = count_doubles(r)
                    history.append({"date": r['GAME_DATE'], "opponent": r['MATCHUP'].split()[-1], "result": r['WL'], 
                                    "margin": r['PLUS_MINUS'], "pts": int(r['PTS']), 
                                    "ast": int(r['AST']), "reb": int(r['REB']), 
                                    "dd2": partido_dd2, "dd3": partido_td3, 
                                    "tpm": int(r['FG3M']), "tpa": int(r['FG3A']), 
                                    "ft_m": int(r['FTM']), "ft_a": int(r['FTA']),
                                    "stl": int(r['STL']), "blk": int(r['BLK']),
                                    "min": str(r['MIN'])})
            history.reverse()
            # Averages
            career = safe_api_call(playercareerstats.PlayerCareerStats, player_id=p_id)
            avgs = {"pts": 0, "reb": 0, "ast": 0, "tpm": 0, "min": 0, "dd2": dd2, "td3": td3}
            if not career.empty:
                s = career[career['SEASON_ID'] == '2025-26']
                if not s.empty:
                    row = s.iloc[0]; gp = row['GP'] if row['GP'] > 0 else 1
                    avgs.update({"pts": round(row['PTS']/gp, 1), "reb": round(row['REB']/gp, 1), "ast": round(row['AST']/gp, 1), "tpm": round(row['FG3M']/gp, 1), "min": round(row['MIN']/gp, 1)})
            data["players"].append({"id": p_id, "name": p_name, "team": team['abbreviation'], "bio": bio, "season_averages": avgs, "last_15": history})
            print(f"   ✅ {p_name}"); time.sleep(SLEEP_TIME)
    with open('data_p2.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__": run()