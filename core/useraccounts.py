from utilities.misc import read_save_file, save_file
from core.model.accounts.useraccount import UserAccount
from _global.config import Config

ACCOUNTS_FILE_PATH = Config.get_config_property("saveDir") + "/accounts/accounts.pkl"
ACCOUNTS = read_save_file(ACCOUNTS_FILE_PATH)


def get_account(prof):
    if prof.bot:
        return None
    return __get_or_create_account(prof.id)


def save_accounts():
    save_file(ACCOUNTS, ACCOUNTS_FILE_PATH)


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
