from discord.ext import commands
from discord.utils import find
from _global.Config import Config
from core.TenMan import TenMan
from core.model.TenMan.Game import Game
from core.model.TenMan.TeamStatus import TeamStatus
from core.model.TenMan.Side import Side
from _global.ArgParsers.TenManArgParsers import TenManArgParsers
from _global.ArgParsers.ThrowingArgumentParser import ArgumentParserError
import yaml
import logging
import discord
from random import randint

LOGGER = logging.getLogger("goldlog")


class TenManCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # core.model.TenMan
        self.__ongoing = None
        # Message for displaying the current status of the tenman (teams, map picks, etc.)
        self.__status_message = None
        # Print help messages to help new users know which commands need to come next
        self.__display_help = False
        with open("bin/resources/tenman/resources.yml") as f:
            self.__resources = yaml.load(f, Loader=yaml.FullLoader)
        LOGGER.info("Initialized ten man command cog.")

    @commands.command(name="tm_init", aliases=["tm_start"])
    @commands.has_role(Config.get_config_property("tenman", "organizerRole"))
    async def init(self, ctx, *args):
        """
        Initializes ten man with users in the general channel.
        Requires 10 users in the general voice channel

        SYNOPSIS
            .tm_init [-h] game
        """
        # Check if there is already a game going on and if there is bail
        if self.__ongoing is not None:
            raise SyntaxError

        # Get the arguments from the command message. Game command is necessary (CSGO/Valorant)
        try:
            parsed_args = TenManArgParsers.TM_INIT_ARG_PARSER.parse_known_args(args)[0]
        except ArgumentParserError as e:
            raise commands.ArgumentParsingError(message=e.args[0])

        game = Game.get(parsed_args.game)

        self.__display_help = parsed_args.help

        # All players should be in a communal voice channel when this command is called. Get all 10 players in the
        # voice channel and creates a list of all their ids.
        general_voice = find(lambda v: v.name == Config.get_config_property("tenman", "generalVoice"),
                             ctx.guild.voice_channels)
        # member_list = [m.id for m in general_voice.members]
        member_list = [148297442452963329, 645696336469164107, 727670795081351188, 727672213871919215, 727672966539771934]
        # If there are more than 10 or less than 10 members there is going to be a problem
        # if len(member_list) is not 10:
        #     raise SyntaxError

        self.__ongoing = TenMan(member_list, game)

        # Pretty output for discord
        embed = discord.Embed(
            title=ctx.guild.name + " Ten Man",
            description="Ten Man initialization completed!",
            color=discord.Color.dark_grey()
        )
        if game == Game.CSGO:
            logo = self.__resources["csgoLogo"]
        elif game == Game.VALORANT:
            logo = self.__resources["valorantLogo"]

        embed.add_field(name="Game", value=game.name)
        embed.add_field(name="Type", value="Best of 3")
        embed.add_field(name="Player Pick Sequence", value=Config.get_config_property("tenman", "playerPickSequence"))
        embed.add_field(name="Available Participants", value="\n".join([find(lambda u: u.id == p, ctx.guild.members).name
                        for p in member_list]))
        embed.add_field(name="Available Map Pool", value="\n".join(self.__ongoing.get_remaining_maps()), inline=False)

        embed.set_image(url=logo)
        self.__status_message = await ctx.channel.send(embed=embed)

        if self.__display_help:
            message = "***Help Message:***\nTen man has been initialized. Now it's time to pick captains. You can do " \
                      "so by either calling\n`.pick_captains`\nor\n`.pick_captains @captainA @captainB`"
            await ctx.channel.send(message)

    @commands.command(name="tm_pick_captains", aliases=["pick_captains"])
    @commands.has_role(Config.get_config_property("tenman", "organizerRole"))
    async def pick_captains(self, ctx):
        # Caller tried to manually select too many captains
        if len(ctx.message.mentions) > 2:
            raise SyntaxError

        # Create role objects for config
        captain_a_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamA", "captainRole"), ctx.guild.roles)
        captain_b_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamB", "captainRole"), ctx.guild.roles)

        # Get captains either randomly or manually (based on # of mentioned users)
        captain_ids = ctx.message.raw_mentions
        captains = self.__ongoing.set_or_pick_captains(captain_ids)
        captain_a = find(lambda c: str(c.id) == str(captains[0]), ctx.guild.members)
        captain_b = find(lambda c: str(c.id) == str(captains[1]), ctx.guild.members)
        await captain_a.add_roles(captain_a_role)
        await captain_b.add_roles(captain_b_role)

        # Pretty output for discord
        embed_a = discord.Embed(
            title="Captain Selected",
            color=discord.Color.red()
        )
        embed_a.set_thumbnail(url=captain_a.avatar_url)
        embed_a.add_field(name="Name", value=captain_a.name)
        embed_a.add_field(name="Selection Type", value="Manual" if len(ctx.message.mentions) == 2 else "Random")
        embed_a.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")

        embed_b = discord.Embed(
            title="Captain Selected",
            color=discord.Color.blue()
        )
        embed_b.set_thumbnail(url=captain_b.avatar_url)
        embed_b.add_field(name="Name", value=captain_b.name)
        embed_b.add_field(name="Selection Type", value="Manual" if len(ctx.message.mentions) == 2 else "Random")
        embed_b.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")

        await ctx.channel.send(embed=embed_a)
        await ctx.channel.send(embed=embed_b)

        status_embed = self.__status_message.embeds[0]
        rp_field = status_embed.fields[3]
        status_embed.set_field_at(index=3, name=rp_field.name, value="\n".join([find(lambda u: u.id == rp, ctx.guild.members).name for rp in self.__ongoing.get_remaining_participant_ids()]))
        status_embed.insert_field_at(index=4, name="Team A", value=captain_a.name, inline=True)
        status_embed.insert_field_at(index=5, name="Team B", value=captain_b.name, inline=True)
        await self.__status_message.edit(embed=status_embed)

        if self.__display_help:
            message = "***Help Message***:\nNow that captains have been selected, it is time for the captain of Team" \
                      "A to pick a player. They can do so by using the command\n`.pick_player @mention`"
            await ctx.channel.send(message)

    @commands.command(name="tm_pick_player", aliases=["pick_player"])
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def pick_player(self, ctx):
        if len(ctx.message.raw_mentions) > 1:
            raise SyntaxError

        captain_id = ctx.message.author.id
        pick = ctx.message.mentions[0]
        captain_team_status = self.__ongoing.get_captain_team_status(captain_id)

        last_pick = self.__ongoing.pick_player(pick.id, captain_id)

        role_config_property = Config.get_config_property("tenman", "team" + captain_team_status.name, "playerRole")
        role = find(lambda r: r.name == role_config_property, ctx.guild.roles)

        await ctx.message.mentions[0].add_roles(role)

        embed = discord.Embed(
            title="Player Selected",
            color=discord.Color.red() if captain_team_status == TeamStatus.A else discord.Color.blue()
        )
        embed.add_field(name="Name", value=ctx.message.mentions[0].name)
        embed.add_field(name="Picked By", value="Team " + captain_team_status.name)
        embed.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")
        embed.set_thumbnail(url=pick.avatar_url)
        await ctx.channel.send(embed=embed)

        status_embed = self.__status_message.embeds[0]
        team_field = status_embed.fields[4 if captain_team_status == TeamStatus.A else 5]
        status_embed.set_field_at(index=(4 if captain_team_status == TeamStatus.A else 5), name=team_field.name,
                                  value=(team_field.value + "\n" + pick.name))

        if last_pick[0] is not None and last_pick[1] is not None:
            last_pick_profile = find(lambda p: p.id == last_pick[0], ctx.guild.members)
            role_config_property_lp = Config.get_config_property("tenman", "team" + last_pick[1].name, "playerRole")
            role_lp = find(lambda r: r.name == role_config_property_lp, ctx.guild.roles)

            await last_pick_profile.add_roles(role_lp)

            embed_lp = discord.Embed(
                title="Last Pick",
                color=discord.Color.red() if last_pick[1] == TeamStatus.A else discord.Color.blue()
            )
            embed_lp.set_thumbnail(url=last_pick_profile.avatar_url)
            embed_lp.add_field(name="Name", value=last_pick_profile.name)
            embed_lp.add_field(name="Picked for", value="Team " + last_pick[1].name)
            embed_lp.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")
            await ctx.channel.send(embed=embed_lp)
            status_embed.remove_field(index=3)
            status_embed.set_field_at(index=(3 if last_pick[0] == TeamStatus.A else 4), name=team_field.name,
                                      value=(team_field.value + "\n" + last_pick_profile.name))
            status_embed.set_field_at(index=5, name=status_embed.fields[5].name, value=status_embed.fields[5].value, inline=True)
        else:
            rp_field = status_embed.fields[3]
            status_embed.set_field_at(index=3, name=rp_field.name, value="\n".join(
                [find(lambda u: u.id == rp, ctx.guild.members).name for rp in self.__ongoing.get_remaining_participant_ids()]))
            status_embed.set_field_at(index=5, name=status_embed.fields[5].name, value=status_embed.fields[5].value,
                                      inline=True)
        await self.__status_message.edit(embed=status_embed)

        if self.__display_help:
            try:
                message = "***Help Message:***\nIt is Team " + self.__ongoing.peek_next_player_pick().name + "'s " \
                          "turn to pick the next player.\nThey can do so by using the command\n`.pick_player @player`"
            except IndexError:
                map_pick_ban_entry = self.__ongoing.peek_next_map_pick_ban()
                message = "***Help Message:***\nIt is now time to move on to the map pick/ban phase. Team " \
                          + map_pick_ban_entry.get_team_status().name + " can " + \
                          map_pick_ban_entry.get_mode().name.lower() + " the first map.\nThey can do so by using the " \
                          "command\n`." + map_pick_ban_entry.get_mode().name.lower() + "_map map`"
            await ctx.channel.send(message)

    @commands.command(name="tm_ban_map", aliases=["ban_map"])
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def ban_map(self, ctx, map_name):
        map_name = map_name.lower().replace(" ", "")
        captain_id = ctx.message.author.id
        status = self.__ongoing.get_captain_team_status(captain_id)
        decider = self.__ongoing.ban_map(map_name, captain_id)

        embed = discord.Embed(
            title="Map Banned",
            color=discord.Color.red()
        )
        embed.set_image(url=self.__resources[map_name])
        embed.add_field(name="Map Name", value=map_name.capitalize())
        embed.add_field(name="Banned by", value="Team " + status.name)
        embed.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")

        await ctx.channel.send(embed=embed)

        status_embed = self.__status_message.embeds[0]

        banned_text = map_name.capitalize() + " - Team " + status.name
        try:
            banned_field = status_embed.fields[6]
            status_embed.set_field_at(index=6, name=banned_field.name, value=banned_field.value + "\n" + banned_text)
        except IndexError:
            status_embed.add_field(name="Ban History", value=banned_text)
        finally:
            status_embed.set_field_at(index=5, name=status_embed.fields[5].name,
                                      value="\n".join(self.__ongoing.get_remaining_maps()))

        if decider is not None:
            embed_decider = discord.Embed(
                title="Map Picked",
                color=discord.Color.dark_grey()
            )
            embed_decider.set_image(url=self.__resources[decider])
            embed_decider.add_field(name="Map Name", value=decider.capitalize())
            embed_decider.add_field(name="Type", value="Decider")
            embed_decider.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")
            status_embed.add_field(name="Decider", value=decider.capitalize())
            status_embed.remove_field(index=5)
            await ctx.channel.send(embed=embed_decider)

        await self.__status_message.edit(embed=status_embed)

        if self.__display_help:
            map_pick_ban_entry = self.__ongoing.peek_next_map_pick_ban()
            try:
                message = "It is Team " + map_pick_ban_entry.get_team_status().name + "'s turn to " + \
                          map_pick_ban_entry.get_mode().name.lower() + " a map.\nThey can do so by using the command" \
                          "\n`." + map_pick_ban_entry.get_mode().name.lower() + "_map map`"
            except IndexError:
                message = "Map pick/ban phase is over. See you on the server!"
            await ctx.channel.send(message)

    @commands.command(name="tm_pick_map", aliases=["pick_map"])
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def pick_map(self, ctx, map_name):
        map_name = map_name.lower().replace(" ", "")
        captain_id = ctx.message.author.id
        status = self.__ongoing.get_captain_team_status(captain_id)
        self.__ongoing.pick_map(map_name, captain_id)

        embed = discord.Embed(
            title="Map Picked",
            color=discord.Color.green()
        )
        embed.set_image(url=self.__resources[map_name])
        embed.add_field(name="Map Name", value=map_name.capitalize())
        embed.add_field(name="Picked by", value="Team " + status.name)
        embed.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")

        await ctx.channel.send(embed=embed)

        status_embed = self.__status_message.embeds[0]

        status_embed.add_field(name="Team " + status.name + "'s Pick", value=map_name.capitalize())

        await self.__status_message.edit(embed=status_embed)

        if self.__display_help:
            message = "It is Team " + self.__ongoing.get_side_pick_team().name + "'s turn to pick a side.\nThey can" \
                      " do so by using the command\n`.pick_side side`"
            await ctx.channel.send(message)

    @commands.command(name="tm_pick_side", aliases=["pick_side"])
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def pick_side(self, ctx, side):
        captain_id = ctx.message.author.id
        side, decider = self.__ongoing.pick_side(captain_id, side)
        status = self.__ongoing.get_captain_team_status(captain_id)
        status_embed = self.__status_message.embeds[0]
        pick_field = status_embed.fields[len(status_embed.fields) - 1]
        status_embed.set_field_at(index=len(status_embed.fields) - 1, name=pick_field.name, value=pick_field.value +
                                  "\n" + status.name + "'s Start Side: " + side.name)
        await self.__status_message.edit(embed=status_embed)

        embed = discord.Embed(
            title="Side Selected",
            color=discord.Color.red() if status == TeamStatus.A else discord.Color.blue()
        )
        if side == Side.CT:
            embed.set_thumbnail(url=self.__resources["csgoCTLogo"])
        elif side == Side.T:
            embed.set_thumbnail(url=self.__resources["csgoTLogo"])
        elif side == Side.RANDOM:
            embed.set_thumbnail(url=self.__resources["csgoBothLogo"])
        else:
            raise SyntaxError

        embed.add_field(name="Side", value=side.name)
        embed.add_field(name="Team", value=status.name)
        embed.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")
        await ctx.channel.send(embed=embed)

        if decider is not None:
            embed_decider = discord.Embed(
                title="Map Picked",
                color=discord.Color.dark_grey()
            )
            embed_decider.set_image(url=self.__resources[decider])
            embed_decider.add_field(name="Map Name", value=decider.capitalize())
            embed_decider.add_field(name="Type", value="Decider")
            embed_decider.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")
            status_embed.add_field(name="Decider", value=decider.capitalize() + "\nB's Start Side: " + Side(randint(0, 1)).name)
            status_embed.set_field_at(index=5, name="\u200b", value="\u200b")

            await ctx.channel.send(embed=embed_decider)

        await self.__status_message.edit(embed=status_embed)

        if self.__display_help:
            try:
                map_pick_ban_entry = self.__ongoing.peek_next_map_pick_ban()
                message = "It is Team " + map_pick_ban_entry.get_team_status().name + "'s turn to " + \
                          map_pick_ban_entry.get_mode().name.lower() + " a map.\nThey can do so by using the command" \
                          "\n`." + map_pick_ban_entry.get_mode().name.lower() + "_map map`"
            except IndexError:
                message = "Map pick/ban phase is over. See you on the server!"
            await ctx.channel.send(message)

    @commands.command(name="tm_free", aliases=["free"])
    @commands.has_role(Config.get_config_property("tenman", "organizerRole"))
    async def free(self, ctx):
        captain_a_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamA", "captainRole"),
                              ctx.guild.roles)
        captain_b_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamB", "captainRole"),
                              ctx.guild.roles)
        player_a_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamA", "playerRole"),
                             ctx.guild.roles)
        player_b_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamB", "playerRole"),
                             ctx.guild.roles)

        await ctx.channel.send(content="Beginning deconstruction.")
        teams = self.__ongoing.get_teams()

        for a, b in zip(teams[0].get_players(), teams[1].get_players()):
            await find(lambda u: u.id == a, ctx.guild.members).remove_roles(captain_a_role, player_a_role)
            await find(lambda u: u.id == b, ctx.guild.members).remove_roles(captain_b_role, player_b_role)
        await ctx.channel.send(content="Players freed.")

        self.__ongoing = None


def setup(bot):
    bot.add_cog(TenManCog(bot))
