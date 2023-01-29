import collections
import math
import random
import time
from typing import MutableSequence, Tuple, Mapping, Callable, Any, TypeAlias

import validators

from . import sources
from . import exceptions
from . import rules_setup


class Player:
	"""A player in the game."""

	def __init__(self, player_id: int, name: str = None) -> None:
		"""Create a new player.

		:param player_id: The player's ID.
		:param name: The player's name which can be generated automatically
		if it is not specified."""
		self.id: int = player_id
		self._name = name

		self.cards: MutableSequence[str] = []
		"""The player's cards."""
		self.discarded_cards: MutableSequence[str] = []
		"""The cards the player has discarded during a game."""
		self.score: float = 0
		"""The player's score in a game."""
		self.chosen_card: int | None = None
		"""The card the player has voted for in a round."""

	def __hash__(self) -> int:
		return hash(self.id)

	def __repr__(self) -> str:
		return self.name

	def __str__(self) -> str:
		return self.name

	def __eq__(self, other: Any) -> bool:
		try:
			return self.id == other.id
		except AttributeError:
			return self.id == other

	def __ne__(self, other: Any) -> bool:
		try:
			return self.id != other.id
		except AttributeError:
			return self.id != other

	def __gt__(self, other: Any) -> bool:
		try:
			return self.score > other.score
		except AttributeError:
			return self.score > other

	def __lt__(self, other: Any) -> bool:
		try:
			return self.score < other.score
		except AttributeError:
			return self.score < other

	def __ge__(self, other: Any) -> bool:
		try:
			return self.score >= other.score
		except AttributeError:
			return self.score >= other

	def __le__(self, other: Any) -> bool:
		try:
			return self.score <= other.score
		except AttributeError:
			return self.score <= other

	@property
	def name(self) -> str:
		if self._name is None:
			return f'Player {self.id}'
		else:
			return self._name

	@name.setter
	def name(self, value: str) -> None:
		self._name = value

	@name.deleter
	def name(self) -> None:
		self._name = None

	def reset_state(self) -> None:
		"""Reset the player's state to their default values."""
		self.score = 0


def create_source_object(source: str) -> sources.BaseSource:
	"""Process the link to the source (email, url, etc.)
	and create a BaseSource object that can be used to get cards.

	:param source: A link to the source.
	:returns: A BaseSource object that can be used to get cards."""
	if validators.url(source):
		domain_name = source[source.find('/') + 2:]
		domain_name = domain_name[:domain_name.find('/')]
		domain_name = (domain_name := domain_name.split('.')) \
			[math.ceil(len(domain_name) / 2) - 1]

		match domain_name:
			case 'vk':
				return sources.Vk(source)
			case 'discord':
				pass
			case 'instagram':
				pass
			case 'twitter':
				pass
	elif validators.email(source):
		pass

	raise exceptions.UnexpectedSource(
		'The specified source is unsupported.')


def get_random_card() -> str:
	"""Get a random card from a source in the list of sources.

	:returns: A link to a random card."""
	try:
		return random.choice(used_sources).get_random_card()
	except exceptions.NoAnyPosts:
		return get_random_card()


used_cards: MutableSequence[str] = []
"""The cards that have already been used in the game."""
unused_cards: MutableSequence[str] = []
"""The cards that will be used in the game."""
used_sources: MutableSequence[sources.BaseSource] = []
"""The sources that are used in a game."""
players: MutableSequence[Any] = []
"""The players that are playing."""

player_step_timeout: float = 0
"""The time in seconds that the player has to make a choice."""


class GameCondition:
	"""A class which contains variables
	with information about
	the state of the game."""
	_leader: Any = None
	"""The player who is the leader in the current round."""
	_circle_number: int = None
	_round_number: int = None
	_discarded_cards: MutableSequence[Tuple[str, Player | int | None]] = None
	"""The tuples of cards and the players who discarded them.
	The player is None if the card was discarded by the bot."""
	_votes_for_card: Mapping[Player | int | None, int] = None
	"""The map of players and the number of votes for their cards."""
	_game_started_at: float = None
	_bot_score: float = None
	"""The bot's score in two-person mode."""
	_players_score: float = None
	"""The players' score in two-person mode."""
	_game_started: bool = None
	_round_association: str = None
	_game_took_time: float = None
	_players_count: int = None


EmptyHook: TypeAlias = Callable[[], None]


def empty_hook() -> None:
	"""Do nothing perfectly."""
	pass


