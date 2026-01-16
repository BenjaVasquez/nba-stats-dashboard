import pandas as pd
import json
from datetime import datetime

TEAM_MAP = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS"
}

# --- DICCIONARIOS DE TRADUCCIÓN ---
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def process_excel_fixture():
    print("--- Procesando fixture.xlsx con Fechas en Español ---")
    try:
        df = pd.read_excel('fixture.xlsx')
        
        if pd.api.types.is_numeric_dtype(df['Fecha']):
            df['DATE_OBJ'] = pd.to_datetime(df['Fecha'], unit='D', origin='1899-12-30')
        else:
            df['DATE_OBJ'] = pd.to_datetime(df['Fecha'])
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        df_future = df[df['DATE_OBJ'] >= today].copy().sort_values(by='DATE_OBJ')
        
        fixture_list = []
        for _, row in df_future.head(60).iterrows():
            dt = row['DATE_OBJ']
            # Construimos la etiqueta en español manualmente
            dia_semana = DIAS[dt.weekday()]
            mes_nombre = MESES[dt.month - 1]
            label_es = f"{dia_semana} {dt.day} de {mes_nombre}"
            
            local_abb = TEAM_MAP.get(str(row['Local']).strip(), str(row['Local']))
            visita_abb = TEAM_MAP.get(str(row['Visita']).strip(), str(row['Visita']))
            
            fixture_list.append({
                "DAY_LABEL": label_es,
                "TIME_ONLY": dt.strftime('%H:%M'),
                "STADIUM": str(row['Estadio']).strip(),
                "MATCHUP": f"{visita_abb} @ {local_abb}",
                "HOME_TEAM": local_abb,
                "AWAY_TEAM": visita_abb
            })
            
        with open('fixture.json', 'w', encoding='utf-8') as f:
            json.dump(fixture_list, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Fixture traducido al español correctamente.")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    process_excel_fixture()