# TODO: Proper logging
# TODO: Rewrite Goldbot.cs TenManCommands from the ground up
# TODO: Actual help command for individual cogs. Overwrite the build in help commands
# TODO: Clean up input checking for discord commands. Send less messages via await ctx.channel.send
# TODO: HTML Image generation for current matches in ongoing sl tournament
# TODO: Make commands more intuitive and user friendly??
# TODO: I don't like the way I create default sl tournament names. Think of a way to handle that better
# TODO: Write get x json by id / name in TournamentCommands to return as many objects as there are args
# TODO: If pickled file doesnt load because its corrupt destroy it and create a new one

import logging
from discord.ext import commands
from _global.Config import Config

TOKEN = Config.get_config_property(config_property="discord_api_key")
BOT_PREFIX = "."

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cogs = [
    "cogs.TournamentCog",
    "cogs.UserAccountCog",
    "cogs.SquadlockeCog",
    "cogs.TenManCog"
]

bot = commands.Bot(command_prefix=BOT_PREFIX)

if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)


@bot.event
async def on_ready():
    print('Logged in')

bot.run(TOKEN, bot=True, reconnect=True)
