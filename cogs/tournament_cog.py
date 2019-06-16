from discord.ext import commands
from cogs.helper.challonge import tournament_commands


class TournamentCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create_tournament")
    async def create_tournament_d(self, ctx, *args):
        tournament_commands.create_tournament(tournament_name=args[0], extraParams=args[1:])

    @commands.command(name="destroy_tournament",
                      aliases=["delete_tournament"])
    async def destroy_tournament_d(self, ctx, *args):
        tournament_commands.destroy_tournament(tournament_name=args[0])

    @commands.command(name="start_tournament")
    async def start_tournament(self, ctx, *args):
        tournament_commands.start_tournament(tournament_name=args[0])

    @commands.command(name="finalize_tournament",
                      aliases=["end_tournament"])
    async def finalize_tournament(self, ctx, *args):
        tournament_commands.finalize_tournament(tournament_name=args[0])

    @commands.command(name="add_users",
                      aliases=["add_user", "add_participants", "add_participant"])
    async def add_user_to_tournament(self, ctx, *args):
        tournament_commands.add_users(tournament_name=args[0], users=ctx.message.mentions)

    @commands.command(name="destroy_participant",
                      aliases=["delete_participant"])
    async def destroy_participant(self, ctx, *args):
        tournament_commands.destroy_participant(tournament_name=args[0], participant_name=args[1])

    @commands.command(name="update_match")
    async def update_match(self, ctx, *args):
        tournament_commands.update_match(tournament_name=args[0], participant1_name=args[1], participant2_name=args[2],
                                         participant1_score=args[3], participant2_score=args[4])


def setup(bot):
    bot.add_cog(TournamentCog(bot))
