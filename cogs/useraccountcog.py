import logging
from discord.ext import commands
from core.useraccounts import get_account
from _global.config import Config
from utilities.misc import get_project_dir

LOGGER = logging.getLogger("goldlog")

SERVER_SAVE_FILE = get_project_dir() / "{0}/server.pkl".format(Config.get_config_property("saveDir"))


class UserAccountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Initialized user account command cog.")

    @commands.command(name="set_friend_code")
    async def set_friend_code(self, ctx, friend_code: str):
        account = get_account(ctx.message.author)
        if account.set_friend_code(friend_code):
            await ctx.channel.send(content="Your friend code has been set!")
            LOGGER.info("UserCommand::get_friend_code called for " + ctx.message.author.name)
        else:
            LOGGER.warning("UserCommand::set_friend_code call failed for " + str(ctx.message.author.id) +
                           ". Invalid formatting")
            raise commands.BadArgument("Incorrect Friend Code formatting. Expecting formats:\n"
                                       "`1234-1234-1234`\n`SW-1234-1234-1234`\n`DS-1234-1234-1234`", friend_code)

    @commands.command(name="get_friend_code")
    async def get_friend_code(self, ctx):
        if len(ctx.message.mentions) < 1:
            LOGGER.warning("UserCommand::get_friend_code called with not enough arguments.")
            raise commands.BadArgument("You are missing required arguments for this command:\n`user (@mention)`")
        account = get_account(ctx.message.mentions[0])
        if account is not None:
            LOGGER.info("UserCommand::get_friend_code successfully called by " + ctx.message.author.name)
            if account.get_friend_code() is not None:
                await ctx.channel.send(content=account.get_friend_code())
                message = account.get_friend_code()
            else:
                message = ctx.message.mentions[0].name + " has not set their friend code."
            await ctx.channel.send(content=message)
        else:
            LOGGER.warning("UserCommand::get_friend_code called for invalid user.")
            raise commands.BadArgument("You requested the friend code for a user that does not exist")


def setup(bot):
    bot.add_cog(UserAccountCog(bot))
