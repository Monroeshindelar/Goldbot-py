from _global.Config import Config
from utilities import Misc
from core.Goldbot import Goldbot

LOGGER = Misc.setup_logging()


def main():
    cogs = [
        "cogs.CommandErrorHandler",
        "cogs.ServerCog",
        "cogs.UserAccountCog",
        "cogs.TenManCog",
        "cogs.TournamentCog",
        "cogs.SquadlockeCog"
    ]

    bot = Goldbot(command_prefix=Config.get_config_property("prefix"))

    for cog in cogs:
        bot.load_extension(cog)

    bot.run(Config.get_config_property("discordApiKey"), bot=True, reconnect=True)


if __name__ == '__main__':
    main()

