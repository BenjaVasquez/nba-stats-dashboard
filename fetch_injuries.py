import requests
import json
from bs4 import BeautifulSoup

def fetch_injuries():
    print("--- Consultando lesiones ---")
    url = "https://www.espn.com/nba/injuries"
    header = {"User-Agent": "Mozilla/5.0"}
    injury_map = {}
    try:
        response = requests.get(url, headers=header, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table', class_='Table')
        for table in tables:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    p_name = cols[0].text.replace('*', '').strip()
                    status_text = cols[2].text.lower()
                    # Rojo para 'Fuera', Mostaza para 'GTD/Duda'
                    red_keys = ['out', 'season', 'surgery', 'indefinitely', 'sidelined']
                    status_color = "red" if any(x in status_text for x in red_keys) else "yellow"
                    injury_map[p_name] = {"status": status_color, "description": cols[2].text.strip()}
        with open('injuries.json', 'w', encoding='utf-8') as f:
            json.dump(injury_map, f, indent=4, ensure_ascii=False)
        print(f"✅ Injuries.json generado.")
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_injuries()