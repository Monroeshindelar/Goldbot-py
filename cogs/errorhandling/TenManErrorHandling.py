from discord.ext import commands
from cogs.TenManCog import TenManCog


@TenManCog.pick_player.error
async def pick_player_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        ctx.channel.send(content="You do not have the permission to call this command")
