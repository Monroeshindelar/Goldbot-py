import discord
import logging
from discord.ext import commands
from discord.ext.commands import UserConverter
from cogs.helper.challonge import TournamentCommands
from _global.Config import Config
from utilities.Misc import read_or_create_file_pkl, save_to_file_pkl
from core.squadlocke.SquadlockeConstants import ENCOUNTER_AREA_DICT, WEATHER_DICT
from _global.ArgParsers.SquadlockeArgParsers import SquadlockeArgParsers
from utilities.DiscordServices import build_embed
from core.squadlocke.RouteEncounter import RouteEncounter

LOGGER = logging.getLogger("goldlog")

SQUADLOCKE_DATA_FILE_PATH = Config.get_config_property("save_file_directory") + "sldata.pkl"
SQUADLOCKE_ROLE = Config.get_config_property("squadlocke_guild_role")
SQUADLOCKE_NAME = Config.get_config_property("squadlocke_default_checkpoint_name")
SL_SERIALIZE = read_or_create_file_pkl(SQUADLOCKE_DATA_FILE_PATH)
PARTICIPANTS = {} if len(SL_SERIALIZE) < 1 else SL_SERIALIZE[0]
CHECKPOINT = 1 if len(SL_SERIALIZE) < 2 else SL_SERIALIZE[1]

save_to_file_pkl([PARTICIPANTS, CHECKPOINT], SQUADLOCKE_DATA_FILE_PATH)


class SquadlockeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Initialized squadlocke command cog.")

    @commands.command(name="sl_init",)
    async def squadlocke_init(self, ctx, *args):
        if len(PARTICIPANTS) > 0:
            await ctx.channel.send(
                content="A squadlocke has already been started. \n"
                        "Please conclude it before starting a new one."
            )
            LOGGER.warning("SquadlockeCommand::squadlocke_init - call failed because one is already initialized.")
            return
        squadlocke_role = None
        LOGGER.info("SquadlockeCommand::squadlocke_init - Getting role.")
        for role in ctx.message.guild.roles:
            if role.name == SQUADLOCKE_ROLE:
                squadlocke_role = role
                break

        if len(ctx.message.mentions) > 0:
            LOGGER.info("SquadlockeCommand::squadlocke_init - Assigning roles to members")
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
            participant = await UserConverter().convert(ctx=ctx, argument=str(participant))
            players.append(participant.name)

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
            LOGGER.warning("SquadlockeCommand::sl_update_match - Failed due to insufficient number of arguments.")
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
        LOGGER.info("SquadlockeCommand::sl_get_ready_list - called successfully by " + ctx.message.author.name)
        for participant in PARTICIPANTS:
            user = await UserConverter().convert(ctx=ctx, argument=str(participant))
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
                participant_id=match["match"]["player2_id"]
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
        LOGGER.info("SquadlockeCommand::save_squadlocke - Saving current squadlocke state.")
        squadlocke_object = [PARTICIPANTS, CHECKPOINT]
        save_to_file_pkl(squadlocke_object, SQUADLOCKE_DATA_FILE_PATH)

    @staticmethod
    def get_squadlocke_tournament_name():
        return SQUADLOCKE_NAME + "_" + str(CHECKPOINT)

    @commands.command(name="slencounter")
    async def t(self, ctx, *args):
        a, ua = SquadlockeArgParsers.SLENCOUNTER_ARG_PARSER.parse_known_args(args)
        re = RouteEncounter(ua[0])
        if a.get_info:
            encounter_info = re.get_info()
            i = 0
            for section in encounter_info:
                for weather in encounter_info[section]:
                    message = "```Section: " + section + " (id: " + str(i) + ")\n" + "Weather: " + weather + " (id: " \
                              + str(WEATHER_DICT[weather]) + ")\n\n" + encounter_info[section][weather] + "```"
                    await ctx.channel.send(message)
                i = i + 1
            return
        if not a.all:
            re.add_area_filter([2, 3, 6, 7], -1)
        if a.f:
            re.add_area_filter([2], False)
        if a.w is not None:
            re.add_weather_filter(a.w.split(","), 0)
        if a.s is not None:
            re.add_section_filter(a.s.split(","), 0)
        if a.a is not None:
            re.add_area_filter(a.a.split(","), 0)

        enc = re.get_encounter()
        if enc is None:
            await ctx.channel.send("There are no encounters available on this route with the specified filters.")
            return
        v1, v2 = enc.get()

        generic_embed_descr = 'Encounter rate: ' + str(v1.get('rate')) + '%\n Normalized encounter rate: ' + \
                              str(v1.get('n_rate')) + '%\n Area: ' + ENCOUNTER_AREA_DICT.inverse[v1.get('area')][0] \
                              + "\n Section: " + v1.get('section')

        if v1.get('weather') != 'None':
            generic_embed_descr += '\n Weather: ' + v1.get('weather')

        embed_color = discord.Color.purple()
        v2embed = None

        if v2 is not None:
            v2_embed_descr = "Exclusive to Pokémon Shield!\n" + generic_embed_descr
            generic_embed_descr = "Exclusive to Pokémon Sword!\n" + generic_embed_descr
            v2embed = build_embed(title=v2.get('name'), thumbnail='https://serebii.net' + v2.get('sprite'),
                                  description=v2_embed_descr, color=discord.Color.red())
            embed_color = discord.Color.blue()

        v1embed = build_embed(title=v1.get('name'), thumbnail='https://serebii.net' + v1.get('sprite'),
                              description=generic_embed_descr, color=embed_color)

        await ctx.channel.send(embed=v1embed)

        if v2embed is not None:
            await ctx.channel.send(embed=v2embed)


def setup(bot):
    bot.add_cog(SquadlockeCog(bot))



