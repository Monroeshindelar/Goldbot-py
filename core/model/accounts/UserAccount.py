import re
import logging
import core.UserAccounts

LOGGER = logging.getLogger("goldlog")


class UserAccount:
    def __init__(self, _id):
        self.__id = _id
        self.__friend_code = None
        self.__scores = {}

    def get_id(self):
        return self.__id

    def get_friend_code(self):
        return self.__friend_code

    def set_friend_code(self, friend_code):
        success = False
        if friend_code is None:
            LOGGER.warning("UserAccount::set_friend_code - No friend code provided.")
            return None
        elif re.match(pattern="(((SW)|(DS))-)?(\d{4}-){2}(\d{4})", string=friend_code):
            self.__friend_code = friend_code
            success = True
        else:
            LOGGER.error("UserAccount::set_friend_code - " + friend_code + " does not fit the friend code pattern.")
        core.UserAccounts.save_accounts()
        return success
