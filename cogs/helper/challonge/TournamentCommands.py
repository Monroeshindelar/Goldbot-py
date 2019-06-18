import requests
import utilities

CONF = utilities.read_config("bin/config.txt")
API_KEY = CONF["challonge_api_key"]
CHALLONGE_USERNAME = CONF["challonge_username"]
BASE_URL = "https://" + CHALLONGE_USERNAME + ":" + API_KEY + "@api.challonge.com/v1/"


def index_tournaments():
    url = BASE_URL + "tournaments.json"
    r = requests.get(url=url)
    return r.json()


def create_tournament(tournament_name, extraParams):
    params = {
        "tournament[name]": tournament_name,
        "tournament[url]": tournament_name
    }
    if extraParams is not None:
        for arg in extraParams:
            tokens = arg.split('=')
            trim_underscores = tokens[1].split('_')
            tokens[1] = ""
            for token in trim_underscores:
                tokens[1] += token + " "

            tokens[1] = tokens[1].strip()

            newParam = {
                "tournament[" + tokens[0] + "]": tokens[1]
            }

            params.update(newParam)

    url = BASE_URL + "tournaments.json"
    r = requests.post(url=url, data=params)
    print(r.json())


def destroy_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + ".json"
    r = requests.delete(url=url)
    print(r.json())


def start_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/start.json"
    r = requests.post(url=url)
    print(r.json())


def finalize_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/finalize.json"
    r = requests.post(url=url)
    print(r.json())


def reset_tournament(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "reset.json"
    r = requests.post(url=url)
    print(r.json())


def index_participants(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/participants.json"
    r = requests.get(url=url)
    return r.json()


def add_users(tournament_name, users):
    url = BASE_URL + "tournaments/" + tournament_name + "/participants"
    params = None
    if len(users) > 1:
        url += "/bulk_add"
        participants = []
        for user in users:
            participants.append(user.name)
        params = {
            "participants[][name]": participants
        }
    elif len(users) == 1:
        params = {
            "participant[name]": users[0].name
        }
    url += ".json"
    r = requests.post(url=url, data=params)
    print(r.json())


def destroy_participant(tournament_name, participant_name):
    participant_id = get_participant_id_by_name(participant_name)
    url = BASE_URL + "tournaments/" + tournament_name + "/participants/" + participant_id + ".json"
    r = requests.delete(url=url)
    print(r.json())


def shuffle_seeds(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/participants/randomize.json"
    r = requests.post(url=url)
    print(r.json())


def index_matches(tournament_name):
    url = BASE_URL + "tournaments/" + tournament_name + "/matches.json"
    r = requests.get(url=url)
    return r.json()


def update_match(tournament_name, participant1_name, participant2_name, participant1_score, participant2_score):
    matches = index_matches(tournament_name)
    participant1_id = get_participant_id_by_name(tournament_name, participant1_name)
    participant2_id = get_participant_id_by_name(tournament_name, participant2_name)
    participants = [participant1_id, participant2_id]
    match_to_update = None

    for match in matches:
        if (match['match']["player1_id"] in participants) and (match['match']["player2_id"] in participants):
            match_to_update = match['match']
            break

    if match_to_update['player1_id'] != participant1_id:
        temp = participant2_id
        participant2_id = participant1_id
        participant1_id = temp

        temp = participant2_score
        participant2_score = participant1_score
        participant1_score = temp

    url = BASE_URL + "tournaments/" + tournament_name + "/matches/" + str(match_to_update["id"]) + ".json"

    if participant1_score > participant2_score:
        winner = {
            "id": participant1_id,
            "score": participant1_score
        }
    else:
        winner = {
            "id": participant2_id,
            "score": participant2_score
        }

    params = {
        "match[scores_csv]": participant1_score + "-" + participant2_score,
        "match[winner_id]": winner["id"]
    }
    r = requests.put(url=url, data=params)
    print(r.json())


def get_participant_id_by_name(tournament_name, participant_name):
    participants = index_participants(tournament_name)
    for participant in participants:
        if participant['participant']['name'] == participant_name:
            return participant['participant']['id']
    return None


def get_match_by_participants(tournament_name, participant1_id, participant2_id):
    matches = index_matches(tournament_name)
    for match in matches:
        if (match["player1_id"] == participant1_id) and (match["player2_id"] == participant2_id):
            return match
    return None