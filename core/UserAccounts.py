from utilities.utilities import read_or_create_file_pkl, save_to_file_pkl
from core.UserAccount import UserAccount
from _global.Config import Config

ACCOUNTS_FILE_PATH = Config.get_config_property("accounts_file")
ACCOUNTS = read_or_create_file_pkl(ACCOUNTS_FILE_PATH)


def get_account(_id):
    return __get_or_create_account(_id)


def save_accounts():
    save_to_file_pkl(ACCOUNTS,ACCOUNTS_FILE_PATH)


def __get_or_create_account(_id):
    return_account = None
    for account in ACCOUNTS:
        if account.get_id() == _id:
            return_account = account
            break
    if return_account is None:
        return_account = __create_account(_id)
    return return_account


def __create_account(_id):
    account = UserAccount(_id)
    ACCOUNTS.append(account)
    save_accounts()
    return account
