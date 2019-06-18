import os
import pickle
from utilities import read_config
from core.UserAccount import UserAccount

CONF = read_config("bin/config.txt")
ACCOUNTS_FILE_PATH = CONF["accounts_file"]
accounts = []

if os.path.exists(ACCOUNTS_FILE_PATH):
    with open(ACCOUNTS_FILE_PATH, "rb") as accounts_file:
        accounts = pickle.load(accounts_file)
else:
    accounts_file = open(ACCOUNTS_FILE_PATH, "wb+")
    pickle.dump(accounts, accounts_file, pickle.HIGHEST_PROTOCOL)


def get_account(_id):
    return __get_or_create_account(_id)


def save_accounts():
    with open(ACCOUNTS_FILE_PATH, 'wb+') as outfile:
        pickle.dump(accounts, outfile, pickle.HIGHEST_PROTOCOL)


def __get_or_create_account(_id):
    return_account = None
    for account in accounts:
        if account.get_id() == _id:
            return_account = account
            break
    if return_account is None:
        return_account = __create_account(_id)
    return return_account


def __create_account(_id):
    account = UserAccount(_id)
    accounts.append(account)
    save_accounts()
    return account
