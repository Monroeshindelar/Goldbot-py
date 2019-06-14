from discord.ext import commands
import Cogs.Helper.Challonge.tournament_commands


class TournamentCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create_tournament")
    async def create_tournament_d(self, ctx):
       Cogs.Helper.Challonge.tournament_commands.create_tournament("pytest_linux")

    @commands.command(name="destroy_tournament")
    async def destroy_tournament_d(self, ctx):
        Cogs.Helper.Challonge.tournament_commands.destroy_tournament("pytest_linux")


def setup(bot):
    bot.add_cog(TournamentCog(bot))
