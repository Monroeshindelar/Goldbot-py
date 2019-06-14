API_URL = "api.challonge.com/v1/"

_credentials = {
    "username": None,
    "api_key": None
}


def get_credentials():
    return _credentials["user_name"], _credentials["api_key"]


def set_credentials(username, api_key):
    _credentials["username"] = username
    _credentials["api_key"] = api_key


def get_api_url():
    return API_URL
