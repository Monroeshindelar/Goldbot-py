import logging
import json
import discord
from tabulate import tabulate
from discord.utils import find
from discord.ext import commands
from _global.argparsers.serverargparsers import ServerArgParsers
from _global.argparsers.throwingargumentparser import ArgumentParserError
from _global.config import Config

LOGGER = logging.getLogger("goldlog")


class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        LOGGER.info("Initialized server command cog.")

    @commands.command(name="leaderboard")
    async def get_leaderboard(self, ctx, *args):
        try:
            parsed_args = ServerArgParsers.LEADERBOARD_ARG_PARSER.parse_known_args(args)[0]
        except ArgumentParserError as e:
            raise commands.ArgumentParsingError(message=e.args[0])

        emoji = find(lambda em: str(em) == parsed_args.emoji, ctx.guild.emojis)

        try:
            if emoji.name not in Config.get_config_property("server", "leaderboard", "emojiMap").keys():
                raise commands.BadArgument("There is no leaderboard associated with the emoji.")

            with open("{0}/leaderboards/{1}/{2.name}.json".format(Config.get_config_property("saveDir"),
                                                                  str(ctx.guild.id), emoji)) as f:
                leaderboard_json = json.load(f)

            entries = sorted(leaderboard_json, key=lambda e: (leaderboard_json[e]["score"],
                             leaderboard_json[e]["current_streak"], leaderboard_json[e]["longest_streak"]),
                             reverse=True)

        except AttributeError as e:
            raise commands.BadArgument("Leaderboards don't exist for default emojis.")
        except FileNotFoundError as e:
            raise commands.BadArgument("No leaderboard data found for called emoji.")

        try:
            entries = entries[0:int(parsed_args.top)]
        except TypeError:
            pass
        except IndexError:
            pass
        except ValueError:
            raise commands.BadArgument("Bad argument for top parameter. Expected integer.")

        embed = discord.Embed(
            title="Leaderboard | {0.name}".format(emoji)
        )

        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name="User", value="\n".join([find(lambda u: str(u.id) == e, ctx.guild.members).name for e in entries]))
        embed.add_field(name="Score", value="\n".join([str(leaderboard_json[e]["score"]) for e in entries]))
        embed.add_field(name="Streak", value="\n".join([str(leaderboard_json[e]["current_streak"]) for e in entries]))

        await ctx.channel.send(embed=embed)


        # await ctx.channel.send(str(emoji) + "***  Leaderboard  ***" + str(emoji) + "\n```" + tabulate(table,
        #                        headers=headers) + "```")


def setup(bot):
    bot.add_cog(ServerCog(bot))
