import logging
from discord.ext import commands

LOGGER = logging.getLogger("goldlog")


class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Debug Cog Initialized")

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.channel.send("I am online.")


def setup(bot):
    bot.add_cog(DebugCog(bot))