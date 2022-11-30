from discord.ext import commands
import chardet

import Imaginarium
from messages_text import *


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
			await ctx.send(English.filetype_is_not_supported(filetype))


class SettingUpGame(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def set_winning_score(self, ctx, score):
		if score.isdigit():
			Imaginarium.setting_up_game.set_winning_score(int(score))
		else:
			await ctx.author.send(English.score_must_be_number())

	@commands.command()
	async def set_minutes_for_step(self, ctx, minutes):
		if minutes.isdigit():
			Imaginarium.setting_up_game.set_step_timeout(float(minutes * 60))
		else:
			await ctx.author.send(English.step_timeout_must_be_number())

	@commands.command()
	async def reset_used_cards(self, ctx):
		Imaginarium.setting_up_game.reset_used_cards()

		await ctx.send(English.used_cards_successfully_reset())

	@commands.command()
	async def reset_used_sources(self, ctx):
		Imaginarium.setting_up_game.reset_used_sources()

		await ctx.send(English.sources_successfully_reset())

	@commands.command()
	async def add_used_sources(self, ctx, *, message=''):
		async def move_source(source):
			if source:
				try:
					Imaginarium.setting_up_game.add_used_source(source)
				except Imaginarium.exceptions.UnexpectedSource:
					await ctx.send(English.wrong_source(source))

		await iterate_sources(ctx, message, move_source)

	@commands.command()
	async def remove_used_sources(self, ctx, *, message=''):
		async def move_source(source):
			try:
				Imaginarium.setting_up_game.remove_used_source(source)
			except KeyError:
				await ctx.send(English.no_source(source))

		await iterate_sources(ctx, message, move_source)

	@commands.command()
	async def shuffle_players_order(self, ctx):
		try:
			if Imaginarium.getting_game_information.get_players():
				Imaginarium.setting_up_game.shuffle_players_order()
				await ctx.send(English.current_following_order())
			else:
				await ctx.send(English.no_any_players())
		except Imaginarium.exceptions.GameIsStarted:
			await ctx.send(English.you_cannot_shuffle_players_now())


def setup(bot):
	bot.add_cog(SettingUpGame(bot))
