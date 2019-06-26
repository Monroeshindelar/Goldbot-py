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
        success = False
        if re.match(pattern="(((SW)|(DS))-)?(\d{4}-){2}(\d{4})", string=friend_code):
            self.__friend_code = friend_code
            success = True
        core.UserAccounts.save_accounts()
        return success
