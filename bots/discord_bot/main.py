import os
import sys

import nest_asyncio

# The "next_asyncio.apply()" have to be called before "discord" import
# to fix "RuntimeError: This event loop is already running".
nest_asyncio.apply()
import discord
from discord.ext import commands
import dotenv

import configuration

dotenv.load_dotenv()

# Add directory with cogs to search for
sys.path.append(configuration.PATH_TO_COGS_DIRECTORY)

bot = commands.Bot(command_prefix=configuration.PREFIX,
                   intents=discord.Intents.all())
bot.remove_command('help')


@bot.command()
async def load_extension(ctx, extension):
    bot.load_extension(extension)


@bot.command()
async def unload_extension(ctx, extension):
    bot.unload_extension(extension)


@bot.command()
async def reload_extension(ctx, extension):
    bot.unload_extension(extension)
    bot.load_extension(extension)


def get_extensions():
    return [filename[:-3] for filename in os.listdir(configuration.PATH_TO_COGS_DIRECTORY)
            if all((filename[:-3] in configuration.COGS_NAMES,
                    filename.endswith('.py')))]


@bot.command()
async def load_extensions(ctx):
    for extension in get_extensions():
        bot.load_extension(extension)


@bot.command()
async def unload_extensions(ctx):
    for extension in get_extensions():
        bot.unload_extension(extension)


@bot.command()
async def reload_extensions(ctx):
    for extension in get_extensions():
        bot.unload_extension(extension)
        bot.load_extension(extension)


def main():
    for extension in get_extensions():
        bot.load_extension(extension)

    bot.run(os.environ['DISCORD_BOT_TOKEN'])


if __name__ == '__main__':
    main()
