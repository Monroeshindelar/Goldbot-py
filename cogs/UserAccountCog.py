from discord.ext import commands
from core.UserAccounts import get_account


class UserAccountCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_friend_code")
    async def set_friend_code(self, ctx, *args):
        if len(args) < 1:
            await ctx.message.channel.send(
                content="```Usage:\n !set_friend_code friend_code"
                        "\n\nfriend_code: Your nintendo friend code"
            )
            return
        account = get_account(ctx.message.author.id)
        if account.set_friend_code(args[0]):
            message = "Your friend code has been set!"
        else:
            message = "Incorrect friend code formatting. Please try again."

        await ctx.message.channel.send(message)

    @commands.command(name="get_friend_code")
    async def get_friend_code(self, ctx):
        account = get_account(ctx.message.mentions[0].id)
        if account is not None:
            await ctx.message.channel.send(content=account.get_friend_code())


def setup(bot):
    bot.add_cog(UserAccountCog(bot))
