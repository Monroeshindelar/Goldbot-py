import os
import pickle
from utilities import read_config
from core.UserAccount import UserAccount

CONF = read_config("bin/config.txt")
ACCOUNTS_FILE_PATH = CONF["accounts_file"]
accounts = []

if os.path.exists(ACCOUNTS_FILE_PATH):
    # open the file
    with open(ACCOUNTS_FILE_PATH, "rb") as accounts_file:
        # read the file into accounts
        accounts = pickle.load(accounts_file)
else:
    accounts_file = open(ACCOUNTS_FILE_PATH, "wb+")
    pickle.dump(accounts, accounts_file, pickle.HIGHEST_PROTOCOL)


def get_account(_id):
    return get_or_create_account(_id)


def modify_account(old_account, new_account):
    accounts[accounts.index(old_account)] = new_account
    save_accounts()


def save_accounts():
    with open(ACCOUNTS_FILE_PATH, 'wb') as outfile:
        pickle.dump(accounts, outfile, pickle.HIGHEST_PROTOCOL)


def get_or_create_account(_id):
    acc = None
    for account in accounts:
        if account.id is _id:
            acc = account
            break
    if acc is None:
        acc = create_account(_id)
    return acc


def create_account(_id):
    account = UserAccount(_id)
    accounts.append(account)
    save_accounts()
    return account
