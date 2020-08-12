from discord.ext import commands
from discord.utils import find
from _global.Config import Config
from core.TenMan import TenMan
from core.model.TenMan.Game import Game
from core.model.TenMan.CaptainStatus import CaptainStatus
from core.model.TenMan.Side import Side
from _global.ArgParsers.TenManArgParsers import TenManArgParsers
from _global.ArgParsers.ThrowingArgumentParser import ArgumentParserError
import yaml
import logging
import discord

LOGGER = logging.getLogger("goldlog")


class TenManCogNew(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__ongoing = None
        self.__status_message = None
        with open("bin/resources/tenman/resources.yml") as f:
            self.__resources = yaml.load(f, Loader=yaml.FullLoader)
        LOGGER.info("Initialized ten man command cog.")

    @commands.command(name="tm_init", aliases=["tm_start"])
    @commands.has_role(Config.get_config_property("tenman", "organizerRole"))
    async def init(self, ctx, *args):
        if self.__ongoing is not None:
            raise SyntaxError

        try:
            parsed_args = TenManArgParsers.TM_INIT_ARG_PARSER.parse_known_args(args)[0]
        except ArgumentParserError as e:
            raise commands.ArgumentParsingError(message=e.args[0])

        game = Game.get(parsed_args.game)

        general_voice = find(lambda v: v.name == Config.get_config_property("tenman", "generalVoice"),
                             ctx.guild.voice_channels)
        # member_list = [m.id for m in general_voice.members]
        # member_list = ["133445513344319488", "148297442452963329", "113118901381967872", "176904641878032385",
        #                "150082226850234368", "645696336469164107", "148337577055748096", "133450790646841344",
        #                "128953069537853440", "285699164879192065"]
        member_list = ["148297442452963329", "645696336469164107", "727670795081351188", "727672213871919215", "727672966539771934"]
        self.__ongoing = TenMan(member_list, game)
        embed = discord.Embed(
            title=ctx.guild.name + " Ten Man",
            description="Ten Man initialization completed!",
            color=discord.Color.dark_grey()
        )
        if game == Game.CSGO:
            logo = self.__resources["csgoLogo"]
            # mapPickBanSequence = Config.get_config_property("tenman", "mapPickBanSequence", "csgo", "bo3")
        elif game == Game.VALORANT:
            logo = self.__resources["valorantLogo"]
            # mapPickBanSequence = Config.get_config_property("tenman", "mapPickBanSequence", "valorant", "bo3")

        embed.add_field(name="Game", value=game.name)
        embed.add_field(name="Type", value="Best of 3")
        embed.add_field(name="Player Pick Sequence", value=Config.get_config_property("tenman", "playerPickSequence"))
        # embed.add_field(name="Map Pick Ban Sequence", value=mapPickBanSequence, inline=False)
        embed.add_field(name="Available Participants", value="\n".join([find(lambda u: str(u.id) == p, ctx.guild.members).name
                                                              for p in member_list]))
        embed.add_field(name="Available Map Pool", value="\n".join(self.__ongoing.get_remaining_maps()), inline=False)

        embed.set_image(url=logo)
        self.__status_message = await ctx.channel.send(embed=embed)

    @commands.command(name="tm_pc")
    @commands.has_role(Config.get_config_property("tenman", "organizerRole"))
    async def pick_captains(self, ctx):
        if len(ctx.message.mentions) > 2:
            raise SyntaxError

        captain_a_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamA", "captainRole"), ctx.guild.roles)
        captain_b_role = find(lambda r: r.name == Config.get_config_property("tenman", "teamB", "captainRole"), ctx.guild.roles)
        captain_ids = ctx.message.raw_mentions
        captains = self.__ongoing.set_or_pick_captains(captain_ids)
        captain_a = find(lambda c: str(c.id) == str(captains[0]), ctx.guild.members)
        captain_b = find(lambda c: str(c.id) == str(captains[1]), ctx.guild.members)
        await captain_a.add_roles(captain_a_role)
        await captain_b.add_roles(captain_b_role)

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
        status_embed.set_field_at(index=3, name=rp_field.name, value="\n".join([find(lambda u: str(u.id) == rp, ctx.guild.members).name for rp in self.__ongoing.get_remaining_participant_ids()]))
        status_embed.insert_field_at(index=4, name="Team A", value=captain_a.name, inline=True)
        status_embed.insert_field_at(index=5, name="Team B", value=captain_b.name, inline=True)
        await self.__status_message.edit(embed=status_embed)

    @commands.command(name="tm_pp")
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def pick_player(self, ctx):
        if len(ctx.message.raw_mentions) > 1:
            raise SyntaxError

        pick_info = self.__ongoing.pick_player(ctx.message.mentions[0].id, ctx.message.author.id)

        embed = discord.Embed(
            title="Player Selected",
            color=discord.Color.red() if pick_info[1] == CaptainStatus.CAPTAIN_A else discord.Color.blue()
        )
        embed.add_field(name="Name", value=ctx.message.mentions[0].name)
        embed.add_field(name="Picked By", value="Team " + ("A" if pick_info[1] == CaptainStatus.CAPTAIN_A else "B"))
        embed.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")
        embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
        await ctx.channel.send(embed=embed)

        status_embed = self.__status_message.embeds[0]
        team_field = status_embed.fields[4 if pick_info[1] == CaptainStatus.CAPTAIN_A else 5]
        status_embed.set_field_at(index=(4 if pick_info[1] == CaptainStatus.CAPTAIN_A else 5), name=team_field.name,
                                  value=(team_field.value + "\n" + ctx.message.mentions[0].name))

        if pick_info[2] is not None and pick_info[3] is not None:
            last_pick_profile = find(lambda p: str(p.id) == pick_info[2], ctx.guild.members)
            embed_lp = discord.Embed(
                title="Last Pick",
                color=discord.Color.red() if pick_info[3] == CaptainStatus.CAPTAIN_A else discord.Color.blue()
            )
            embed_lp.set_thumbnail(url=last_pick_profile.avatar_url)
            embed_lp.add_field(name="Name", value=last_pick_profile.name)
            embed_lp.add_field(name="Picked for", value="Team " + ("A" if pick_info[3] == CaptainStatus.CAPTAIN_A else "B"))
            embed_lp.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")
            await ctx.channel.send(embed=embed_lp)
            status_embed.remove_field(index=3)
            status_embed.set_field_at(index=(3 if pick_info[2] == CaptainStatus.CAPTAIN_A else 4), name=team_field.name,
                                      value=(team_field.value + "\n" + last_pick_profile.name))
            status_embed.set_field_at(index=5, name=status_embed.fields[5].name, value=status_embed.fields[5].value, inline=True)
        else:
            rp_field = status_embed.fields[3]
            status_embed.set_field_at(index=3, name=rp_field.name, value="\n".join(
                [find(lambda u: str(u.id) == rp, ctx.guild.members).name for rp in
                 self.__ongoing.get_remaining_participant_ids()]))
            status_embed.set_field_at(index=5, name=status_embed.fields[5].name, value=status_embed.fields[5].value,
                                      inline=True)
        await self.__status_message.edit(embed=status_embed)

    @commands.command(name="tm_bm")
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def ban_map(self, ctx, map_name):
        map_name = map_name.lower().replace(" ", "")
        captain, decider = self.__ongoing.ban_map(map_name, str(ctx.message.author.id))

        embed = discord.Embed(
            title="Map Banned",
            color=discord.Color.red()
        )
        embed.set_image(url=self.__resources[map_name])
        embed.add_field(name="Map Name", value=map_name.capitalize())
        embed.add_field(name="Banned by", value="Team " + ("A" if captain == CaptainStatus.CAPTAIN_A else "B"))
        embed.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")

        await ctx.channel.send(embed=embed)

        status_embed = self.__status_message.embeds[0]

        banned_text = map_name.capitalize() + " - Team " + (
            "A" if captain == CaptainStatus.CAPTAIN_A else "B")
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

    @commands.command(name="tm_pm")
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def pick_map(self, ctx, map_name):
        map_name = map_name.lower().replace(" ", "")
        captain = self.__ongoing.pick_map(map_name, str(ctx.message.author.id))

        embed = discord.Embed(
            title="Map Picked",
            color=discord.Color.green()
        )
        embed.set_image(url=self.__resources[map_name])
        embed.add_field(name="Map Name", value=map_name.capitalize())
        embed.add_field(name="Picked by", value="Team " + ("A" if captain == CaptainStatus.CAPTAIN_A else "B"))
        embed.add_field(name="Ten Man Status", value="[Link](" + self.__status_message.jump_url + ")")

        await ctx.channel.send(embed=embed)

        status_embed = self.__status_message.embeds[0]

        status_embed.add_field(name="Team " + ("A" if captain == CaptainStatus.CAPTAIN_A else "B") + "'s Pick",
                               value=map_name.capitalize())

        # try:
        #     decider = self.__ongoing.final_map_pick()
        #     embed_decider = discord.Embed(
        #         title=decider,
        #         color=discord.Color.dark_grey(),
        #         description="Decider map."
        #     )
        #     embed_decider.set_image(url=self.__resources[decider])
        #     await ctx.channel.send(embed=embed_decider)
        #     status_embed.add_field(name="Decider", value=decider.capitalize())
        # except SyntaxError:
        #     pass
        # finally:
        #     status_embed.set_field_at(index=5, name=status_embed.fields[5].name, value="\n".join(self.__ongoing.get_remaining_maps()))

        await self.__status_message.edit(embed=status_embed)

    @commands.command(name="tm_ps")
    @commands.has_any_role(Config.get_config_property("tenman", "teamA", "captainRole"),
                           Config.get_config_property("tenman", "teamB", "captainRole"))
    async def pick_side(self, ctx, side):
        side, status, decider = self.__ongoing.pick_side(str(ctx.message.author.id), side)
        status_embed = self.__status_message.embeds[0]
        pick_field = status_embed.fields[len(status_embed.fields) - 1]
        status_embed.set_field_at(index=len(status_embed.fields) - 1, name=pick_field.name, value=pick_field.value +
                                  "\n" + ("A" if status == CaptainStatus.CAPTAIN_A else "B") + "'s Start Side: " + side.name)
        await self.__status_message.edit(embed=status_embed)

        embed = discord.Embed(
            title="Side Selected",
            color=discord.Color.red() if status == CaptainStatus.CAPTAIN_A else discord.Color.blue()
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
        embed.add_field(name="Team", value="A" if status == CaptainStatus.CAPTAIN_A else "B")
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
            status_embed.add_field(name="Decider", value=decider.capitalize())
            status_embed.remove_field(index=5)
            await ctx.channel.send(embed=embed_decider)


def setup(bot):
    bot.add_cog(TenManCogNew(bot))
