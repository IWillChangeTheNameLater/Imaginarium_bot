from discord.ext import commands

import Imaginarium
from Imaginarium.gameplay import GameCondition
import messages_text as mt
from messages_text import users_languages as ul


class GettingGameInformation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_guidance(self, ctx):
        await ctx.author.send(mt.help_guidance(
            message_language=ul[ctx.author]))

    @commands.command()
    async def get_players(self, ctx):
        if Imaginarium.getting_game_information.get_players():
            await ctx.author.send(mt.players_list(
                message_language=ul[ctx.author]))
        else:
            await ctx.author.send(mt.no_any_players(
                message_language=ul[ctx.author]))

    @commands.command()
    async def get_players_score(self, ctx):
        if not GameCondition._game_started:
            await ctx.author.send(mt.fault_because_game_ended(
                message_language=ul[ctx.author]))
        elif not Imaginarium.getting_game_information.get_players_score():
            await ctx.author.send(mt.no_any_players(
                message_language=ul[ctx.author]))
        else:
            await ctx.author.send(mt.players_score(
                message_language=ul[ctx.author]))

    @commands.command()
    async def get_used_cards(self, ctx):
        if Imaginarium.getting_game_information.get_used_cards():
            await ctx.author.send(mt.used_cards_list(
                message_language=ul[ctx.author]))
        else:
            await ctx.author.send(mt.no_any_used_cards(
                message_language=ul[ctx.author]))

    @commands.command()
    async def get_used_sources(self, ctx):
        if Imaginarium.getting_game_information.get_used_sources():
            await ctx.author.send(mt.used_sources_list(
                message_language=ul[ctx.author]))
        else:
            await ctx.author.send(mt.no_any_sources(
                message_language=ul[ctx.author]))

    @commands.command()
    async def get_language(self, ctx):
        language = mt.users_languages[ctx.author]
        if language:
            await ctx.author.send(mt.your_language_is(
                mt.languages_maps.code_language_map[language],
                message_language=ul[ctx.author]))
        else:
            await ctx.author.send(mt.your_language_is_not_set(
                message_language=ul[ctx.author]))


def setup(bot):
    bot.add_cog(GettingGameInformation(bot))
