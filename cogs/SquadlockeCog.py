from discord.ext import commands
from cogs.helper.challonge import TournamentCommands
from _global.Config import Config

SQUADLOCKE_ROLE = Config.get_config_property("squadlocke_guild_role")
PARTICIPANTS = []


class SquadlockeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sl_init")
    async def squadlocke_init(self, ctx, *args):
        squadlocke_role = None
        for role in ctx.message.guild.roles:
            if role.name == SQUADLOCKE_ROLE:
                squadlocke_role = role

        members = ctx.message.channel.members
        for member in members:
            if squadlocke_role in member.roles:
                PARTICIPANTS.append(member)


def setup(bot):
    bot.add_cog(SquadlockeCog(bot))
