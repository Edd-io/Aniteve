import requests
from bs4 import BeautifulSoup
import threading
import time

AS_URL = "https://anime-sama.pw/"
_cached_url = None
_thread_started = False
_lock = threading.Lock()

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def _fetch_url_logic():
    url = None
    data = fetch_data(AS_URL)
    if data:
        soup = BeautifulSoup(data, 'html.parser')
        button = soup.select_one('.btn-primary')
        if button and button.has_attr('href'):
            initial_url = button['href']
            try:
                response = requests.head(str(initial_url), allow_redirects=True, timeout=10)
                if response.status_code == 200:
                    url = response.url
                    print(f"URL finale après redirection: {url}")
                else:
                    print(f"Status code {response.status_code} pour l'URL: {initial_url}")
                    url = initial_url
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la vérification de l'URL: {e}")
                url = initial_url
        else:
            print("Button with class 'btn-primary' not found or has no href.")
    return url

def _update_loop():
    global _cached_url
    while True:
        try:
            time.sleep(12 * 3600)
            new_url = _fetch_url_logic()
            if new_url:
                with _lock:
                    _cached_url = new_url
                print(f"Updated global URL to: {_cached_url}")
        except Exception as e:
            print(f"Error updating URL in background thread: {e}")

def get_url():
    global _cached_url, _thread_started
    
    with _lock:
        if not _thread_started:
            if _cached_url is None:
                _cached_url = _fetch_url_logic()
            
            t = threading.Thread(target=_update_loop, daemon=True)
            t.start()
            _thread_started = True
        if _cached_url is None:
             return _fetch_url_logic()
        return _cached_url  