import requests
import utilities

CHALLONGE_USERNAME = "Monroeshindelar"
API_KEY = utilities.read_token("bin/apikey.txt")
BASE_URL = f"https://{CHALLONGE_USERNAME}:{API_KEY}@api.challonge.com/v1/"


def create_tournament(tournament_name):
    params = {
        "tournament[name]": tournament_name,
        "tournament[url]": tournament_name
    }
    url = f"{BASE_URL}/tournaments.json"
    r = requests.post(url=url, data=params)
    print(r.json())




