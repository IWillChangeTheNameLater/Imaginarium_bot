from discord.ext import commands

import Imaginarium


class GettingGameInformation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_guidance(self, ctx):
        await ctx.author.send('Godspeed.\n'
                              '*Useful information*')

    @commands.command()
    async def get_players(self, ctx):
        if ps := Imaginarium.getting_game_information.get_players():
            await ctx.author.send('Players: \n' + '\n'.join(str(player) for player in ps))
        else:
            await ctx.author.send('There are no any players.')

    @commands.command()
    async def get_players_score(self, ctx):
        if pss := Imaginarium.getting_game_information.get_players_score():
            await ctx.author.send(
                'Players score:\n' + '\n'.join(
                    (str(ps[0]) + ': ' + str(ps[1]) for ps in pss)))
        else:
            await ctx.author.send('There are no any players.')

    @commands.command()
    async def get_used_cards(self, ctx):
        if uc := Imaginarium.getting_game_information.get_used_cards():
            await ctx.author.send('\n'.join(uc))
        else:
            await ctx.author.send('There are no any used cards.')

    @commands.command()
    async def get_used_sources(self, ctx):
        if us := Imaginarium.getting_game_information.get_used_sources():
            await ctx.author.send('Used sources: \n' + '\n'.join(str(source) for source in us))
        else:
            await ctx.author.send('There are no any sources.')


def setup(bot):
    bot.add_cog(GettingGameInformation(bot))
