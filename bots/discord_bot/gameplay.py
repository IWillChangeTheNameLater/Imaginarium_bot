import asyncio
import random
import itertools
import functools
from typing import TypeAlias, Iterable, MutableSequence, Callable, Any

import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, Interaction

import Imaginarium
from Imaginarium.gameplay import GameCondition
from messages_text import *


class Player(Imaginarium.gameplay.Player):
	def __init__(self, user: discord.Member) -> None:
		super().__init__(user.id, user.mention)

		self.user: discord.Member = user

	async def send(self, *args, **kwargs) -> None:
		await self.user.send(*args, **kwargs)


Emoji: TypeAlias = discord.Emoji | discord.PartialEmoji | str


def generate_buttons(labels: Iterable[str],
                     styles: Iterable[int] = itertools.repeat(2),
                     urls: Iterable[str] = itertools.repeat(None),
                     disabled: Iterable[bool] = itertools.repeat(False),
                     emojis: Iterable[Emoji] = itertools.repeat(None)) \
		-> MutableSequence[MutableSequence[Button]]:
	"""Return generated list of DiscordComponents.Button."""
	labels = iter(labels)
	styles = iter(styles)
	urls = iter(urls)
	disabled = iter(disabled)
	emojis = iter(emojis)

	buttons = []
	for i in range(5):
		row = []
		for j in range(5):
			try:
				row.append(Button(label=next(labels),
				                  style=next(styles),
				                  url=next(urls),
				                  disabled=next(disabled),
				                  emoji=next(emojis)))
			except StopIteration:
				if row:
					buttons.append(row)
				return buttons
		buttons.append(row)
	return buttons


Reaction: TypeAlias = Emoji | discord.Reaction


async def wait_for_reply(recipient: discord.abc.Messageable | Player,
                         message: str = None,
                         reactions: Iterable[Reaction] = (),
                         buttons: Iterable[Iterable[Button]] = None,
                         message_check: Callable[[discord.Message], bool] = None,
                         reaction_check: Callable[[discord.Reaction], bool] = None,
                         button_check: Callable[[Interaction], bool] = None,
                         timeout: float = None,
                         bot: discord.Client = None) -> str:
	if bot is None:
		# noinspection PyUnresolvedReferences
		bot = wait_for_reply.bot
	if timeout is None:
		timeout = Imaginarium.rules_setup.step_timeout

	reply = None

	message = await recipient.send(message, components=buttons)
	for r in reactions:
		await message.add_reaction(r)

	async def wait_for_message():
		nonlocal reply
		reply = (await bot.wait_for('message', check=message_check)).content

	async def wait_for_reaction_add():
		nonlocal reply
		reply = (await bot.wait_for('reaction_add', check=reaction_check))[0].emoji

	async def wait_for_button_click():
		nonlocal reply
		reply = (await bot.wait_for('button_click', check=button_check)).component.label

	pending_tasks = (wait_for_message(),
	                 wait_for_reaction_add(),
	                 wait_for_button_click())
	pending_tasks = (await asyncio.wait(pending_tasks,
	                                    timeout=timeout,
	                                    return_when=asyncio.FIRST_COMPLETED))[1]
	for task in pending_tasks:
		task.cancel()

	if reply:
		return str(reply)

	raise asyncio.TimeoutError


MessageCheck: TypeAlias = Callable[[discord.Message], bool]
ButtonCheck: TypeAlias = Callable[[Interaction], bool]


def not_bot_message_check_decorator(func: MessageCheck) -> MessageCheck:
	@functools.wraps(func)
	def inner(message):
		if not message.author.bot:
			return func(message)
		return False

	return inner


def not_bot_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
	@functools.wraps(func)
	def inner(interaction):
		if not interaction.author.bot:
			return func(interaction)
		return False

	return inner


def digit_message_check_decorator(func: MessageCheck) -> MessageCheck:
	@functools.wraps(func)
	def inner(message):
		if message.content.isdigit():
			return func(message)
		return False

	return inner


def digit_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
	@functools.wraps(func)
	def inner(interaction):
		if interaction.component.label.isdigit():
			return func(interaction)
		return False

	return inner


