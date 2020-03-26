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

    def get_leaderboard_info(self, emote):
        if emote in self.__scores:
            return self.__scores[emote]
        else:
            LOGGER.error("UserAccount::get_score - " + emote + " does not have its score tracked for user " + str(self.__id))
            return None

    def set_leaderboard_info(self, emote, score, timestamp):
        if emote not in self.__scores:
            # Adding all the initial leaderboard tracking information for a new user
            LOGGER.warning("UserAccount::set_score - " + emote + " wasn't previously tracked for " + str(self.__id) +
                                                                 ". Adding score tracking.")
            self.__scores.update({emote: {
                "score": 0,
                "last_received": None,
                "current_streak": 0,
                "longest_streak": 0
            }})
        timestamp = timestamp.replace(microsecond=0)
        current_info = self.get_leaderboard_info(emote)
        if current_info["score"] + score < 0:
            current_info["score"] = 0
        else:
            current_info["score"] = current_info["score"] + score

        last_ts = current_info["last_received"]
        current_info["last_received"] = timestamp

        if last_ts is not None:
            if timestamp is None:
                current_info["current_streak"] = 0
            elif (timestamp.date() - last_ts.date()).days == 1:
                current_info["current_streak"] = current_info["current_streak"] + 1
            elif (timestamp.date() - last_ts.date()).days > 1:
                current_info["current_streak"] = 1

        if current_info["current_streak"] > current_info["longest_streak"]:
            current_info["longest_streak"] = current_info["current_streak"]

        self.__scores[emote] = current_info
        core.UserAccounts.save_accounts()
        LOGGER.info("UserAccount::set_score - " + emote + " score adjusted for " + str(self.__id))
