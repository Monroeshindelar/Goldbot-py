import discord
import utilities
from discord.ext import commands

BOT_PREFIX = "!"
TOKEN = utilities.read_token("bin/token.txt")

cogs = [
    'Cogs.TournamentCog'
]

bot = commands.Bot(command_prefix=BOT_PREFIX)

if __name__ == '__main__':
    bot.load_extension('Cogs.TournamentCog')


@bot.event
async def on_ready():
    print('Logged in')


bot.run(TOKEN, bot=True, reconnect=True)
