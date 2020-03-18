import logging
from datetime import date
from discord.ext import commands
from _global.Config import Config


LOGGER = logging.getLogger("goldlog")
LOGGER.setLevel(logging.DEBUG)

today = date.today()
fh = logging.FileHandler("bin/log/" + str(today) + "_goldbot.log")
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
LOGGER.addHandler(ch)
LOGGER.addHandler(fh)

TOKEN = Config.get_config_property(config_property="discord_api_key")
BOT_PREFIX = "."

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


# @bot.event
# async def on_command_error(ctx, error):
#     message = ""
#     if isinstance(error, commands.MissingAnyRole):
#         message = "You do not have the required role to execute this command.\n" \
#                   "Required roles are:\n"
#         for role in error.missing_roles:
#             message += "`" + role + "`\n"
#     elif isinstance(error, commands.MissingRequiredArgument):
#         message = "You are missing required arguments for this command:\n`" + error.param.name + "`"
#     elif isinstance(error, commands.BadArgument):
#         message = error.args[0]
#
#     # await ctx.channel.send(content=message)

@bot.event
async def on_ready():
    LOGGER.info("Logged in.")

bot.run(TOKEN, bot=True, reconnect=True)
