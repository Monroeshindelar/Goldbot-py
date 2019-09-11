import logging
from discord.ext import commands
from core.UserAccounts import get_account
from _global.Config import Config

LOGGER = logging.getLogger("goldlog")

OPTIONAL_ROLES = Config.get_config_property("optional_role_names").split(',')


class UserAccountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Initialized user account command cog.")

    @commands.command(name="set_friend_code")
    async def set_friend_code(self, ctx, friend_code: str):
        account = get_account(ctx.message.author.id)
        if account.set_friend_code(friend_code):
            await ctx.channel.send(content="Your friend code has been set!")
            LOGGER.info("UserCommand::get_friend_code called for " + ctx.message.author.name)
        else:
            # message = "Incorrect friend code formatting. Please try again."
            LOGGER.warning("UserCommand::set_friend_code call failed for " + ctx.message.author.id + ". Invalid formatting")
            raise commands.BadArgument("Incorrect Friend Code formatting. Expecting formats:\n"
                                       "`1234-1234-1234`\n`SW-1234-1234-1234`\n`DS-1234-1234-1234`", friend_code)

    @commands.command(name="get_friend_code")
    async def get_friend_code(self, ctx):
        if len(ctx.message.mentions) < 1:
            LOGGER.warning("UserCommand::get_friend_code called with not enough arguments.")
            raise commands.BadArgument("You are missing required arguments for this command:\n`user (@mention)`")
        account = get_account(ctx.message.mentions[0].id)
        if account is not None:
            LOGGER.info("UserCommand::get_friend_code successfully called by " + ctx.message.author.name)
            await ctx.channel.send(content=account.get_friend_code())
        else:
            LOGGER.warning("UserCommand::get_friend_code called for invalid user.")
            raise commands.BadArgument("You requested the friend code for a user that does not exist")

    @commands.command(name="add_role")
    async def add_role(self, ctx):
        if len(ctx.message.role_mentions) < 1:
            LOGGER.warning("UserCommand::add_role call failed for " + ctx.message.author.name +
                           ". Invalid number of arguments")
            raise commands.BadArgument(message="You are missing required arguments for this command:\n`role "
                                               "(@mention)`")
        account = ctx.message.author
        role = ctx.message.role_mentions[0]
        if UserAccountCog.__role_is_optional(role):
            await account.add_roles(role)
            await ctx.channel.send(content="Role has been successfully assigned.")
            LOGGER.info("UserCommand::add_role called for " + account.name + ":" + role.name)
        else:
            LOGGER.warning("UserCommand::add_role call failed due to invalid arguments.")
            raise commands.BadArgument("The role you are trying to assign to yourself either doesnt exist or "
                                       "is not a user manageable role.")

    @commands.command(name="remove_role")
    async def remove_role(self, ctx):
        if len(ctx.message.role_mentions) < 1:
            LOGGER.warning("UserCommand::remove_role failed for " + ctx.message.author.name
                           + " because no role was mentioned")
            raise commands.BadArgument(message="You are missing required arguments for this command:\n`role "
                                               "(@mention)`")
        account = ctx.message.author
        role = ctx.message.role_mentions[0]
        if role in account.roles:
            if UserAccountCog.__role_is_optional(role):
                await account.remove_roles(role)
                ctx.channel.send(content="Role has been successfully removed.")
                LOGGER.info("UserCommands::remove_role successfully called for " + account.name + ":" + role.name)
            else:
                LOGGER.warning("UserCommands::remove_role call failed for " + account.name + ".  Bad arguments")
                raise commands.BadArgument("The role you are trying to remove either doesnt exist or "
                                           "is not a user manageable role.")

    @staticmethod
    def __role_is_optional(role):
        optional = False
        for role_name in OPTIONAL_ROLES:
            if role.name == role_name:
                optional = True
                break
        return optional


def setup(bot):
    bot.add_cog(UserAccountCog(bot))
