import logging
import pytz
import asyncio
import os
from itertools import cycle
from datetime import date, datetime, timedelta
from discord.ext import commands
from discord.utils import find
from _global.Config import Config
from core.LeaderboardHandler import LeaderboardHandler


LOGGER = logging.getLogger("goldlog")
LOGGER.setLevel(logging.DEBUG)

today = date.today()
if not os.path.exists("bin/log"):
    os.makedirs("bin/log")
fh = logging.FileHandler("bin/log/" + str(today) + "_goldbot.log")
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
LOGGER.addHandler(ch)
LOGGER.addHandler(fh)

TOKEN = Config.get_config_property("discordApiKey")
BOT_PREFIX = Config.get_config_property("prefix")

TZ = pytz.timezone(Config.get_config_property("server", "timezone"))
LEADERBOARD_HANDLER = LeaderboardHandler.get_leaderboard_handler()

cogs = [
    "cogs.TournamentCog",
    "cogs.UserAccountCog",
    "cogs.SquadlockeCog",
    "cogs.TenManCog",
    "cogs.ServerCog"
]

bot = commands.Bot(command_prefix=BOT_PREFIX)

if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)


@bot.event
async def on_command_error(ctx, error):
    message = ""
    if isinstance(error, commands.MissingAnyRole):
        message = "You do not have the required role to execute this command.\n" \
                  "Required roles are:\n"
        for role in error.missing_roles:
            message += "`" + role + "`\n"
    elif isinstance(error, commands.MissingRequiredArgument):
        message = "You are missing required arguments for this command:\n`" + error.param.name + "`"
    elif isinstance(error, commands.BadArgument):
        message = error.args[0]
    else:
        print(error)
        return

    await ctx.channel.send(content=message)

async def __leaderboard_job():
    await bot.wait_until_ready()
    # List of timers as specified in the config
    timers = [(datetime.strptime(entry, "%H:%M")).time() for entry in Config.get_config_property("server", "leaderboardTracking").values()]
    # Add the military time equivalents to the list
    timers.extend([timer.replace(hour=timer.hour + 12) for timer in timers if timer.hour != 12])
    timers.sort()
    # This part only runs once, I want to find the time it started up so I can find the next available time to
    # schedule the job
    startup_time = TZ.localize(datetime.now())
    # shift to the next closest time in the list
    i = 0
    while timers[0] <= startup_time.time() and i < len(timers):
        t = timers[0]
        timers.remove(t)
        timers.append(t)
        i = i + 1
    # Make the timers list cycle infinitely
    timers = cycle(timers)

    while not bot.is_closed():
        # At startup or after the job is done sleeping, get the current time so we can calculate how many seconds we
        # need to wait until the next job
        current_time = TZ.localize(datetime.now())
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


@bot.event
async def on_message(message):
    emoji = find(lambda e: str(e) == message.content, message.guild.emojis)
    if emoji is not None:
        LEADERBOARD_HANDLER.add_entry(message.author, datetime.now(), emoji.name)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    LOGGER.info("Logged in.")

bot.loop.create_task(__leaderboard_job())

bot.run(TOKEN, bot=True, reconnect=True)

