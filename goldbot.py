# TODO: Proper logging

import logging
from discord.ext import commands
from _global.Config import Config

TOKEN = Config.get_config_property(config_property="discord_api_key")
BOT_PREFIX = "!"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cogs = [
    'cogs.TournamentCog',
    'cogs.UserAccountCog',
    'cogs.SquadlockeCog'
]

bot = commands.Bot(command_prefix=BOT_PREFIX)

if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)


@bot.event
async def on_ready():
    print('Logged in')


bot.run(TOKEN, bot=True, reconnect=True)
