import logging
from tabulate import tabulate
from discord.utils import find
from discord.ext import commands
from core import UserAccounts

LOGGER = logging.getLogger("goldlog")


class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Initialized server command cog.")

    @commands.command(name="leaderboard")
    async def get_leaderboard(self, ctx, emote):
        emote = find(lambda e: str(e) == emote, ctx.guild.emojis)
        accounts = None
        if emote is not None:
            accounts = [(account.name, UserAccounts.get_account(account).get_leaderboard_info(emote.name)) for account
                        in ctx.guild.members if UserAccounts.get_account(account) is not None and
                        UserAccounts.get_account(account).get_leaderboard_info(emote.name) is not None and
                        UserAccounts.get_account(account).get_leaderboard_info(emote.name)["score"] != 0]
        if accounts is not None and len(accounts) > 0:
            accounts.sort(key=lambda a: a[1]["score"], reverse=True)
            table = [[account[0], account[1]["score"], account[1]["current_streak"], account[1]["longest_streak"]]
                     for account in accounts]
            await ctx.channel.send(str(emote) + "***  Leaderboard  ***" + str(emote) + "\n```" +
                                   tabulate(table, headers=["Name", "Score", "Current Streak", "Longest Streak"],
                                            tablefmt="github") + "```")
        else:
            await ctx.channel.send("There is no leaderboard associated with that emoji.")


def setup(bot):
    bot.add_cog(ServerCog(bot))
