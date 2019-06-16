from discord.ext import commands
from core import UserAccounts


class UserAccountCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_friend_code",
                      aliases=["add_friendcode", "set_friend_code", "set_friendcode"])
    async def add_friend_code(self, ctx, *args):
        old_account = UserAccounts.get_account(ctx.message.author.id)
        new_account = old_account
        # check for validity with regex
        new_account.friend_code = args[0]
        UserAccounts.modify_account(old_account, new_account)
        UserAccounts.save_accounts()
        print("done")

    @commands.command(name="get_friend_code")
    async def get_friend_code(self, ctx, *args):
        account = UserAccounts.get_account(ctx.message.author.id)
        if account.friend_code is not None:
            print(account.friend_code)
        else:
            print("didnt work")


def setup(bot):
    bot.add_cog(UserAccountCog(bot))
