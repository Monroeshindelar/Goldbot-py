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
MESSAGES = {}
ROLES = {}
CHANNELS = {}
FLAGS = {}


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
        MESSAGES.update({
            "REMAINING_MAPS_MESSAGE_ID": remaining_maps_message.id
        })

        remaining_players_message = await ctx.channel.send(
            content="```Remaining Players:\n" + remaining_players + "```"
        )
        MESSAGES.update({
            "REMAINING_PLAYERS_MESSAGE_ID": remaining_players_message.id
        })

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
        MESSAGES.update({
            "TEAM_A_PLAYERS_MESSAGE_ID": team_A_players_message.id
        })

        team_B_players_message = await ctx.channel.send(
            content="```Team B:```"
        )
        MESSAGES.update({
            "TEAM_B_PLAYERS_MESSAGE_ID": team_B_players_message.id
        })

        maps_to_play = await ctx.channel.send(
            content="```Maps Pick/Ban History:```"
        )
        MESSAGES.update({
            "MAPS_HISTORY_MESSAGE_ID": maps_to_play.id
        })

        FLAGS.update({
            "IS_TEAM_A_TURN": True,
            "IS_BAN_PHASE": True
        })

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
                    if participant == captains[0].id or participant == captains[1].id:
                        PARTICIPANTS[participant]["picked"] = True
        # assign captain roles to captain
        await captains[0].add_roles(captain_A_Role)
        await captains[1].add_roles(captain_B_Role)

        # build and send embed for the captains
        capAEmbed = build_embed(title="Team A Captain", thumbnail=captains[0].avatar_url,
                                description=captains[0].name + " has been picked to be the captain of Team A",
                                color=discord.Color.red())

        capBEmbed = build_embed(title="Team B Captain", thumbnail=captains[1].avatar_url,
                                description=captains[1].name + " has been picked to be the captain of Team B",
                                color=discord.Color.blue())
        embeds = [capAEmbed, capBEmbed]
        for embed in embeds:
            await ctx.channel.send(embed=embed)

        # update all the messages
        message = await ctx.channel.fetch_message(MESSAGES["REMAINING_PLAYERS_MESSAGE_ID"])
        new_content = "```Remaining Players:\n" + TenManCog.__get_remaining_participants(ctx) + "```"
        await message.edit(content=new_content)

        message = await ctx.channel.fetch_message(MESSAGES["TEAM_A_PLAYERS_MESSAGE_ID"])
        new_content = "```Team " + captains[0].name + ":\n" + captains[0].name + "```"
        await message.edit(content=new_content)

        message = await ctx.channel.fetch_message(MESSAGES["TEAM_B_PLAYERS_MESSAGE_ID"])
        new_content = "```Team " + captains[1].name + ":\n" + captains[1].name + "```"
        await message.edit(content=new_content)

        await captains[0].move_to(CHANNELS[TEAM_A_CHANNEL_NAME])
        await captains[1].move_to(CHANNELS[TEAM_B_CHANNEL_NAME])

    @commands.command(name="tm_pick_player")
    async def pick_player(self, ctx):
        # set permissions to captains
        caller_team = TenManCog.__get_caller_team(ctx)
        if not TenManCog.__caller_turn_to_call(caller_team):
            await ctx.channel.send(content="It is the other captains turn to pick a player.")
            return

        potential_pick = None
        # get team role to assign
        team_role = ROLES[TEAM_A_ROLE] if caller_team == "A" else ROLES[TEAM_B_ROLE]

        if len(ctx.message.mentions) > 0:
            potential_pick = ctx.message.mentions[0]

        message = None
        embed = None

        if potential_pick is not None and not PARTICIPANTS[potential_pick.id]["picked"]:
            PARTICIPANTS[potential_pick.id]["picked"] = True
            await potential_pick.add_roles(team_role)
            title = "Team " + caller_team + " picked: "
            color = discord.Color.red()
            embed = build_embed(title=title, thumbnail=potential_pick.avatar_url, description=potential_pick.name,
                                color=color)
            FLAGS["IS_TEAM_A_TURN"] = not FLAGS["IS_TEAM_A_TURN"]
            to_edit = ctx.channel.fetch_message(MESSAGES["REMAINING_PLAYERS_MESSAGE_ID"])
            await to_edit.edit(content="```Remaining Players:\n" + TenManCog.__get_remaining_participants() + "```")
        elif potential_pick is None or PARTICIPANTS[potential_pick.id] is None:
            message = "That user either doesnt exist or is not participating in the ten man."
        elif PARTICIPANTS[potential_pick.id]["picked"]:
            message = potential_pick.name + " has already been picked."

        await ctx.message.send(content=message, embed=embed)

        channel = CHANNELS[TEAM_A_CHANNEL_NAME] if caller_team == "A" else CHANNELS[TEAM_B_CHANNEL_NAME]
        await potential_pick.move_to(channel)

    @commands.command(name="tm_pick_map")
    async def pick_map(self, ctx, *args):
        if len(args) < 1:
            # error message
            return

        # if not all players picked, error message to discord

        if FLAGS["IS_BAN_PHASE"]:
            ctx.channel.send(content="Its not currently time to pick a map.")
            return

        caller_team = TenManCog.__get_caller_team(ctx)

        success = TenManCog.__select_map(args[0])
        if success:
            title = "Team " + ctx.message.author.name + " picked: "
            map_name = args[0].lower().capitalize()
            embed = build_embed(title=title, thumbnail=MAPS_REMAINING[map_name]["thumbnail"], description=map_name,
                                color=discord.Color.green())
            if caller_team == "B":
                FLAGS["IS_BAN_PHASE"] = not FLAGS["IS_BAN_PHASE"]

            # send embed
            await ctx.channel.send(embed=embed)
            # update message
            message = await ctx.channel.fetch_message(MESSAGES["REMAINING_MAPS_MESSAGE_ID"])
            await message.edit(content="```Remaining Maps:\n" + TenManCog.__get_remaining_maps() + "```")

            message = await ctx.channel.fetch_message(MESSAGES["MAPS_HISTORY_MESSAGE_ID"])
            content = message.content
            content = content[3:len(content)-3]
            content += "```" + content + "\n" + map_name + " - picked by " + ctx.message.author.name + "\n```"
            await message.edit(content=content)

    @commands.command(name="tm_ban_map")
    async def ban_map(self, ctx, *args):
        if len(args) < 1:
            # error message
            return

        # if not all players picked, error message to discord

        if not FLAGS["IS_BAN_PHASE"]:
            ctx.channel.send(content="Its not currently time to ban a map.")
            return

        caller_team = TenManCog.__get_caller_team(ctx)

        success = TenManCog.__select_map(args[0])
        if success:
            title = "Team " + ctx.message.author.name + " banned: "
            map_name = args[0].lower().capitalize()
            embed = build_embed(title=title, thumbnail=MAPS_REMAINING[map_name]["thumbnail"], description=map_name,
                                color=discord.Color.red())
            if caller_team == "B":
                FLAGS["IS_BAN_PHASE"] = not FLAGS["IS_BAN_PHASE"]

            # send embed
            await ctx.channel.send(embed=embed)
            # update message
            message = await ctx.channel.fetch_message(MESSAGES["REMAINING_MAPS_MESSAGE_ID"])
            await message.edit(content="```Remaining Maps:\n" + TenManCog.__get_remaining_maps() + "```")

            message = await ctx.channel.fetch_message(MESSAGES["MAPS_HISTORY_MESSAGE_ID"])
            content = message.content
            content = content[3:len(content)-3]
            content += "```" + content + "\n" + map_name + " - banned by " + ctx.message.author.name + "\n```"
            await message.edit(content=content)

    @commands.command(name="tm_free")
    async def tm_free(self, ctx):
        await ctx.channel.send(content="Beginning deconstruction.")
        for participant in PARTICIPANTS:
            discord_user = get_discord_user_by_id(participant, ctx.channel)
            await discord_user.remove_roles(ROLES[CAP_A_ROLE], ROLES[CAP_B_ROLE], ROLES[TEAM_A_ROLE], ROLES[TEAM_B_ROLE])

        await ctx.channel.send(content="Players freed.")

    @staticmethod
    def __select_map(map_name):
        for map in MAPS_REMAINING:
            if (map.lower() == map_name.lower()) and not MAPS_REMAINING[map]["selected"]:
                MAPS_REMAINING[map]["selected"] = True
                return True
        return False

    @staticmethod
    def __get_caller_team(ctx):
        caller = ctx.message.author
        caller_team = None
        for role in caller.roles:
            if role.name == CAP_A_ROLE:
                caller_team = "A"
                break
            elif role.name == CAP_B_ROLE:
                caller_team = "B"
                break
        return caller_team

    @staticmethod
    def __caller_turn_to_call(caller_team):
        if (FLAGS["IS_TEAM_A_TURN"] and caller_team == "B") or (not FLAGS["IS_TEAM_A_TURN"] and caller_team == "A"):
            return False
        else:
            return True

    @staticmethod
    def __get_remaining_participants(ctx):
        remaining_participants = ""
        for participant in PARTICIPANTS:
            if not PARTICIPANTS[participant]["picked"]:
                remaining_participants += get_discord_user_by_id(participant, ctx.channel).name + "\n"
        return remaining_participants

    @staticmethod
    def __get_remaining_maps():
        remaining_maps = ""
        for map_name in MAPS_REMAINING:
            if not MAPS_REMAINING[map_name]["selected"]:
                remaining_maps += map_name + "\n"
        return remaining_maps


def setup(bot):
    bot.add_cog(TenManCog(bot))
