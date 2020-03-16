import logging
from discord.ext import commands
from cogs.helper.challonge import TournamentCommands

LOGGER = logging.getLogger("goldlog")


class TournamentCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Initialized tournament commands cog.")

    @commands.command(name="create_tournament")
    async def create_tournament(self, ctx, *args):
        extra_params = None
        if len(args) < 1:
            LOGGER.warning("TournamentCommand::create_tournament - Failed call by " + ctx.message.author.name
                           + " due to insufficient number arguments.")
            await ctx.channel.send(
                content="```Usage: \n!create_tournament tournament_name [tournament[param]=value]"
                        "\n\ntournament_name: name of tournament to create (no spaces)"
                        "\n[tournament[param]=value]: Optional tournament settings"
                        "You can find more information about these parameters here"
                        "\nhttps://api.challonge.com/v1/documents/tournaments/create```"
            )
            return
        elif len(args) > 1:
            extra_params = ctx.args[1:]

        TournamentCommands.create_tournament(tournament_name=args[0], extra_params=extra_params)

    @commands.command(name="destroy_tournament",
                      aliases=["delete_tournament"])
    async def destroy_tournament_d(self, ctx, *args):
        if len(args) < 1:
            await ctx.channel.send(
                content="```Usage: \n!destroy_tournament tournament_name"
                        "\n\ntournament_name: name of tournament to destroy```"
            )
            LOGGER.warning("TournamentCommands::destroy_tournament - Failed call by " + ctx.message.author.name +
                           " due to insufficient number of arguments.")
            return
        TournamentCommands.destroy_tournament(tournament_name=args[0])

    @commands.command(name="start_tournament")
    async def start_tournament(self, ctx, *args):
        if len(args) < 1:
            await ctx.channel.send(
                content="```Usage: \n!start_tournament tournament_name"
                        "\n\ntournament_name: name of tournament to start```"
            )
            LOGGER.warning("TournamentCommand::start_tournament - Failed call by " + ctx.message.author.name +
                           " due to insufficient number of arguments")
            return
        TournamentCommands.start_tournament(tournament_name=args[0])

    @commands.command(name="finalize_tournament",
                      aliases=["end_tournament"])
    async def finalize_tournament(self, ctx, *args):
        if len(args) < 1:
            await ctx.channel.send(
                content="```Usage: \n!finalize_tournament tournament_name"
                        "\n\ntournament_name: name of tournament to finalize```"
            )
            LOGGER.warning("TournamentCommand::finalize_tournament - Failed call by " + ctx.message.author.name +
                           " due to insufficient number of arguments")
            return
        TournamentCommands.finalize_tournament(tournament_name=args[0])

    @commands.command(name="add_users",
                      aliases=["add_user", "add_participants", "add_participant"])
    async def add_user_to_tournament(self, ctx, *args):
        if len(args) < 1 or len(ctx.message.mentions) < 1:
            await ctx.channel.send(
                content="```Usage: \n!add_partipants tournament_name @user [@user2...]"
                        "\n\ntournament_name: tournament to add participants to"
                        "\n@user: Mentioned user to add to the tournament"
                        "\n[@user2...]: Optional other users to add to the tournament```"
            )
            LOGGER.warning("TournamentCommand::add_user - Failed call by " + ctx.message.author.name +
                           " due to insufficient number of arguments")
            return
        users = []
        for user in ctx.message.mentions:
            users.append(user.name)
        TournamentCommands.add_users(tournament_name=args[0], users=users)

    @commands.command(name="destroy_participant",
                      aliases=["delete_participant"])
    async def destroy_participant(self, ctx, *args):
        if len(args) < 2:
            await ctx.channel.send(
                content="```Usage: \n!destroy_participant tournament_name participant_name"
                        "\n\ntournament_name: name of tournament the participant is in"
                        "\nparticipant_name: name of participant to destroy```"
            )
            LOGGER.warning("TournamentCommand::destroy_participant - Failed call by " + ctx.message.author.name +
                           " due to insufficient number of arguments")
            return
        TournamentCommands.destroy_participant(tournament_name=args[0], participant_name=args[1])

    @commands.command(name="update_match")
    async def update_match(self, ctx, *args):
        if len(args) < 5:
            await ctx.channel.send(
                content="```Usage: \n!update_match tournament_name participant1_name participant2_name "
                        "participant1_score participant2_score"
                        "\n\ntournament_name: name of the tournament where the match exists"
                        "\nparticipant1_name: name of the first participant in the match"
                        "\nparticipant2_name: name of the second participant in the match"
                        "\nparticipant1_score: final score of the first participant"
                        "\nparticipant2_score: final score of the second participant```"
            )
            LOGGER.warning("TournamentCommand::update_match - Failed call by " + ctx.message.author.name +
                           " due to insufficient number of arguments")
            return
        TournamentCommands.update_match(tournament_name=args[0], participant1_name=args[1], participant2_name=args[2],
                                        participant1_score=args[3], participant2_score=args[4])


def setup(bot):
    bot.add_cog(TournamentCog(bot))
