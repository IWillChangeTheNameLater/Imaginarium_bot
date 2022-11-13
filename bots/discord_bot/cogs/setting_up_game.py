import random

from discord.ext import commands
import chardet

import Imaginarium


def extract_file_extension(filename):
    return filename[filename.rfind('.') + 1:]


async def iterate_sources(ctx, message, function):
    """Extract sources from attachments and process them.

    Extract separated by break sources from the file and the message and
    process them by the function."""

    async def iterate_lines(lines):
        for source in lines.replace('\r', '').split('\n'):
            await function(source)

    await iterate_lines(message)

    for attachment in ctx.message.attachments:
        filetype = extract_file_extension(attachment.filename)

        if filetype == 'txt':
            text = await attachment.read()
            await iterate_lines(text.decode(chardet.detect(text[:1000])['encoding']))
        else:
            await ctx.send('The "' + filetype + '" filetype is not supported.')


class SettingUpGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_winning_score(self, ctx, score):
        if score.isdigit():
            Imaginarium.rules_setup.winning_score = int(score)
        else:
            await ctx.author.send('Score is supposed to be a number.')

    @commands.command()
    async def set_step_minutes(self, ctx, minutes):
        if minutes.isdigit():
            Imaginarium.rules_setup.step_timeout = float(minutes) * 60
        else:
            await ctx.author.send('"Score" supposed to be a number.')

    @commands.command()
    async def reset_used_cards(self, ctx):
        Imaginarium.game.used_cards = set()

        await ctx.send('Used cards are reset.')

    @commands.command()
    async def reset_used_sources(self, ctx):
        Imaginarium.game.used_sources = set()

        await ctx.send('Sources are reset.')

    @commands.command()
    async def add_used_sources(self, ctx, *, message=''):
        async def move_source(source):
            if source:
                try:
                    Imaginarium.game.used_sources.add(Imaginarium.game.create_source_object(source))
                except Imaginarium.exceptions.UnexpectedSource:
                    await ctx.send('There is something wrong with source: ' + source)

        await iterate_sources(ctx, message, move_source)

    @commands.command()
    async def remove_used_sources(self, ctx, *, message=''):
        async def move_source(source):
            if source:
                try:
                    Imaginarium.game.used_sources.remove(source)
                except KeyError:
                    await ctx.send('There is no the source: ' + source)

        await iterate_sources(ctx, message, move_source)

    @commands.command()
    async def shuffle_players_order(self, ctx):
        random.shuffle(Imaginarium.game.players)
        if Imaginarium.game.players:
            await ctx.send(
                'Now you walk in the following order: ' + '\n' + '\n'.join(
                    str(player) for player in Imaginarium.game.players))
        else:
            await ctx.send('There are no any players.')


def setup(bot):
    bot.add_cog(SettingUpGame(bot))
