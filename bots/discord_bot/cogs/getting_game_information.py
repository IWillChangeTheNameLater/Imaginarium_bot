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
        if Imaginarium.game.players:
            await ctx.author.send('Players: \n' + '\n'.join(str(player) for player in Imaginarium.game.players))
        else:
            await ctx.author.send('There are no any players.')

    @commands.command()
    async def get_players_score(self, ctx):
        if Imaginarium.game.players:
            await ctx.author.send(
                'Players score:\n' + '\n'.join(
                    (str(player) + ': ' + str(player.score) for player in Imaginarium.game.players)))
        else:
            await ctx.author.send('There are no any players.')

    @commands.command()
    async def get_used_cards(self, ctx):
        await ctx.author.send('\n'.join(Imaginarium.game.used_cards))

    @commands.command()
    async def get_used_sources(self, ctx):
        if Imaginarium.game.used_sources:
            await ctx.author.send('\n'.join(str(source) for source in Imaginarium.game.used_sources))
        else:
            await ctx.author.send('There are no any sources here yet.')


def setup(bot):
    bot.add_cog(GettingGameInformation(bot))
