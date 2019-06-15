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


def start_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/start.json"
    params = {
        "api_key": API_KEY
    }
    r = requests.post(url=url, data=params)
    print(r.json())


def finalize_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/finalize.json"
    params = {
        "api_key": API_KEY
    }
    r = requests.post(url=url, data=params)
    print(r.json())


def reset_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "reset.json"
    params = {
        "api_key": API_KEY
    }
    r = requests.post(url=url, data=params)
    print(r.json())


def add_users(tournament_name, users):
    url = BASE_URL + "tournaments/" + tournament_name + "/participants"
    params = None
    if len(users) > 1:
        url += "/bulk_add"
        participants = []
        for user in users:
            participants.append(user.name)
        params = {
            "api_key": API_KEY,
            "participants[][name]": participants
        }
    elif len(users) == 1:
        params = {
            "api_key": API_KEY,
            "participant[name]": users[0].name
        }
    url += ".json"
    r = requests.post(url=url, data=params)
    print(r.json())


def shuffle_seeds(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/participants/randomize.json"
    params = {
        "api_key": API_KEY
    }
    r = requests.post(url=url, data=params)
    print(r.json())
