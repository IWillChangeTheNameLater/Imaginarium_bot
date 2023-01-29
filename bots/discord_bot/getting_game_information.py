from discord.ext import commands

import Imaginarium
import messages_text as mt


class GettingGameInformation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='help')
	async def help_guidance(self, ctx):
		await ctx.author.send(mt.help_guidance())

	@commands.command()
	async def get_players(self, ctx):
		if Imaginarium.getting_game_information.get_players():
			await ctx.author.send(mt.players_list())
		else:
			await ctx.author.send(mt.no_any_players())

	@commands.command()
	async def get_players_score(self, ctx):
		if not Imaginarium.gameplay.GameCondition._game_started:
			await ctx.author.send(mt.fault_because_game_ended())
		elif not Imaginarium.getting_game_information.get_players_score():
			await ctx.author.send(mt.no_any_players())
		else:
			await ctx.author.send(mt.players_score())

	@commands.command()
	async def get_used_cards(self, ctx):
		if Imaginarium.getting_game_information.get_used_cards():
			await ctx.author.send(mt.used_cards_list())
		else:
			await ctx.author.send(mt.no_any_used_cards())

	@commands.command()
	async def get_used_sources(self, ctx):
		if Imaginarium.getting_game_information.get_used_sources():
			await ctx.author.send(mt.used_sources_list())
		else:
			await ctx.author.send(mt.no_any_sources())


def setup(bot):
	bot.add_cog(GettingGameInformation(bot))
