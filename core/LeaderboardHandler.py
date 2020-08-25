import logging
import json
import os
import shutil
from datetime import datetime
from datetime import timedelta
from _global.Config import Config
from utilities.Misc import read_json_safe

LOGGER = logging.getLogger("goldlog")


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
        emoji_time_dict = Config.get_config_property("server", "leaderboard", "emojiMap")
        for entry in self.__unprocessed_entries:
            if entry["user_id"] == user_id and entry["emote"] == emote:
                return
        if emote in emoji_time_dict.keys():
            fixed_timestamp = timestamp.time().replace(second=0, microsecond=0)
            r_time = datetime.strptime(emoji_time_dict[emote], "%H:%M").time()
            m_time = r_time.replace(hour=r_time.hour + 12)
            if fixed_timestamp == r_time or fixed_timestamp == m_time or fixed_timestamp == \
                    r_time.replace(minute=r_time.minute + 1) or fixed_timestamp == m_time.replace(minute=m_time.minute + 1):
                self.__unprocessed_entries.append({"user_id": user_id, "timestamp": timestamp, "emote": emote})
                LOGGER.info("LeaderboardHandler::add_entry - Adding message from " + str(user_id) +
                            " to the message queue for the emote " + emote)

    def process_entries(self):
        LOGGER.info("LeaderboardHandler::process_entries - Processing leaderboard entries")
        emoji_time_dict = Config.get_config_property("server", "leaderboard", "emojiMap")
        today = datetime.now()
        if today.day == 1:
            self.__process_score_reset()

        for emoji in emoji_time_dict.keys():
            leaderboard_path = Config.get_config_property("saveDir") + "/leaderboards/307026836066533377/" + emoji \
                               + ".json"
            leaderboard_json = read_json_safe(leaderboard_path)

            entries = [entry for entry in self.__unprocessed_entries if entry["emote"] == emoji]
            time = datetime.strptime(emoji_time_dict[emoji], "%H:%M")
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
                        "longest_streak": 0,
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
                try:
                    user_score["timestamp"] = datetime.strftime(entry["timestamp"], "%m/%d/%Y")
                except TypeError:
                    user_score["timestamp"] = None

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
                except (KeyError, TypeError):
                    pass

            with open(leaderboard_path, "w") as f:
                json.dump(leaderboard_json, f, indent=4)

    def __process_score_reset(self):
        base_path = Config.get_config_property("saveDir") + "/leaderboards/307026836066533377/"
        global_path = base_path + "global.json"
        global_leaderboard = read_json_safe(global_path)
        aggregate_scores_dict = {}
        yesterday = datetime.now() - timedelta(days=1)
        emoji_time_dict = Config.get_config_property("server", "leaderboard", "emojiMap")

        try:
            os.makedirs(base_path + "old/" + str(yesterday.month) + "-" + str(yesterday.year))
        except OSError:
            pass

        for emoji in emoji_time_dict.keys():
            leaderboard_path = base_path + emoji + ".json"
            try:
                leaderboard_json = read_json_safe(leaderboard_path)
            except FileNotFoundError:
                continue

            score_sorted = sorted(leaderboard_json, key=lambda e: (leaderboard_json[e]["score"],
                                  leaderboard_json[e]["current_streak"], leaderboard_json[e]["longest_streak"]),
                                  reverse=True)
            for i, k in zip(range(len(score_sorted), 0, -1), score_sorted):
                try:
                    user_global_score = aggregate_scores_dict[k]
                except KeyError:
                    user_global_score = 0
                aggregate_scores_dict[k] = user_global_score + i

            shutil.move(leaderboard_path, base_path + "old/" + str(yesterday.month) + "-" + str(yesterday.year) + "/" +
                        emoji + ".json")

        for k in aggregate_scores_dict.keys():
            try:
                user_score = global_leaderboard[k]
            except KeyError:
                user_score = 0

            user_score = user_score + (aggregate_scores_dict[k] * 10)
            global_leaderboard[k] = user_score

        with open(global_path, "w") as f:
            json.dump(global_leaderboard, f, indent=4)
