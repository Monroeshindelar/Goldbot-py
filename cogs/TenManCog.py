import discord
from discord.ext import commands
from _global.Config import Config
from utilities.Misc import read_or_create_file_pkl, save_to_file_pkl
from utilities.DiscordServices import get_discord_role_by_name, get_discord_channel_by_name
from utilities.Misc import read_config

MASTER_ROLE = Config.get_config_property("tenman_master_role_name")
MASTER_VOICE_CHANNEL = Config.get_config_property("tenman_master_voice_channel_name")
CAP_A_ROLE = Config.get_config_property("tenman_captian_A_role_name")
CAP_B_ROLE = Config.get_config_property("tenman_captian_B_role_name")
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

ROLES = {}
CHANNELS = {}


class TenManCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sl_init")
    async def init_tenman(self, ctx, *args):
        if ctx.message.mentions < 10:
            # error
            return
        maps = Config.get_config_property("tenman_default_map_pool")
        maps = maps.split(",")
        map_thumbnails = read_config("bin/resources/map_thumbnails.txt")
        remaining_maps = ""
        for stage in maps:
            MAPS_REMAINING.update({
                "name": stage,
                "thumbnail": map_thumbnails[stage]
            })
            remaining_maps += stage + "\n"
        remaining_players = ""
        for mention in ctx.message.mentions:
            PARTICIPANTS.update({
                "name": mention.name,
                "picked": False
            })
            remaining_players += mention.name + "\n"
        remaining_maps_message = await ctx.channel.send(
            content="```Remaining Maps:\n" + remaining_maps + "```"
        )
        REMAINING_MAPS_MESSAGE_ID = remaining_maps_message
        remaining_players_message = await ctx.channel.send(
            content="```Remaining Players:\n" + remaining_players + "```"
        )
        role_names = [MASTER_ROLE, CAP_A_ROLE, CAP_B_ROLE, TEAM_A_ROLE, TEAM_B_ROLE]
        for role in role_names:
            ROLES.update({
                "name": role,
                "role": get_discord_role_by_name(role, ctx.channel)
            })
        channel_names = [MASTER_VOICE_CHANNEL, TEAM_A_CHANNEL_NAME, TEAM_B_CHANNEL_NAME]
        for channel in channel_names:
            CHANNELS.update({
                "name": channel,
                "channel": get_discord_channel_by_name(channel, ctx.message.guild)
            })

        REMAINING_PLAYERS_MESSAGE_ID = remaining_players_message.id
        IS_TEAM_A_TURN = True
        IS_BAN_PHASE = True


def setup(bot):
    bot.add_cog(TenManCog(bot))