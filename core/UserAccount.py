import re
import core.UserAccounts


class UserAccount:
    def __init__(self, _id, friend_code=None):
        self.__id = _id
        self.set_friend_code(friend_code)

    def get_id(self):
        return self.__id

    def get_friend_code(self):
        return self.__friend_code

    def set_friend_code(self, friend_code):
        # TODO: Regex for detecting proper friend code format
        self.__friend_code = friend_code
        core.UserAccounts.save_accounts()
