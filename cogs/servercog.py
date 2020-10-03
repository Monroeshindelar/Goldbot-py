import logging
import json
from tabulate import tabulate
from discord.utils import find
from discord.ext import commands
from _global.argparsers.serverargparsers import ServerArgParsers
from _global.argparsers.throwingargumentparser import ArgumentParserError
from _global.config import Config
from utilities.misc import get_project_dir

LOGGER = logging.getLogger("goldlog")


class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Initialized server command cog.")

    @commands.command(name="leaderboard")
    async def get_leaderboard(self, ctx, *args):
        try:
            parsed_args = ServerArgParsers.LEADERBOARD_ARG_PARSER.parse_known_args(args)[0]
        except ArgumentParserError as e:
            raise commands.ArgumentParsingError(message=e.args[0])

        if parsed_args.mobile:
            headers = ["N", "S", "CS", "LS"]
        else:
            headers = ["Name", "Score", "Current Streak", "Longest Streak"]

        emoji = find(lambda em: str(em) == parsed_args.emoji, ctx.guild.emojis)

        try:
            if emoji.name not in Config.get_config_property("server", "leaderboard", "emojiMap").keys():
                raise commands.BadArgument("There is no leaderboard associated with the emoji.")
            relative_path = "{0}/leaderboards/{1}/{2}.json".format(Config.get_config_property("saveDir"),
                                                                   str(ctx.guild.id), emoji.name)
            with open(str(get_project_dir() / relative_path)) as f:
                leaderboard_json = json.load(f)

            entries = sorted(leaderboard_json, key=lambda e: (leaderboard_json[e]["score"],
                             leaderboard_json[e]["current_streak"], leaderboard_json[e]["longest_streak"]),
                             reverse=True)

        except AttributeError as e:
            LOGGER.error("ServerCog::leaderboard - Called with default emoji.")
            raise commands.BadArgument("Leaderboards don't exist for default emojis.")
        except FileNotFoundError as e:
            LOGGER.error("ServerCog::leaderboard - No leaderboard data found for called emoji")
            raise commands.BadArgument("No leaderboard data found for called emoji.")

        try:
            entries = entries[0:int(parsed_args.top)]
        except TypeError:
            pass
        except IndexError:
            LOGGER.warning("Specified a value that was larger than the amount of users with scores")
            pass
        except ValueError:
            LOGGER.error("ServerCog::leaderboard - " + parsed_args.top + " is not an int")
            raise commands.BadArgument("Bad argument for top parameter. Expected integer.")

        table = [[find(lambda u: str(u.id) == e, ctx.guild.members).name, leaderboard_json[e]["score"],
                  leaderboard_json[e]["current_streak"], leaderboard_json[e]["longest_streak"]] for e in entries]

        await ctx.channel.send("{0}*** Leaderboard ***{0}\n```{1}```".format(str(emoji), tabulate(table,
                                                                                                  headers=headers)))

    @commands.command(name="add_role", aliases=["subscribe"])
    async def add_role(self, ctx):
        if len(ctx.message.role_mentions) < 1:
            raise commands.BadArgument(message="You are missing required arguments for this command:\n`role "
                                               "(@mention)`")
        account = ctx.message.author
        role = ctx.message.role_mentions[0]
        if ServerCog.__role_is_optional(role):
            await account.add_roles(role)
            await ctx.channel.send(content="Role has been successfully assigned.")
        else:
            raise commands.BadArgument("The role you are trying to assign to yourself either doesnt exist or "
                                       "is not a user manageable role.")

    @commands.command(name="remove_role", aliases=["unsubscribe"])
    async def remove_role(self, ctx):
        if len(ctx.message.role_mentions) < 1:
            raise commands.BadArgument(message="You are missing required arguments for this command:\n`role "
                                               "(@mention)`")
        account = ctx.message.author
        role = ctx.message.role_mentions[0]
        if role in account.roles:
            if ServerCog.__role_is_optional(role):
                await account.remove_roles(role)
                await ctx.channel.send(content="Role has been successfully removed.")
            else:
                raise commands.BadArgument("The role you are trying to remove either doesnt exist or "
                                           "is not a user manageable role.")

    @commands.command(name="make_role_subscribable")
    @commands.has_permissions(administrator=True)
    async def make_role_subscribable(self, ctx):
        if len(ctx.message.role_mentions) < 1:
            raise commands.BadArgument(message="You are missing required arguments for this command:\n`role "
                                               "(@mention)`")
        role_list = Config.get_config_property("server", "optionalRoles")
        role_list.append(ctx.message.role_mentions[0].name)
        Config.update_config_property_and_write("server/optionalRoles", role_list)

    @staticmethod
    def __role_is_optional(role):
        return role.name in Config.get_config_property("server", "optionalRoles")


def setup(bot):
    bot.add_cog(ServerCog(bot))
