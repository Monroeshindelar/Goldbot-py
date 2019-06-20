# TODO: Proper logging


from discord.ext import commands
from _global.Config import Config

TOKEN = Config.get_config_property(config_property="discord_api_key")
BOT_PREFIX = "!"


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
