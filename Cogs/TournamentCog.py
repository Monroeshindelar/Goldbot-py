import discord
from discord.ext import commands


class TournamentCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='test')
    async def test_command(self, ctx):
        await ctx.send('test123')


def setup(bot):
    bot.add_cog(TournamentCog(bot))

