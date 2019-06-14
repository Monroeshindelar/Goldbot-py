from discord.ext import commands
import Cogs.Helper.Challonge.tournament_commands


class TournamentCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create_tournament")
    async def create_tournament_d(self, ctx, *args):
        tournament_name = args[0]
        Cogs.Helper.Challonge.tournament_commands.create_tournament(tournament_name=tournament_name)

    @commands.command(name="destroy_tournament")
    async def destroy_tournament_d(self, ctx, *args):
        tournament_name = args[0]
        Cogs.Helper.Challonge.tournament_commands.destroy_tournament(tournament_name=tournament_name)


def setup(bot):
    bot.add_cog(TournamentCog(bot))
