import requests
import utilities

API_KEY = utilities.read_token("bin/apikey.txt")
BASE_URL = "https://api.challonge.com/v1/"


def create_tournament(tournament_name):
    params = {
        "api_key": API_KEY,
        "tournament[name]": tournament_name,
        "tournament[url]": tournament_name
    }
    url = BASE_URL + "tournaments.json"
    r = requests.post(url=url, data=params)
    print(r.json())

def destroy_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + ".json"
    params = {
        "api_key": API_KEY
    }
    r = requests.delete(url=url, params=params)
    print(r.json())
