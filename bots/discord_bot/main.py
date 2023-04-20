from os import environ
from pathlib import Path
import sys
from functools import wraps
from typing import (
    Generator,
    Callable
)

from discord import Intents
from discord.ext import commands
from discord_components import DiscordComponents
from dotenv import load_dotenv

# Make the script available both as a script and as a module.
if __name__ == '__main__':
    # Iterate up the directory until the "Imaginarium_bot" folder is found.
    for parent in Path(__file__).parents:
        if parent.name == 'Imaginarium_bot':
            sys.path.append(str(parent))
            break
else:
    sys.path.append(str(Path(__file__).parent.resolve()))

import configuration as config
import messages_text as mt
from messages_text import users_languages as ul

load_dotenv()

# Add directory with cogs to search for
sys.path.append(environ['PATH_TO_DISCORD_COGS_DIRECTORY'])

bot = commands.Bot(command_prefix=config.PREFIX,
                   intents=Intents.all())
bot.remove_command('help')


def get_extensions(cogs_dir: Path | str = None) -> Generator[str, None, None]:
    """Get the names of all available the extensions in the directory.

    :param cogs_dir: The directory with cogs."""
    if cogs_dir is None:
        cogs_dir = environ['PATH_TO_DISCORD_COGS_DIRECTORY']
    cogs_dir = Path(cogs_dir)

    return (filename.stem for filename in cogs_dir.iterdir()
            if filename.stem in config.COGS_NAMES and
            filename.suffix == '.py')


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


@bot.event
async def on_ready():
    DiscordComponents(bot)

    print(mt.bot_ready())


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

    bot.run(environ['DISCORD_BOT_TOKEN'])


if __name__ == '__main__':
    main()
