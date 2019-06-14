from discord.ext import commands
import Cogs.Helper.Challonge.TournamentCommands


class TournamentCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create_tournament")
    async def create_tournament_d(self, ctx):
       Cogs.Helper.Challonge.TournamentCommands.create_tournament("pytest_linux")


def setup(bot):
    bot.add_cog(TournamentCog(bot))
