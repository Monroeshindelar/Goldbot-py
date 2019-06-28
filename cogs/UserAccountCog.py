from discord.ext import commands
from core.UserAccounts import get_account
from _global.Config import Config

OPTIONAL_ROLES = Config.get_config_property("optional_role_names").split(',')


class UserAccountCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_friend_code")
    async def set_friend_code(self, ctx, *args):
        if len(args) < 1:
            await ctx.channel.send(
                content="```Usage:\n !set_friend_code friend_code"
                        "\n\nfriend_code: Your nintendo friend code"
            )
            return
        account = get_account(ctx.message.author.id)
        if account.set_friend_code(args[0]):
            message = "Your friend code has been set!"
        else:
            message = "Incorrect friend code formatting. Please try again."

        await ctx.channel.send(message)

    @commands.command(name="get_friend_code")
    async def get_friend_code(self, ctx):
        account = get_account(ctx.message.mentions[0].id)
        if account is not None:
            await ctx.channel.send(content=account.get_friend_code())

    @commands.command(name="add_role")
    async def add_role(self, ctx):
        message = "The role you are trying to assign to yourself either doesnt exist or " \
                  "is not a user manageable role."
        account = ctx.message.author
        role = ctx.message.role_mentions[0]
        if UserAccountCog.__role_is_optional(role):
            await account.add_roles(role)
            message = "Role has been successfully assigned."
        await ctx.channel.send(content=message)

    @commands.command(name="remove_role")
    async def remove_role(self, ctx):
        message = "The role you were trying to remove either doesn't exist or is not a user" \
                  " manageable role."
        account = ctx.message.author
        role = ctx.message.role_mentions[0]
        if role in account.roles:
            if UserAccountCog.__role_is_optional(role):
                await account.remove_roles(role)
                message = "Role has been successfully removed."
        await ctx.channel.send(content=message)

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
