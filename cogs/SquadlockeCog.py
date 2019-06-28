import discord
from discord.ext import commands
from cogs.helper.challonge import TournamentCommands
from _global.Config import Config
from utilities.Misc import read_or_create_file_pkl, save_to_file_pkl
from utilities.DiscordServices import get_discord_user_by_id

SQUADLOCKE_DATA_FILE_PATH = Config.get_config_property("squadlocke_data_file")
SQUADLOCKE_ROLE = Config.get_config_property("squadlocke_guild_role")
SQUADLOCKE_NAME = Config.get_config_property("squadlocke_default_checkpoint_name")
SL_SERIALIZE = read_or_create_file_pkl(SQUADLOCKE_DATA_FILE_PATH)
PARTICIPANTS = {} if len(SL_SERIALIZE) < 1 else SL_SERIALIZE[0]
CHECKPOINT = 1 if len(SL_SERIALIZE) < 2 else SL_SERIALIZE[1]


class SquadlockeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sl_init",)
    async def squadlocke_init(self, ctx, *args):
        if len(PARTICIPANTS) > 0:
            await ctx.channel.send(
                content="A squadlocke has already been started. \n"
                        "Please conclude it before starting a new one."
            )
            return
        squadlocke_role = None
        for role in ctx.message.guild.roles:
            if role.name == SQUADLOCKE_ROLE:
                squadlocke_role = role
                break

        if len(ctx.message.mentions) > 0:
            for mention in ctx.message.mentions:
                mention.add_roles(roles=squadlocke_role)

        members = ctx.channel.members
        for member in members:
            if squadlocke_role in member.roles:
                PARTICIPANTS.update({
                    member.id: False
                })
        await SquadlockeCog.__save_squadlocke()
        extra_params = None if len(args) > 1 else args[1:]
        TournamentCommands.create_tournament(
            tournament_name=SquadlockeCog.get_squadlocke_tournament_name(),
            extra_params=extra_params
        )

        players = []
        for participant in PARTICIPANTS:
            players.append(get_discord_user_by_id(participant, ctx.channel).name)

        TournamentCommands.add_users(SQUADLOCKE_NAME + "_" + str(CHECKPOINT), players)

        await ctx.channel.send(
            content="Squadlocke has been started.\n"
                    "Here is a link to the first tournament:\n" +
                    TournamentCommands.get_tournament_url(SquadlockeCog.get_squadlocke_tournament_name())
        )

    @commands.command(name="sl_ready_up")
    async def squadlocke_ready_up(self, ctx):
        message = "Looks like there was a problem with readying you up\n" \
                  "Make sure you're a participant in the squadlocke before using this command"
        if ctx.message.author.id in PARTICIPANTS:
            PARTICIPANTS[ctx.message.author.id] = True
            message = "You have been readied up!"
            await SquadlockeCog.__save_squadlocke()
        await ctx.channel.send(
            content=message
        )
        start = True
        for participant in PARTICIPANTS:
            if not PARTICIPANTS[participant]:
                start = False
                break
        if start:
            TournamentCommands.start_tournament(SQUADLOCKE_NAME + str(CHECKPOINT))
            await ctx.channel.send(
                content="Everyone is ready. Starting the tournament.\n"
                        "View the bracket here:\n" +
                        TournamentCommands.get_tournament_url(
                            tournament_name=SquadlockeCog.get_squadlocke_tournament_name()
                        )
            )

    @commands.command(name="sl_update_match")
    async def squadlocke_update_match(self, ctx, *args):
        if len(args) < 4:
            await ctx.channel.send(
                content="```Usage: \n!sl_update_match participant1_name participant2_name "
                        "participant1_score participant2_score"
                        "\n\nparticipant1_name: name of the first participant in the match"
                        "\nparticipant2_name: name of the second participant in the match"
                        "\nparticipant1_score: final score of the first participant"
                        "\nparticipant2_score: final score of the second participant```"
            )
            return
        TournamentCommands.update_match(
            tournament_name=SquadlockeCog.get_squadlocke_tournament_name(),
            participant1_name=args[0],
            participant2_name=args[1],
            participant1_score=args[2],
            participant2_score=args[3]
        )
        matches = TournamentCommands.index_matches(
            tournament_name=SquadlockeCog.get_squadlocke_tournament_name()
        )

        # TODO: report to discord

        finish = True
        for match in matches:
            if match["match"]["state"] == "open":
                finish = False
                break

        if finish:
            TournamentCommands.finalize_tournament(
                tournament_name=SquadlockeCog.get_squadlocke_tournament_name()
            )
        # TODO: report to discord

    @commands.command(name="sl_get_ready_list")
    async def squadlocke_get_ready_list(self, ctx):
        for participant in PARTICIPANTS:
            user = get_discord_user_by_id(participant, ctx.channel)
            embed = discord.Embed(
                title=user.name,
                thumbnail=user.avatar,
                description="Ready" if PARTICIPANTS[participant] else "Not ready",
                color=discord.Color.green() if PARTICIPANTS[participant] else discord.Color.red()
            )
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.channel.send(
                embed=embed
            )

    @commands.command(name="get_current_matches")
    async def get_matches_squadlocke(self, ctx):
        open_matches = TournamentCommands.index_matches(
            tournament_name=SquadlockeCog.get_squadlocke_tournament_name(),
            state="open"
        )
        for match in open_matches:
            participant1 = TournamentCommands.get_participant_json_by_id(
                tournament_name=SquadlockeCog.get_squadlocke_tournament_name(),
                participant_id=match["match"]["player1_id"]
            )
            participant2 = TournamentCommands.get_participant_json_by_id(
                tournament_name=SquadlockeCog.get_squadlocke_tournament_name(),
                participant1=match["match"]["player2_id"]
            )

            embed = discord.Embed(
                title="Upcoming Match",
                description=participant1["name"] + " vs. " + participant2["name"],
                color=discord.Color.green()
            )
            await ctx.channel.send(
                embed=embed
            )


    @staticmethod
    async def __save_squadlocke():
        squadlocke_object = [PARTICIPANTS, CHECKPOINT]
        save_to_file_pkl(squadlocke_object, SQUADLOCKE_DATA_FILE_PATH)

    @staticmethod
    def get_squadlocke_tournament_name():
        return SQUADLOCKE_NAME + "_" + str(CHECKPOINT)


def setup(bot):
    bot.add_cog(SquadlockeCog(bot))



