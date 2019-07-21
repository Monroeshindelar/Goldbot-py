# TODO: Proper logging
# TODO: Actual help command for individual cogs. Overwrite the build in help commands
# TODO: Clean up input checking for discord commands. Send less messages via await ctx.channel.send
# TODO: HTML Image generation for current matches in ongoing sl tournament
# TODO: Make commands more intuitive and user friendly??
# TODO: I don't like the way I create default sl tournament names. Think of a way to handle that better
# TODO: If pickled file doesnt load because its corrupt destroy it and create a new one

from utilities import log
from discord.ext import commands
from _global.Config import Config

logger = log.setup_custom_logger("goldlog")


TOKEN = Config.get_config_property(config_property="discord_api_key")
BOT_PREFIX = "."


cogs = [
    "cogs.error.TenManCogErrorHandling",
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
async def on_command_error(ctx, error):
    message = ""
    if isinstance(error, commands.MissingAnyRole):
        message = "You do not have the required role to execute this command.\n" \
                  "Required roles are:\n"
        for role in error.missing_roles:
            message += "`" + role + "`\n"
    elif isinstance(error, commands.MissingRequiredArgument):
        message = "You are missing required arguments for this command:\n`" + error.param + "`"

    await ctx.channel.send(content=message)


@bot.event
async def on_ready():
    print('Logged in')

bot.run(TOKEN, bot=True, reconnect=True)
