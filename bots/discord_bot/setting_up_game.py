from typing import Callable, Coroutine

from discord.ext import commands
import chardet

import Imaginarium
import messages_text as mt


def extract_file_extension(filename: str) -> str:
	return filename[filename.rfind('.') + 1:]


async def iterate_sources(ctx: commands.Context,
						  message: str,
						  function: Callable[..., Coroutine]) -> None:
	"""Extract separated by break sources from the file and the message and
	process them by the function.
	:param ctx: The message context.
	:param message: The message with sources.
	:param function: The function to process the sources.
	"""

	async def iterate_lines(lines: str, function: Callable[[str], Coroutine]) -> None:
		"""Iterate over the lines and process them by the function."""
		for source in lines.replace('\r', '').split('\n'):
			await function(source)

	await iterate_lines(message, function)

	for attachment in ctx.message.attachments:
		filetype = extract_file_extension(attachment.filename)

		if filetype == 'txt':
			text = await attachment.read()
			await iterate_lines(text.decode(chardet.detect(text[:1000])['encoding']), function)
		else:
			await ctx.send(mt.filetype_is_not_supported(filetype))


class SettingUpGame(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def set_winning_score(self, ctx, score):
		if score.isdigit():
			Imaginarium.setting_up_game.set_winning_score(int(score))
		else:
			await ctx.author.send(mt.score_must_be_number())

	@commands.command()
	async def set_minutes_for_step(self, ctx, minutes):
		if minutes.isdigit():
			Imaginarium.setting_up_game.set_step_timeout(float(minutes * 60))
		else:
			await ctx.author.send(mt.step_timeout_must_be_number())

	@commands.command()
	async def reset_used_cards(self, ctx):
		Imaginarium.setting_up_game.reset_used_cards()

		await ctx.send(mt.used_cards_successfully_reset())

	@commands.command()
	async def reset_used_sources(self, ctx):
		Imaginarium.setting_up_game.reset_used_sources()

		await ctx.send(mt.sources_successfully_reset())

	@commands.command()
	async def add_used_sources(self, ctx, *, message=''):
		async def move_source(source: str) -> None:
			if source:
				try:
					Imaginarium.setting_up_game.add_used_source(source)
				except Imaginarium.exceptions.UnexpectedSource:
					await ctx.send(mt.wrong_source(source))

		await iterate_sources(ctx, message, move_source)

	@commands.command()
	async def remove_used_sources(self, ctx, *, message=''):
		async def move_source(source: Imaginarium.sources.BaseSource) -> None:
			try:
				Imaginarium.setting_up_game.remove_used_source(source)
			except KeyError:
				await ctx.send(mt.no_source(source._link))

		await iterate_sources(ctx, message, move_source)

	@commands.command()
	async def shuffle_players_order(self, ctx):
		if Imaginarium.getting_game_information.get_players():
			try:
				Imaginarium.setting_up_game.shuffle_players_order()
			except Imaginarium.exceptions.GameIsStarted:
				await ctx.send(mt.you_cannot_shuffle_players_now())
			else:
				await ctx.send(mt.current_following_order())
		else:
			await ctx.send(mt.no_any_players())

	@commands.command()
	async def set_language(self, ctx, language):
		# If the language is a code
		if 2 <= len(language) <= 3:
			if language in mt.languages_maps.languages_codes:
				mt.users_languages[ctx.author] = language
				language = mt.languages_maps.code_language_map[language]
				await ctx.author.send(mt.your_language_is(language))
		else:
			language = language.capitalize()
			if language in mt.languages_maps.languages_names:
				mt.users_languages[ctx.author] = mt.languages_maps.language_code_map[language]
				await ctx.author.send(mt.your_language_is(language))
			else:
				await ctx.author.send(mt.language_is_not_supported(language))

	@commands.command()
	async def reset_language(self, ctx):
		mt.users_languages[ctx.author] = None


def setup(bot):
	bot.add_cog(SettingUpGame(bot))
