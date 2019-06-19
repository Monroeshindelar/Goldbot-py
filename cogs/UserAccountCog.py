from discord.ext import commands
from core.UserAccounts import get_account


class UserAccountCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_friend_code")
    async def set_friend_code(self, ctx, *args):
        account = get_account(ctx.message.author.id)
        account.set_friend_code(args[0])

    @commands.command(name="get_friend_code")
    async def get_friend_code(self, ctx):
        account = get_account(ctx.message.mentions[0].id)
        if account is not None:
            await ctx.message.channel.send(content=account.get_friend_code())


def setup(bot):
    bot.add_cog(UserAccountCog(bot))
