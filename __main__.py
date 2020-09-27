from _global.config import Config
from utilities import misc
from core.goldbot import Goldbot

LOGGER = misc.setup_logging()


def main():
    cogs = [
        "cogs.commanderrorhandler",
        #"cogs.servercog",
        "cogs.useraccountcog",
        "cogs.tenmancog",
        #"cogs.tournamentcog"
        #"cogs.squadlockecog"
    ]

    bot = Goldbot(command_prefix=Config.get_config_property("prefix"))

    for cog in cogs:
        bot.load_extension(cog)

    bot.run(Config.get_config_property("discordApiKey"), bot=True, reconnect=True)


if __name__ == '__main__':
    main()

