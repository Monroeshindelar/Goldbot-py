import discord
from discord.ext import commands

def read_token():
    with open("bin/token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


BOT_PREFIX = "!"
TOKEN = read_token()

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
