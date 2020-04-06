import logging
from tabulate import tabulate
from discord.utils import find
from discord.ext import commands
from core import UserAccounts
from _global.ArgParsers.ServerArgParsers import ServerArgParsers
from _global.ArgParsers.ThrowingArgumentParser import ArgumentParserError
from _global.Config import Config

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

        emoji = find(lambda em: str(em) == parsed_args.emoji, ctx.guild.emojis)

        if parsed_args.mobile:
            headers = ["N", "S", "CS", "LS"]
            table_format = "plain"
        else:
            headers = ["Name", "Score", "Current Streak", "Longest Streak"]
            table_format = "github"

        try:
            if emoji.name not in Config.get_config_property("server", "leaderboardTracking").keys():
                raise commands.BadArgument("There is no leaderboard associated with the emoji.")

            accounts = [(account.name, UserAccounts.get_account(account).get_leaderboard_info(emoji.name)) for account
                        in ctx.guild.members if UserAccounts.get_account(account) is not None and
                        UserAccounts.get_account(account).get_leaderboard_info(emoji.name) is not None and
                        UserAccounts.get_account(account).get_leaderboard_info(emoji.name)["score"] != 0]
        except AttributeError:
            LOGGER.error("ServerCog::leaderboard - Called with default emoji.")
            raise commands.BadArgument("Leaderboards don't exist for default emojis.")

        accounts = sorted(accounts, key=lambda a: (a[1]["score"], a[1]["current_streak"], a[1]["longest_streak"]),
                          reverse=True)
        try:
            accounts = accounts[0:int(parsed_args.top)]
        except TypeError:
            pass
        except IndexError:
            LOGGER.warning("Specified a value that was larger than the amount of users with scores")
            pass
        except ValueError:
            LOGGER.error("ServerCog::leaderboard - " + parsed_args.top + " is not an int")
            raise commands.BadArgument("Bad argument for top parameter. Expected integer.")

        table = [[account[0], account[1]["score"], account[1]["current_streak"], account[1]["longest_streak"]]
                 for account in accounts]
        await ctx.channel.send(str(emoji) + "***  Leaderboard  ***" + str(emoji) + "\n```" + tabulate(table,
                               headers=headers, tablefmt=table_format) + "```")


def setup(bot):
    bot.add_cog(ServerCog(bot))
