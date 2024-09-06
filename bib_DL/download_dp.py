import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'bib_DL'))

import getCookies

def extract_string_from_button_element(response, verbous=False):
    # Lese die heruntergeladene Seite mit BeautifulSoup ein.
    soup = BeautifulSoup(response.content, 'html.parser')

    # Suche nach dem <button>-Element und extrahiere den Wert des "onclick"-Attributs.
    button_element = soup.find('button', {'onclick': True})
    if button_element:
        onclick_value = button_element['onclick']
        # Extrahiere den gewünschten String.
        start_index = onclick_value.find("'") + 1
        end_index = onclick_value.rfind("'")
        extracted_string = onclick_value[start_index:end_index]
        if verbous: print('Extrahierter String:', extracted_string)
        return extracted_string
    else:
        if verbous: print('Button-Element nicht gefunden.')

def download_dp(starting_with: str, count_of_dps: int, username="", password="", verbous=False):
    url = 'https://dienstplan.st.roteskreuz.at/Home/Dienstplan/'+ starting_with+ '-00000000-0000-0000-0000-000000000000-57' 
    cookie_jar = getCookies.getCookies(userName=username, passWord=password)

    cookie_string = ""
    for cookie in cookie_jar:
        cookie_string = cookie_string + cookie.name + "=" + cookie.value + ";"
        if verbous: print(f'Cookie: {cookie.name}={cookie.value}\n')

    dps = []
    i = 0
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'de-AT,de;q=0.9,en-AT;q=0.8,en;q=0.7,de-DE;q=0.6,en-US;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': cookie_string ,
        'Host': 'dienstplan.st.roteskreuz.at',
        'Pragma': 'no-cache',
        'Referer': 'https://dienstplan.st.roteskreuz.at/',
        'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        #'Upgrade-Insecure-Requests:': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }
    while i < count_of_dps:
        i=i+1
        # Sende die GET-Anfrage mit den angegebenen Headern.
        response = requests.get(url, headers=headers)
        
        new_url = extract_string_from_button_element(response, verbous=True)
        url = 'https://dienstplan.st.roteskreuz.at/Home/Dienstplan/' + new_url
        dps.append(response.content)
        if verbous: print(f'GET-Anfrage erfolgreich abgeschlossen, und die Seite wurde gespeichert. {i} von {count_of_dps} heruntergeladen.')

    return dps

def extract_csv_vals_from_dp(list_of_dps):
    dp_data = pd.DataFrame(
        {
            'Einheit': [],
            'Zeiten': [],
            'Besatzung': [],
            'Zimmer': [],
            'Datum': []
        }
    )
    for html_content in list_of_dps:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Finde das h2-Feld mit den Informationen für den CSV-Dateinamen
        h2_tag = soup.find('h2')
        if h2_tag:
            csv_dateiname = h2_tag.get_text(strip=True)

            # Ersetze ungültige Zeichen im Dateinamen
            ungültige_zeichen = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
            for zeichen in ungültige_zeichen:
                csv_dateiname = csv_dateiname.replace(zeichen, '')

            
            # Extrahiere das Datum aus dem String
            datum_string = csv_dateiname.split(", ")[1]
            table = soup.find('table')

            # Durchlaufe die Zeilen der Tabelle
            for row in table.find_all('tr'):
                # Extrahiere die Daten aus den Tabellenzellen, aber überspringe Zellen mit der CSS-Klasse "_note"
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells if "_note" not in cell.get('class', [])]
                if row_data:
                    row_data.append(datum_string)  
                    series = pd.Series(row_data, index=['Einheit', 'Zeiten', 'Besatzung', 'Zimmer', 'Datum'])
                    dp_data = dp_data._append(series, ignore_index=True)
                    #df = pd.DataFrame(row_data)
                    #df.rename(index={0: 'Einheit', 1: 'Zeiten', 2: 'Besatzung', 3: 'Zimmer', 4: 'Datum'}, inplace=True)
                    #dp_data = dp_data.join(df)
        else:
            print(f'Warnung: Keine h2-Überschrift in {datum_string}. Die Datei wurde übersprungen.')
    return dp_data


if __name__ == '__main__':
    html_data = download_dp('2022-08-01', 100,username="", password="", verbous=True)
    csv_data = extract_csv_vals_from_dp(html_data)

    print(csv_data)