def in_range_of_cards_message_check_decorator(func: MessageCheck = None,
                                              *,
                                              start: int = 1,
                                              stop: int = None,
                                              step: int = 1) \
		-> MessageCheck | Callable[[], MessageCheck]:
	if func is None:
		return lambda func: in_range_of_cards_message_check_decorator(func,
		                                                              start=start,
		                                                              stop=stop,
		                                                              step=step)

	if stop is None:
		stop = Imaginarium.rules_setup.cards_one_player_has + 1

	@functools.wraps(func)
	def inner(message):
		if int(message.content) in range(start, stop, step):
			return func(message)

		return False

	return inner


def in_range_of_cards_button_check_decorator(func: ButtonCheck = None,
                                             *,
                                             start: int = 1,
                                             stop: int = None,
                                             step: int = 1) \
		-> ButtonCheck | Callable[[], ButtonCheck]:
	if func is None:
		return lambda func: in_range_of_cards_button_check_decorator(func,
		                                                             start=start,
		                                                             stop=stop,
		                                                             step=step)

	if stop is None:
		stop = Imaginarium.rules_setup.cards_one_player_has + 1

	@functools.wraps(func)
	def inner(interaction):
		if int(interaction.component.label) in range(start, stop, step):
			return func(interaction)
		return False

	return inner


def leader_message_check_decorator(func: MessageCheck = None,
                                   *,
                                   leader: Player = None) \
		-> MessageCheck | Callable[[], MessageCheck]:
	if func is None:
		return lambda func: leader_message_check_decorator(func, leader=leader)

	if leader is None:
		leader = GameCondition._leader

	@functools.wraps(func)
	def inner(message):
		if message.author == leader:
			return func(message)
		return False

	return inner


def leader_button_check_decorator(func: ButtonCheck = None,
                                  *,
                                  leader: Player = None) \
		-> ButtonCheck | Callable[[], ButtonCheck]:
	if func is None:
		return lambda func: leader_button_check_decorator(func, leader=leader)

	if leader is None:
		leader = GameCondition._leader

	@functools.wraps(func)
	def inner(interaction):
		if interaction.author.id == leader.id:
			return func(interaction)
		return False

	return inner


def not_leader_message_check_decorator(func: MessageCheck = None,
                                       *,
                                       leader: Player = None) \
		-> MessageCheck | Callable[[], MessageCheck]:
	if func is None:
		return lambda func: not_leader_message_check_decorator(func, leader=leader)

	if leader is None:
		leader = GameCondition._leader

	@functools.wraps(func)
	def inner(message):
		if message.author != leader:
			return func(message)
		return False

	return inner


def not_leader_button_check_decorator(func: ButtonCheck = None,
                                      *,
                                      leader: Player = None):
	if func is None:
		return lambda func: not_leader_button_check_decorator(func, leader=leader)

	if leader is None:
		leader = GameCondition._leader

	@functools.wraps(func)
	def inner(interaction):
		if interaction.author.id != leader.id:
			return func(interaction)
		return False

	return inner


def selected_card_message_check_decorator(func: MessageCheck) -> MessageCheck:
	func = in_range_of_cards_message_check_decorator(func)
	func = digit_message_check_decorator(func)
	func = not_bot_message_check_decorator(func)

	return func


def selected_card_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
	func = in_range_of_cards_button_check_decorator(func)
	func = digit_button_check_decorator(func)
	func = not_bot_button_check_decorator(func)

	return func


def at_start_hook() -> None:
	asyncio.run(Gameplay.start.ctx.channel.send(English.game_has_started()))


def at_round_start_hook() -> None:
	asyncio.run(Gameplay.start.ctx.channel.send(English.round_has_started()))


# noinspection PyTypeChecker
def request_association_hook() -> None:
	@not_bot_message_check_decorator
	@leader_message_check_decorator
	def message_check(message: discord.Message) -> bool:
		return True

	@not_bot_button_check_decorator
	@leader_button_check_decorator
	def button_check(interaction: Any) -> bool:
		return True

	Imaginarium.gameplay.round_association = asyncio.run(wait_for_reply(GameCondition._leader,
	                                                                    message=English.inform_association(),
	                                                                    buttons=[Button(style=ButtonStyle.green,
	                                                                                    label='Yes',
	                                                                                    emoji='✅')],
	                                                                    message_check=message_check,
	                                                                    button_check=button_check))


def show_association_hook() -> None:
	if GameCondition._round_association:
		asyncio.run(Gameplay.start.ctx.channel.send(English.round_association()))


