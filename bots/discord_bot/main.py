import os
import nest_asyncio

# The "next_asyncio.apply()" have to be called before "discord" import
# to fix "RuntimeError: This event loop is already running".
nest_asyncio.apply()
import discord
from discord.ext import commands
import dotenv

import configuration

dotenv.load_dotenv()

bot = commands.Bot(command_prefix=configuration.PREFIX,
                   intents=discord.Intents.all())
bot.remove_command('help')


@bot.command()
async def load_extension(ctx, extension):
    bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload_extension(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')


@bot.command()
async def reload_extension(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')


def get_extensions():
    return [filename[:-3] for filename in os.listdir(r'.\cogs') if
            filename.endswith('.py') and not filename.startswith('__')]


@bot.command()
async def load_extensions(ctx):
    for extension in get_extensions():
        bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload_extensions(ctx):
    for extension in get_extensions():
        bot.unload_extension(f'cogs.{extension}')


@bot.command()
async def reload_extensions(ctx):
    for extension in get_extensions():
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')


def main():
    for cog in get_extensions():
        bot.load_extension(f'cogs.{cog}')

    bot.run(os.environ['DISCORD_BOT_TOKEN'])


if __name__ == '__main__':
    main()
