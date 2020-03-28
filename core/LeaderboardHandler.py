import logging
import pytz
from datetime import datetime
from core import UserAccounts
from _global.Config import Config

LOGGER = logging.getLogger("goldlog")
EMOJI_TIME_DICT = Config.get_config_property("server", "leaderboardTracking")
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

    def add_entry(self, author, timestamp, emote):
        for entry in self.__unprocessed_entries:
            if entry["author"].id == author.id and entry["emote"] == emote:
                return
        if emote in EMOJI_TIME_DICT.keys():
            r_time = datetime.strptime(EMOJI_TIME_DICT[emote], "%H:%M").time()
            m_time = r_time.replace(hour=r_time.hour + 12)
            timestamp = TZ.localize(timestamp.replace(second=0, microsecond=0)).time()
            if timestamp == r_time or timestamp == m_time:
                self.__unprocessed_entries.append({"author": author, "timestamp": timestamp, "emote": emote})
                LOGGER.info("LeaderboardHandler::add_entry - Adding message from " + author.name +
                            " to the message queue for the emote " + emote)

    def process_entries(self):
        LOGGER.info("LeaderboardHandler::process_entries - Processing leaderboard entries")
        for emoji in EMOJI_TIME_DICT.keys():
            entries = [entry for entry in self.__unprocessed_entries if entry["emote"] == emoji]
            time = datetime.strptime(EMOJI_TIME_DICT[emoji], "%H:%M")
            for entry in entries:
                if (entry["timestamp"].hour == time.hour or entry["timestamp"].hour == time.hour + 12) and entry["timestamp"].minute == time.minute:
                    if entries.index(entry) == 0:
                        score = 3
                    else:
                        score = 1
                else:
                    score = -1

                account = UserAccounts.get_account(entry["author"].id)
                account.set_score(entry["emote"], score)
                self.__unprocessed_entries.remove(entry)