def request_players_cards_2_hook() -> None:
	discarded_card = None

	@selected_card_message_check_decorator
	def message_check(message: discord.Message) -> bool:
		number = int(message.content)

		# Check the number is not equal to the previous discarded card
		if number != discarded_card:
			return True
		return False

	@selected_card_button_check_decorator
	def button_check(interaction: Any) -> bool:
		number = int(interaction.component.label)

		# Check the number is not equal to the previous discarded card
		if number != discarded_card:
			return True
		return False

	for player in Imaginarium.gameplay.players:
		for message in (English.choose_first_card(player.cards),
		                English.choose_second_card(player.cards)):
			try:
				card = int(asyncio.run(wait_for_reply(player,
				                                      message=message,
				                                      message_check=message_check,
				                                      button_check=button_check,
				                                      buttons=generate_buttons(
					                                      range(1,
					                                            Imaginarium.rules_setup.cards_one_player_has + 1)))))
				asyncio.run(player.send(English.your_chosen_card(player.cards[card - 1])))
			except asyncio.TimeoutError:
				card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
				asyncio.run(player.send(English.card_selected_automatically(player.cards[card - 1])))

			GameCondition._discarded_cards.append((player.cards[card - 1], player.id))

			# Set the first discarded card
			discarded_card = card


def request_leader_card_hook() -> None:
	@selected_card_message_check_decorator
	@leader_message_check_decorator
	def message_check(message: discord.Message) -> bool:
		return True

	@selected_card_button_check_decorator
	@leader_button_check_decorator
	def button_check(interaction: Any) -> bool:
		return True

	try:
		card = int(asyncio.run(wait_for_reply(GameCondition._leader,
		                                      message=English.choose_your_leaders_card(),
		                                      message_check=message_check,
		                                      button_check=button_check,
		                                      buttons=generate_buttons(
			                                      range(1,
			                                            Imaginarium.rules_setup.cards_one_player_has + 1)))))
		asyncio.run(GameCondition._leader.send(English.your_chosen_card(GameCondition._leader.cards[
			                                                                card - 1])))
	except asyncio.TimeoutError:
		card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
		asyncio.run(GameCondition._leader.send(
			English.card_selected_automatically(GameCondition._leader.cards[card - 1])))

	GameCondition._discarded_cards.append(
		(GameCondition._leader.cards.pop(card - 1), GameCondition._leader.id))


def request_players_cards_hook() -> None:
	@selected_card_message_check_decorator
	@not_leader_message_check_decorator
	def message_check(message: discord.Message) -> bool:
		return True

	@selected_card_button_check_decorator
	@not_leader_button_check_decorator
	def button_check(interaction: Any) -> bool:
		return True

	for player in Imaginarium.gameplay.players:
		if player != GameCondition._leader:
			try:
				card = int(asyncio.run(wait_for_reply(player,
				                                      message=English.choose_card(player.cards),
				                                      message_check=message_check,
				                                      button_check=button_check,
				                                      buttons=generate_buttons(
					                                      range(1,
					                                            Imaginarium.rules_setup.cards_one_player_has + 1)))))
				asyncio.run(player.send(English.your_chosen_card(player.cards[card - 1])))
			except asyncio.TimeoutError:
				card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
				asyncio.run(player.send(English.card_selected_automatically(player.cards[card - 1])))

			GameCondition._discarded_cards.append((player.cards.pop(card - 1), player.id))


# noinspection DuplicatedCode
def vote_for_target_card_2_hook() -> None:
	@selected_card_message_check_decorator
	def message_check(message: discord.Message) -> bool:
		if GameCondition._discarded_cards[int(message.content) - 1][1] != message.author.id:
			return True
		return False

	@selected_card_button_check_decorator
	def button_check(interaction: Any) -> bool:
		if GameCondition._discarded_cards[int(interaction.component.label) - 1][1] != interaction.user.id:
			return True
		return False

	for player in Imaginarium.gameplay.players:
		try:
			card = int(
				asyncio.run(wait_for_reply(player,
				                           message=English.choose_enemy_card(),
				                           message_check=message_check,
				                           button_check=button_check,
				                           buttons=generate_buttons(
					                           range(1,
					                                 len(GameCondition._discarded_cards) + 1)))))
			asyncio.run(player.send(English.your_chosen_card(GameCondition._discarded_cards[card - 1][0])))
		except asyncio.TimeoutError:
			card = random.randint(1, len(Imaginarium.gameplay.players))
			asyncio.run(player.send(English.card_selected_automatically(GameCondition._discarded_cards[card - 1][0])))

		GameCondition._votes_for_card[
			GameCondition._discarded_cards[card - 1][1]] += 1
		player.chosen_card = card


