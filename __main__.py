from _global.config import Config
from utilities import misc
from core.goldbot import Goldbot

LOGGER = misc.setup_logging()


def main():
    cogs = ["cogs.{0}cog".format(m) for m in Config.get_config_property("modules")]

    bot = Goldbot(command_prefix=Config.get_config_property("prefix"))

    for cog in cogs:
        bot.load_extension(cog)

    bot.run(Config.get_config_property("discordApiKey"), bot=True, reconnect=True)


if __name__ == '__main__':
    main()

