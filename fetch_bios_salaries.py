import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_espn_bios():
    # Lista completa de las 30 abreviaturas de equipos para ESPN
    teams = [
        'bos', 'bkn', 'ny', 'phi', 'tor', 'chi', 'cle', 'det', 'ind', 'mil',
        'atl', 'cha', 'mia', 'orl', 'wsh', 'den', 'min', 'okc', 'por', 'utah',
        'gs', 'lac', 'lal', 'phx', 'sac', 'dal', 'hou', 'mem', 'no', 'sa'
    ]
    
    bios = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for team in teams:
        url = f"https://www.espn.cl/basquetbol/nba/equipo/plantel/_/nombre/{team}"
        print(f"Buscando bios de: {team}...")
        
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Buscamos las filas de la tabla de jugadores
            rows = soup.select('section.TeamRoster table tbody tr')

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 7:
                    # El nombre suele estar dentro de un <a> dentro de la primera columna
                    name_tag = cols[0].find('a')
                    name = name_tag.text.strip() if name_tag else cols[0].text.strip()
                    
                    # Ajustamos los índices según la estructura real de ESPN
                    bios[name] = {
                        "posicion": cols[1].text.strip(),
                        "edad": cols[2].text.strip(),
                        "estatura": cols[3].text.strip(),
                        "peso": cols[4].text.strip(),
                        "universidad": cols[5].text.strip(),
                        "salario": cols[6].text.strip()
                    }
            
            # Pausa breve para no saturar a ESPN
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error procesando {team}: {e}")

    # Guardamos con UTF-8 para no perder tildes ni caracteres especiales
    with open('bios.json', 'w', encoding='utf-8') as f:
        json.dump(bios, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Proceso terminado. Se guardaron {len(bios)} biografías.")

if __name__ == "__main__":
    fetch_espn_bios()