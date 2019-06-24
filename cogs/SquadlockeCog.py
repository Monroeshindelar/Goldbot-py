from discord.ext import commands
from cogs.helper.challonge import TournamentCommands
from _global.Config import Config
from utilities.utilities import read_or_create_file_pkl, save_to_file_pkl

SQUADLOCKE_DATA_FILE_PATH = Config.get_config_property("squadlocke_data_file")
SQUADLOCKE_ROLE = Config.get_config_property("squadlocke_guild_role")
SL_SERIALIZE = read_or_create_file_pkl(SQUADLOCKE_DATA_FILE_PATH)

PARTICIPANTS = {} if len(SL_SERIALIZE) < 1 else read_or_create_file_pkl(SQUADLOCKE_DATA_FILE_PATH)[0]


class SquadlockeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sl_init",)
    async def squadlocke_init(self, ctx, *args):
        squadlocke_role = None
        for role in ctx.message.guild.roles:
            if role.name == SQUADLOCKE_ROLE:
                squadlocke_role = role
                break

        if len(ctx.message.mentions) > 0:
            for mention in ctx.message.mentions:
                mention.add_roles(roles=squadlocke_role)

        members = ctx.message.channel.members
        for member in members:
            if squadlocke_role in member.roles:
                PARTICIPANTS.update({
                    member.id: False
                })
        await SquadlockeCog.__save_squadlocke()

    @commands.command(name="sl_ready_up")
    async def squadlocke_ready_up(self, ctx):
        message = "Looks like there was a problem with readying you up\n" \
                  "Make sure you're a participant in the squadlocke before using this command"
        if ctx.message.author.id in PARTICIPANTS:
            PARTICIPANTS[ctx.message.author.id] = True
            message = "You have been readied up!"
            await SquadlockeCog.__save_squadlocke()
        await ctx.message.channel.send(
            content=message
        )


    @staticmethod
    async def __save_squadlocke():
        squadlocke_object = [PARTICIPANTS]
        save_to_file_pkl(squadlocke_object, SQUADLOCKE_DATA_FILE_PATH)


def setup(bot):
    bot.add_cog(SquadlockeCog(bot))