# This is already some kind of bullshit
def start_game(
		at_start_hook: EmptyHook = empty_hook,
		at_circle_start_hook: EmptyHook = empty_hook,
		at_round_start_hook: EmptyHook = empty_hook,
		request_association_hook: EmptyHook = empty_hook,
		show_association_hook: EmptyHook = empty_hook,
		show_players_cards_hook: EmptyHook = empty_hook,
		request_players_cards_2_hook: EmptyHook = empty_hook,
		request_leader_card_hook: EmptyHook = empty_hook,
		request_players_cards_hook: EmptyHook = empty_hook,
		show_discarded_cards_hook: EmptyHook = empty_hook,
		vote_for_target_card_2_hook: EmptyHook = empty_hook,
		vote_for_target_card_hook: EmptyHook = empty_hook,
		at_round_end_hook: EmptyHook = empty_hook,
		at_circle_end_hook: EmptyHook = empty_hook,
		at_end_hook: EmptyHook = empty_hook) -> None:
	"""Call the function inside another module to start the game
	with following order and the module's own hooks.

	:param at_start_hook: A hook that is called when the game starts.
	:param at_circle_start_hook: A hook that is called when a circle starts.
	:param at_round_start_hook: A hook that is called when a round starts.
	:param request_association_hook: A hook that is called
	to require the association of the round from a leader.
	:param show_association_hook: A hook that is called
	to show an association
	to players.
	:param show_players_cards_hook: A hook that is called
	to show players their cards.
	:param request_players_cards_2_hook: A hook that is called
	to require players' cards they want to discard
	in two-person mode.
	:param request_leader_card_hook: A hook that is called
	to require a leader's card he wants to discard.
	:param request_players_cards_hook: A hook that is called
	to require players' cards they want to discard.
	:param show_discarded_cards_hook: A hook that is called
	to show discarded cards to players.
	:param vote_for_target_card_2_hook: A hook that is called
	to require a vote for a target card
	in two-person mode.
	:param vote_for_target_card_hook: A hook that is called
	to require a vote for a target card.
	:param at_round_end_hook: A hook that is called when a round ends.
	:param at_circle_end_hook: A hook that is called when a circle ends.
	:param at_end_hook: A hook that is called when the game ends.
	"""
	if GameCondition._game_started:
		raise exceptions.GameIsStarted(
			'The game is already started.')
	if not used_sources:
		raise exceptions.NoAnyUsedSources(
			'Sources are not specified.')
	if len(players) < 2:
		raise exceptions.NotEnoughPlayers(
			'There are not enough players to start.')

	GameCondition._game_started_at = time.time()
	GameCondition._bot_score = 0
	GameCondition._players_score = 0
	players_count = len(players)
	for player in players:
		player.reset_state()
	GameCondition._game_started = True

	at_start_hook()

	GameCondition._circle_number = 0
	# Circle starts
	while True:
		if not GameCondition._game_started:
			break

		GameCondition._circle_number += 1
		# Hand out cards
		if players_count >= 3:
			for player in players:
				# We deal one less card than the player should have,
				# since at the beginning of each round we add one additional card.
				player.cards = [get_random_card()
				                for _ in range(rules_setup.cards_one_player_has)]

		at_circle_start_hook()

		GameCondition._round_number = 0
		# Round starts
		for GameCondition._leader in players:
			if not GameCondition._game_started:
				break

			GameCondition._round_number += 1
			GameCondition._votes_for_card = collections.defaultdict(int)
			GameCondition._discarded_cards = []
			GameCondition._round_association = None
			# Refresh cards
			if players_count == 2:
				for player in players:
					player.cards = [get_random_card()
					                for _ in range(rules_setup.cards_one_player_has)]

			at_round_start_hook()

			# Each player discards cards to the common deck
			if players_count == 2:
				# Discard the bot's card
				GameCondition._discarded_cards.append((get_random_card(), None))

				request_association_hook()

				show_association_hook()

				show_players_cards_hook()

				request_players_cards_2_hook()

			else:
				if players_count == 3:
					for i in range(2):
						GameCondition._discarded_cards.append((get_random_card(), None))

				show_players_cards_hook()

				request_leader_card_hook()

				request_association_hook()

				show_association_hook()

				request_players_cards_hook()

			random.shuffle(GameCondition._discarded_cards)

			show_discarded_cards_hook()

			# Each player votes for the target card
			if players_count == 2:

				vote_for_target_card_2_hook()

			else:

				vote_for_target_card_hook()

			# Scoring
			if players_count == 2:
				# Count bot's score
				match GameCondition._votes_for_card[None]:
					case 0:
						GameCondition._bot_score += 3
					case 1:
						GameCondition._players_score += 1
						GameCondition._bot_score += 1
					case 2:
						GameCondition._players_score += 2
			else:
				if GameCondition._votes_for_card[GameCondition._leader.id] == 0:
					for player in players:
						player.score += GameCondition._votes_for_card[player.id]
				else:
					if GameCondition._votes_for_card[GameCondition._leader.id] != players_count:
						GameCondition._leader.score += 3
					for player in players:
						if player != GameCondition._leader:
							if GameCondition._discarded_cards[player.chosen_card - 1][1] == \
									GameCondition._leader.id:
								player.score += 3

			# Add missed cards
			if players_count >= 3:
				for player in players:
					player.cards.append(get_random_card())

			at_round_end_hook()

		# Check for victory
		if players_count == 2:
			if max(GameCondition._bot_score, GameCondition._players_score) >= \
					rules_setup.winning_score:
				GameCondition._game_started = False
		else:
			if any(player.score >= rules_setup.winning_score for player in players):
				GameCondition._game_started = False

		at_circle_end_hook()

	GameCondition._game_took_time = time.time() - GameCondition._game_started_at

	at_end_hook()


def end_game() -> None:
	"""End the game as soon as possible."""
	if GameCondition._game_started:
		GameCondition._game_started = False
	else:
		raise exceptions.GameIsEnded(
			'The game is already ended.')


def join(player: Player) -> None:
	if GameCondition._game_started:
		raise exceptions.GameIsStarted()
	elif player in players:
		raise exceptions.PlayerAlreadyJoined()
	else:
		players.append(player)


def leave(player: Player) -> None:
	if GameCondition._game_started:
		raise exceptions.GameIsStarted()
	elif player not in players:
		raise exceptions.PlayerAlreadyLeft()
	else:
		players.remove(player)
