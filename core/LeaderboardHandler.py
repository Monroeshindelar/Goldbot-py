import logging
import pytz
import json
import os
from datetime import datetime
from _global.Config import Config

LOGGER = logging.getLogger("goldlog")
EMOJI_TIME_DICT = Config.get_config_property("server", "leaderboard", "emojiMap")
TZ = pytz.timezone(Config.get_config_property("server", "timezone"))


class LeaderboardHandler:
    __instance = None

    @staticmethod
    def get_leaderboard_handler():
        if LeaderboardHandler.__instance is None:
            LeaderboardHandler()
        return LeaderboardHandler.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Cannot create another instance of LeaderboardHandler, one already exists.")
        else:
            LOGGER.info("Creating leaderboard handler")
            LeaderboardHandler.__instance = self
            self.__unprocessed_entries = []

    def add_entry(self, user_id, timestamp, emote):
        for entry in self.__unprocessed_entries:
            if entry["user_id"] == user_id and entry["emote"] == emote:
                return
        if emote in EMOJI_TIME_DICT.keys():
            fixed_timestamp = timestamp.time().replace(second=0, microsecond=0)
            r_time = datetime.strptime(EMOJI_TIME_DICT[emote], "%H:%M").time()
            m_time = r_time.replace(hour=r_time.hour + 12)
            if fixed_timestamp == r_time or fixed_timestamp == m_time or fixed_timestamp == \
                    r_time.replace(minute=r_time.minute + 1) or fixed_timestamp == m_time.replace(minute=m_time.minute + 1):
                self.__unprocessed_entries.append({"user_id": user_id, "timestamp": timestamp, "emote": emote})
                LOGGER.info("LeaderboardHandler::add_entry - Adding message from " + str(user_id) +
                            " to the message queue for the emote " + emote)

    def process_entries(self):
        LOGGER.info("LeaderboardHandler::process_entries - Processing leaderboard entries")
        for emoji in EMOJI_TIME_DICT.keys():
            leaderboard_path = Config.get_config_property("saveDir") + "/leaderboards/307026836066533377/" + emoji \
                               + ".json"
            if not os.path.isfile(leaderboard_path) or os.path.isfile(leaderboard_path) and not os.access(leaderboard_path, os.R_OK):
                with open(leaderboard_path, "w") as f:
                    json.dump({}, f, indent=4)

            with open(leaderboard_path) as f:
                leaderboard_json = json.load(f)

            entries = [entry for entry in self.__unprocessed_entries if entry["emote"] == emoji]
            time = datetime.strptime(EMOJI_TIME_DICT[emoji], "%H:%M")
            for entry in entries:
                if (entry["timestamp"].hour == time.hour or entry["timestamp"].hour == time.hour + 12) and entry["timestamp"].minute == time.minute:
                    if entries.index(entry) == 0:
                        score = Config.get_config_property("server", "leaderboard", "scores", "max")
                    else:
                        score = Config.get_config_property("server", "leaderboard", "scores", "default")
                else:
                    score = Config.get_config_property("server", "leaderboard", "scores", "min")
                    entry["timestamp"] = None

                try:
                    user_score = leaderboard_json[str(entry["user_id"])]
                except KeyError:
                    user_score = {
                        "score": 0,
                        "current_streak": 1,
                        "longest_streak": 1,
                        "timestamp": None
                    }

                if user_score["score"] + score < 0:
                    user_score["score"] = 0
                else:
                    user_score["score"] = user_score["score"] + score

                try:
                    last_timestamp = datetime.strptime(user_score["timestamp"], "%m/%d/%Y")
                except TypeError:
                    last_timestamp = None
                user_score["timestamp"] = datetime.strftime(entry["timestamp"], "%m/%d/%Y")

                try:
                    if entry["timestamp"] is None:
                        user_score["current_streak"] = 0
                    elif (entry["timestamp"].date() - last_timestamp.date()).days == 1:
                        user_score["current_streak"] = user_score["current_streak"] + 1
                    elif (entry["timestamp"].date() - last_timestamp.date()).days > 1:
                        user_score["current_streak"] = 1
                except AttributeError:
                    pass

                if user_score["current_streak"] > user_score["longest_streak"]:
                    user_score["longest_streak"] = user_score["current_streak"]
                leaderboard_json[str(entry["user_id"])] = user_score
                self.__unprocessed_entries.remove(entry)

            current_day = datetime.now().date()
            for key in leaderboard_json:
                try:
                    score = leaderboard_json[key]
                    if (current_day - datetime.strptime(score["timestamp"], "%m/%d/%Y").date()).days > 1:
                        score["current_streak"] = 0
                        leaderboard_json[key] = score
                except KeyError:
                    pass

            with open(leaderboard_path, "w") as f:
                json.dump(leaderboard_json, f, indent=4)
