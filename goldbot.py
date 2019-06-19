# TODO: Create a singleton class for config
# TODO: Proper logging


import utilities
from discord.ext import commands

CONF = utilities.read_config("bin/config.txt")
BOT_PREFIX = "!"
TOKEN = CONF["discord_api_key"]

cogs = [
    'cogs.TournamentCog',
    'cogs.UserAccountCog'
]

bot = commands.Bot(command_prefix=BOT_PREFIX)

if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)


@bot.event
async def on_ready():
    print('Logged in')


bot.run(TOKEN, bot=True, reconnect=True)
