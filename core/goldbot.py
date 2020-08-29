import logging
import asyncio
import pytz
from itertools import cycle
from datetime import datetime, timedelta
from discord.utils import find
from core.leaderboardhandler import LeaderboardHandler
from discord.ext import commands
from _global.config import Config
from cogs.helpcommand import HelpCommand

LOGGER = logging.getLogger("goldlog")


class Goldbot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix=command_prefix)
        self.loop.create_task(self.__leaderboard_job())
        self.help_command = HelpCommand()

    async def __leaderboard_job(self):
        tz = pytz.timezone(Config.get_config_property("server", "timezone"))
        await self.wait_until_ready()
        # List of timers as specified in the config
        timers = [(datetime.strptime(entry, "%H:%M")).time() for entry in Config.get_config_property("server",
                  "leaderboard", "emojiMap").values()]
        # Add the military time equivalents to the list
        timers.extend([timer.replace(hour=timer.hour + 12) for timer in timers if timer.hour != 12])
        timers.sort()
        # This part only runs once, I want to find the time it started up so I can find the next available time to
        # schedule the job
        startup_time = tz.localize(datetime.now())
        # shift to the next closest time in the list
        i = 0
        while timers[0] < startup_time.time() and i < len(timers):
            t = timers[0]
            timers.remove(t)
            timers.append(t)
            i = i + 1
        # Make the timers list cycle infinitely
        timers = cycle(timers)

        while not self.is_closed():
            # At startup or after the job is done sleeping, get the current time so we can calculate how many seconds we
            # need to wait until the next job
            current_time = tz.localize(datetime.now())
            # Get the next available time in the timer list
            next_timer = next(timers)
            timer = current_time.replace(hour=next_timer.hour, minute=next_timer.minute + 2, second=0)
            if timer.time() < current_time.time():
                timer = timer + timedelta(days=1)
            LOGGER.info("LeaderboardHandler scheduled to process more entries on " + timer.strftime("%d-%b-%Y (%H:%M)"))
            # Wait until the next time and then run the job
            delay = (timer - current_time).total_seconds()
            await asyncio.sleep(delay)
            LeaderboardHandler.get_leaderboard_handler().process_entries()

    async def on_ready(self):
        LOGGER.info("Logged in.")

    async def on_message(self, message):
        try:
            emoji = find(lambda e: str(e) == message.content, message.guild.emojis)
        except AttributeError:
            return

        if emoji is not None:
            LeaderboardHandler.get_leaderboard_handler().add_entry(message.author.id, message.created_at
                                                                   .replace(tzinfo=pytz.utc)
                                                                   .astimezone(pytz.timezone(Config.get_config_property("server", "timezone"))),
                                                                   emoji.name)

        await self.process_commands(message)
