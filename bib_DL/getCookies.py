import requests
import http.cookiejar

def getCookies(userName: str, passWord: str, verbous: bool = False):
    # Definiere die URL, zu der du die POST-Anfrage senden möchtest.
    url = 'https://dienstplan.st.roteskreuz.at/Account/Login?ReturnUrl=%2F'

    payload = {
        'UserName': userName,
        'Password': passWord,
        'RememeberMe': 'false',
    }

    # Erstelle ein CookieJar, um Cookies zu speichern.
    cookie_jar = http.cookiejar.CookieJar()

    # Erstelle eine Sitzung und weise ihr das CookieJar zu.
    session = requests.Session()
    session.cookies = cookie_jar

    # Sende die POST-Anfrage mit dem Payload und speichere die empfangenen Cookies.
    response = session.post(url, json=payload)

    # Überprüfe, ob die Anfrage erfolgreich war (Statuscode 200).
    if response.status_code == 200:

        # Gib die empfangenen Cookies aus.
        for cookie in cookie_jar:
            if(verbous): print(f'Cookie: {cookie.name}={cookie.value}\n')
        return cookie_jar
    else:
        print(f'Fehler: {response.status_code}')

if __name__ == '__main__':
    getCookies('', '', True)
