import discord
import traceback
import sys
import logging
from discord.ext import commands
from ErrorHandling.Exceptions.TenMan.EntityError import EntityError
from ErrorHandling.Exceptions.TenMan.InitializationError import InitializationError
from ErrorHandling.Exceptions.TenMan.TurnError import TurnError
from ErrorHandling.Exceptions.TenMan.PhaseError import PhaseError

LOGGER = logging.getLogger("goldlog")


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        LOGGER.info("Initialized Command Error Handler cog.")
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send(
                content="You are missing required arguments for this command:\n`" + error.param.name +
                        "`")
        elif isinstance(error, (commands.BadArgument, commands.UserInputError, commands.ArgumentParsingError,
                                commands.MissingAnyRole, commands.MissingRole, EntityError, TurnError, PhaseError,
                                InitializationError)):
            await ctx.channel.send(content=error.args[0])
        else:
            LOGGER.error(error, exc_info=True)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
