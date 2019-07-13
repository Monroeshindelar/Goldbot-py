import discord
import random
from discord.ext import commands
from _global.Config import Config
from utilities.Misc import read_or_create_file_pkl, save_to_file_pkl
from utilities.DiscordServices import get_discord_role_by_name, get_discord_channel_by_name, \
    get_discord_user_by_id, build_embed
from utilities.Misc import read_config

MASTER_ROLE = Config.get_config_property("tenman_master_role_name")
MASTER_VOICE_CHANNEL = Config.get_config_property("tenman_master_voice_channel_name")
CAP_A_ROLE = Config.get_config_property("tenman_captain_A_role_name")
CAP_B_ROLE = Config.get_config_property("tenman_captain_B_role_name")
TEAM_A_ROLE = Config.get_config_property("tenman_team_A_role_name")
TEAM_B_ROLE = Config.get_config_property("tenman_team_B_role_name")
TEAM_A_CHANNEL_NAME = Config.get_config_property("tenman_team_A_voice_channel_name")
TEAM_B_CHANNEL_NAME = Config.get_config_property("tenman_team_B_voice_channel_name")

PARTICIPANTS = {}
MAPS_REMAINING = {}

IS_TEAM_A_TURN = None
IS_BAN_PHASE = None

REMAINING_MAPS_MESSAGE_ID = None
REMAINING_PLAYERS_MESSAGE_ID = None
TEAM_A_PLAYERS_MESSAGE_ID = None
TEAM_B_PLAYERS_MESSAGE_ID = None
MATCH_MAPS_MESSAGE_ID = None

ROLES = {}
CHANNELS = {}


class TenManCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tm_init")
    async def init_tenman(self, ctx):
        # if ctx.message.mentions < 10:
            # error
        #    return
        maps = Config.get_config_property("tenman_default_map_pool")
        maps = maps.split(",")
        map_thumbnails = read_config("bin/resources/map_thumbnails.txt", " ")

        remaining_maps = ""
        for stage in maps:
            MAPS_REMAINING.update({
                stage: {
                    "thumbnail": map_thumbnails[stage],
                    "selected": False
                }
            })
            remaining_maps += stage + "\n"

        remaining_players = ""
        for mention in ctx.message.mentions:
            PARTICIPANTS.update({
                mention.id: {
                  "picked": False
                }
            })
            remaining_players += mention.name + "\n"

        remaining_maps_message = await ctx.channel.send(
            content="```Remaining Maps:\n" + remaining_maps + "```"
        )
        REMAINING_MAPS_MESSAGE_ID = remaining_maps_message.id

        remaining_players_message = await ctx.channel.send(
            content="```Remaining Players:\n" + remaining_players + "```"
        )
        REMAINING_PLAYERS_MESSAGE_ID = remaining_players_message.id

        role_names = [MASTER_ROLE, CAP_A_ROLE, CAP_B_ROLE, TEAM_A_ROLE, TEAM_B_ROLE]
        for role in role_names:
            ROLES.update({
                role: get_discord_role_by_name(role, ctx.guild)
            })

        channel_names = [MASTER_VOICE_CHANNEL, TEAM_A_CHANNEL_NAME, TEAM_B_CHANNEL_NAME]
        for channel in channel_names:
            CHANNELS.update({
                channel: get_discord_channel_by_name(channel, ctx.message.guild)
            })

        team_A_players_message = await ctx.channel.send(
             content="```Team A:```"
        )
        TEAM_A_PLAYERS_MESSAGE_ID = team_A_players_message.id

        team_B_players_message = await ctx.channel.send(
            content="```Team B:```"
        )
        TEAM_B_PLAYERS_MESSAGE_ID = team_B_players_message.id

        maps_to_play = await ctx.channel.send(
            content="```Maps Pick/Ban History:```"
        )
        MATCH_MAPS_MESSAGE_ID = maps_to_play.id

        IS_TEAM_A_TURN = True
        IS_BAN_PHASE = True

    @commands.command(name="tm_pick_captains")
    async def pick_captains(self, ctx, *args):
        captains = []
        captain_A_Role = ROLES[CAP_A_ROLE]
        captain_B_Role = ROLES[CAP_B_ROLE]
        if len(args) == 0:
            for x in range(2):
                while True:
                    cap_index = random.randint(0, len(PARTICIPANTS) - 1)
                    potential_cap_id = list(PARTICIPANTS)[cap_index]
                    potential_cap = PARTICIPANTS[potential_cap_id]
                    if not potential_cap["picked"]:
                        potential_cap["picked"] = True
                        captain_id = potential_cap_id
                        captains.append(get_discord_user_by_id(captain_id, ctx.channel))
                        break
        else:
            if len(ctx.message.mentions) > 1:
                captains.append(ctx.message.mentions[0])
                captains.append(ctx.message.mentions[1])
                for participant in PARTICIPANTS:
                    if participant["id"] == captains[0]["id"] or participant.id == captains[1]["id"]:
                        participant["picked"] = True
        # assign captain roles to captain
        await captains[0].add_roles(captain_A_Role)
        await captains[1].add_roles(captain_B_Role)
        # update all the messages
        message = await ctx.channel.fetch_message(REMAINING_PLAYERS_MESSAGE_ID)
        new_content = "```Remaining Players:\n" + TenManCog.__get_remaining_participants() + "```"
        message.content = new_content

        message = await ctx.channel.fetch_message(TEAM_A_PLAYERS_MESSAGE_ID)
        new_content = "```Team " + captains[0].name + ":\n" + captains[0].name
        message.content = new_content

        message = await ctx.channel.fetch_message(TEAM_B_PLAYERS_MESSAGE_ID)
        new_content = "```Team " + captains[1].name + ":\n" + captains[1].name
        message.content = new_content
        # build and send embed for the captains
        capAEmbed = build_embed(title="Team A Captain", thumbnail=captains[0].avatar,
                                description=captains[0].name + " has been picked to be the captain of Team A",
                                color=discord.Color.red())

        capBEmbed = build_embed(title="Team B Captain", thumbnail=captains[0].avatar,
                                description=captains[1].name + " has been picked to be the captain of Team B",
                                color=discord.Color.blue())
        embeds = [capAEmbed, capBEmbed]
        for embed in embeds:
            await ctx.channel.send(
                embed=embed
            )

    @commands.command(name="tm_pick_player")
    async def pick_player(self, ctx):
        # if its a's turn and b tries to pick, fail
        potential_pick = None
        if len(ctx.message.mentions) > 0:
            potential_pick = ctx.message.mentions[0]

        for participant in PARTICIPANTS:
            if (participant["id"] == potential_pick.id) and not participant["picked"]:
                participant["picked"] = True
                # send the embed
                # update teams message

    @commands.command(name="tm_pick_map")
    async def pick_map(self, ctx, *args):
        if len(args) < 1:
            # error message
            return

        success = TenManCog.__select_map(args[0])
        # update message
        # send embed

    @commands.command(name="tm_ban_map")
    async def ban_map(self, ctx, *args):
        if len(args) < 1:
            # error message
            return
        success = TenManCog.__select_map(args[0])
        # update message
        # send embed

    @staticmethod
    def __select_map(map_name):
        for map in MAPS_REMAINING:
            if (map["name"].lower() == map_name.lower()) and not map["selected"]:
                map["selected"] = True
                return True
        return False

    @staticmethod
    def __get_remaining_participants():
        remaining_participants = ""
        for participant in PARTICIPANTS:
            if not participant["picked"]:
                remaining_participants += participant["name"] + "\n"
        return remaining_participants

    @staticmethod
    def __get_remaining_maps():
        remaining_maps = ""
        for map in MAPS_REMAINING:
            if not map["selected"]:
                remaining_maps += map["name"] + "\n"
        return remaining_maps


def setup(bot):
    bot.add_cog(TenManCog(bot))