# noinspection DuplicatedCode
def vote_for_target_card_hook() -> None:
	@selected_card_message_check_decorator
	@not_leader_message_check_decorator
	def message_check(message: discord.Message) -> bool:
		if GameCondition._discarded_cards[int(message.content) - 1][1] != message.author.id:
			return True
		return False

	@selected_card_button_check_decorator
	@not_leader_button_check_decorator
	def button_check(interaction: Any) -> bool:
		if GameCondition._discarded_cards[int(interaction.component.label) - 1][1] != interaction.user.id:
			return True
		return False

	for player in Imaginarium.gameplay.players:
		if player != GameCondition._leader:
			try:
				card = int(
					asyncio.run(wait_for_reply(player,
					                           message=English.choose_enemy_card(),
					                           message_check=message_check,
					                           button_check=button_check,
					                           buttons=generate_buttons(
						                           range(1,
						                                 len(GameCondition._discarded_cards) + 1)))))
				asyncio.run(
					player.send(English.your_chosen_card(GameCondition._discarded_cards[card - 1][
						                                     0])))
			except asyncio.TimeoutError:
				card = random.randint(1, len(Imaginarium.gameplay.players))
				asyncio.run(
					player.send(English.card_selected_automatically(GameCondition._discarded_cards[card - 1][0])))

			GameCondition._votes_for_card[
				GameCondition._discarded_cards[card - 1][1]] += 1
			player.chosen_card = card


def at_end_hook() -> None:
	asyncio.run(Gameplay.start.ctx.send(English.game_took_time()))

	if len(Imaginarium.gameplay.players) == 2:
		if GameCondition._bot_score > GameCondition._players_score:
			asyncio.run(Gameplay.start.ctx.send(English.loss_score()))
		elif GameCondition._bot_score < GameCondition._players_score:
			asyncio.run(Gameplay.start.ctx.send(English.win_score()))
		else:
			asyncio.run(Gameplay.start.ctx.send(English.draw_score()))
	else:
		asyncio.run(Gameplay.start.ctx.send(English.winning_rating()))


class Gameplay(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def join(self, ctx):
		try:
			if ctx.author.id in Imaginarium.gameplay.players:
				await ctx.send(English.you_already_joined())
			else:
				Imaginarium.gameplay.join(Player(ctx.author))

				await ctx.send(English.player_joined(ctx.author.mention))
		except Imaginarium.exceptions.GameIsStarted:
			await ctx.send(English.you_cannot_join_now())

	@commands.command()
	async def leave(self, ctx):
		try:
			if ctx.author.id not in Imaginarium.gameplay.players:
				await ctx.send(English.you_already_left())
			else:
				Imaginarium.gameplay.leave(ctx.author.id)

				await ctx.send(English.player_left(ctx.author.mention))
		except Imaginarium.exceptions.GameIsStarted:
			await ctx.send(English.you_cannot_leave_now())

	@commands.command()
	async def start(self, ctx):
		Gameplay.start.ctx = ctx

		try:
			Imaginarium.gameplay.start_game(at_start_hook=at_start_hook,
			                                at_round_start_hook=at_round_start_hook,
			                                request_association_hook=request_association_hook,
			                                show_association_hook=show_association_hook,
			                                request_players_cards_2_hook=request_players_cards_2_hook,
			                                request_leader_card_hook=request_leader_card_hook,
			                                request_players_cards_hook=request_players_cards_hook,
			                                vote_for_target_card_2_hook=vote_for_target_card_2_hook,
			                                vote_for_target_card_hook=vote_for_target_card_hook,
			                                at_end_hook=at_end_hook)
		except Imaginarium.exceptions.GameIsStarted:
			await ctx.send(English.game_already_started())
		except Imaginarium.exceptions.NoAnyUsedSources:
			await ctx.send(English.no_any_used_sources())
		except Imaginarium.exceptions.NotEnoughPlayers:
			await ctx.send(English.not_enough_players())

	@commands.command()
	async def end(self, ctx):
		try:
			Imaginarium.gameplay.end_game()

			await ctx.send(English.game_will_end())
		except Imaginarium.exceptions.GameIsStarted:
			await ctx.send(English.game_already_ended())


def setup(bot):
	wait_for_reply.bot = bot

	bot.add_cog(Gameplay(bot))
