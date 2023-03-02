import os
from sys import path
from typing import Generator, Callable
from functools import wraps

# Make the script available both as a script and as a module.
if __name__ == '__main__':
    # Iterate up the directory until the "Imaginarium_bot" folder is found.
    path.append(os.sep.join(y := __file__.split(os.sep) \
        [:__file__.split(os.sep).index('Imaginarium_bot') + 1]))
else:
    path.append(os.path.dirname(__file__))

import nest_asyncio

# The "next_asyncio.apply()" have to be called before "discord" import
# to fix "RuntimeError: This event loop is already running".
nest_asyncio.apply()
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

import configuration as config
import messages_text as mt
from messages_text import users_languages as ul

load_dotenv()

# Add directory with cogs to search for
path.append(os.environ['PATH_TO_DISCORD_COGS_DIRECTORY'])

bot = commands.Bot(command_prefix=config.PREFIX,
                   intents=Intents.all())
bot.remove_command('help')


def get_extensions(cogs_dir: str = None) -> Generator[str, None, None]:
    """Get the names of all available the extensions in the directory.

    :param cogs_dir: The directory with cogs.
    """
    if cogs_dir is None:
        cogs_dir = os.environ['PATH_TO_DISCORD_COGS_DIRECTORY']

    return (filename[:-3] for filename in os.listdir(cogs_dir)
            if all((filename[:-3] in config.COGS_NAMES,
                    filename.endswith('.py'))))


def handle_extension_errors(func: Callable) -> Callable:
    @wraps(func)
    async def inner(ctx, extension):
        try:
            await func(ctx, extension)
        except commands.errors.ExtensionNotFound as e:
            await ctx.author.send(mt.extension_does_not_exist(
                extension=extension,
                available_extensions=get_extensions(),
                message_language=ul[ctx.author]
            ))

    return inner


@bot.command()
@commands.has_role(config.EXTENSIONS_ROLE)
@handle_extension_errors
async def load_extension(ctx, extension):
    bot.load_extension(extension)


@bot.command()
@commands.has_role(config.EXTENSIONS_ROLE)
@handle_extension_errors
async def unload_extension(ctx, extension):
    bot.unload_extension(extension)


@bot.command()
@commands.has_role(config.EXTENSIONS_ROLE)
@handle_extension_errors
async def reload_extension(ctx, extension):
    bot.reload_extension(extension)


@bot.command()
@commands.has_role(config.EXTENSIONS_ROLE)
async def load_extensions(ctx):
    for extension in get_extensions():
        bot.load_extension(extension)


@bot.command()
@commands.has_role(config.EXTENSIONS_ROLE)
async def unload_extensions(ctx):
    for extension in get_extensions():
        bot.unload_extension(extension)


@bot.command()
@commands.has_role(config.EXTENSIONS_ROLE)
async def reload_extensions(ctx):
    for extension in get_extensions():
        bot.reload_extension(extension)


def main():
    for extension in get_extensions():
        bot.load_extension(extension)

    bot.run(os.environ['DISCORD_BOT_TOKEN'])


if __name__ == '__main__':
    main()
