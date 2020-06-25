import logging
from discord.ext import commands
from core.Wedlocke import Wedlocke
from core.model.wedlocke.Gender import Gender
from _global.Config import Config
from utilities.Misc import read_save_file, save_file, create_save_dir
from _global.ArgParsers.WedlockeArgParser import WedlockeArgParser
from _global.ArgParsers.ThrowingArgumentParser import ArgumentParserError
from discord.utils import find
from tabulate import tabulate

LOGGER = logging.getLogger("goldlog")


class WedlockeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.save_dir = Config.get_config_property("saveDir") + "/wedlocke"
        self.save_data = self.save_dir + "/wldata.pkl"
        create_save_dir(self.save_dir)
        self.ongoing = read_save_file(self.save_data)
        LOGGER.info("Initialized wedlocke command cog.")

    @commands.command(name="wlinit")
    async def wl_init(self, ctx, *args):
        try:
            parsed_args = WedlockeArgParser.WL_INIT_ARG_PARSER.parse_known_args(args)[0]
        except ArgumentParserError as e:
            raise commands.ArgumentParsingError(message=e.args[0])

        self.ongoing = Wedlocke(ctx.message.mentions[0].id, ctx.message.mentions[1].id, parsed_args.game)
        save_file(self.ongoing, self.save_data)

        message = "Initialized Wedlocke for " + ctx.message.mentions[0].name + " and " + ctx.message.mentions[1].name \
                  + "."

        await ctx.message.channel.send(content=message)

    @commands.command(name="wladdpair")
    async def wl_add_pair(self, ctx, *args):
        try:
            parsed_args = WedlockeArgParser.WL_ADD_PAIR_ARG_PARSER.parse_known_args(args)[0]
        except ArgumentParserError as e:
            raise commands.ArgumentParsingError(message=e.args[0])

        self.ongoing.create_or_append_pair(parsed_args.species, Gender.get(parsed_args.gender), parsed_args.nickname,
                                           ctx.message.author.id, parsed_args.route)
        save_file(self.ongoing, self.save_data)

    @commands.command(name="wlkillpair")
    async def wl_kill_pair(self, ctx, *args):
        try:
            parsed_args = WedlockeArgParser.WL_KILL_PAIR_ARG_PARSER.parse_known_args(args)[0]
        except ArgumentParserError as e:
            raise commands.ArgumentParsingError(message=e.args[0])

        self.ongoing.kill_pair(parsed_args.route)

    @commands.command(name="wlgetpairs")
    async def wl_get_pairs(self, ctx, *args):
        pairs = self.ongoing.get_pairs()

        participant1_acc = find(lambda a: a.id == self.ongoing.get_participants()[0], ctx.guild.members)
        participant2_acc = find(lambda a: a.id == self.ongoing.get_participants()[1], ctx.guild.members)

        headers = ["Route", participant1_acc.name + "'s Nickname", participant2_acc.name + "'s Nickname",
                   participant1_acc.name + "'s Species", participant2_acc.name + "'s Species",
                   "Status"]

        table = [[pairs[pair].get_route(),
                 pairs[pair].get_encounters()[0].get_nickname() if pairs[pair].get_encounters()[0].get_owner() == participant1_acc.id else
                 pairs[pair].get_encounters()[1].get_nickname(),
                 pairs[pair].get_encounters()[0].get_nickname() if pairs[pair].get_encounters()[0].get_owner() == participant2_acc.id else
                 pairs[pair].get_encounters()[1].get_nickname(),
                 pairs[pair].get_encounters()[0].get_species() if pairs[pair].get_encounters()[0].get_owner() == participant1_acc.id else
                 pairs[pair].get_encounters()[1].get_species(),
                 pairs[pair].get_encounters()[0].get_species() if pairs[pair].get_encounters()[0].get_owner() == participant2_acc.id else
                 pairs[pair].get_encounters()[1].get_species(),
                 pairs[pair].get_status().name] for pair in pairs]

        await ctx.channel.send(content="```" + tabulate(table, headers=headers) + "```")


def setup(bot):
    bot.add_cog(WedlockeCog(bot))
