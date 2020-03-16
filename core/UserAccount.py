import re
import logging
import core.UserAccounts

LOGGER = logging.getLogger("goldlog")


class UserAccount:
    def __init__(self, _id, friend_code=None):
        self.__id = _id
        self.set_friend_code(friend_code)
        self.__scores = {'weed': 0, 'bush': 0}

    def get_id(self):
        return self.__id

    def get_friend_code(self):
        return self.__friend_code

    def set_friend_code(self, friend_code):
        success = False
        if re.match(pattern="(((SW)|(DS))-)?(\d{4}-){2}(\d{4})", string=friend_code):
            self.__friend_code = friend_code
            success = True
        else:
            LOGGER.error("UserAccount::set_friend_code - " + friend_code + " does not fit the friend code pattern")
        core.UserAccounts.save_accounts()
        return success

    def get_score(self, emote):
        if emote in self.__scores:
            return self.__scores[emote]
        else:
            LOGGER.error("UserAccount::get_score - " + emote + " does not have its score tracked")
            return None

    def set_score(self, emote, score):
        current_score = self.get_score(emote)
        if current_score is not None:
            if current_score + score < 0:
                self.__scores[emote] = 0
            else:
                self.__scores[emote] += score
        else:
            LOGGER.warning("UserAccount::set_score - " + emote + "does not have its score tracked")