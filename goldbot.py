import discord
import utilities
from discord.ext import commands

BOT_PREFIX = "!"
TOKEN = utilities.read_token("bin/token.txt")

cogs = [
    'Cogs.tournament_cog'
]

bot = commands.Bot(command_prefix=BOT_PREFIX)

if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)


@bot.event
async def on_ready():
    print('Logged in')


bot.run(TOKEN, bot=True, reconnect=True)
