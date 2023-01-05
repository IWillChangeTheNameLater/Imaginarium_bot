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
	def __init__(self, player_id: int, name: str = None) -> None:
		self.id: int = player_id
		if name is None:
			self.name: str = f'Player {self.id}'
		else:
			self.name: str = name

		self.cards: MutableSequence[str] = []
		self.discarded_cards: MutableSequence[str] = []
		self.score: float = 0
		self.chosen_card: int | None = None

	def __hash__(self) -> int:
		return hash(self.id)

	def __repr__(self) -> str:
		return self.name

	def __str__(self) -> str:
		return self.name

	def __eq__(self, other: Any) -> bool:
		# return self.id == other
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

	def reset_features(self) -> None:
		self.score = 0


def create_source_object(source: str) -> sources.BaseSource:
	"""Return an object of class "Source".

	Process the link to the source (email, url, etc.) and create a "Source"
	object that can be used to get some cards."""
	if validators.url(source):
		domain_name = source[source.find('/') + 2:]
		domain_name = domain_name[:domain_name.find('/')]
		domain_name = (domain_name := domain_name.split('.'))[math.ceil(len(domain_name) / 2) - 1]

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
	try:
		return random.choice(used_sources).get_random_card()
	except exceptions.NoAnyPosts:
		return get_random_card()


used_cards: MutableSequence[str] = []
unused_cards: MutableSequence[str] = []
used_sources: MutableSequence[sources.BaseSource] = []
players: MutableSequence[Any] = []

players_score: float = 0
player_step_timeout: float = 0


class GameCondition:
	"""A class which contains variables
	with information about
	the state of the game."""
	_leader: Any = None
	_circle_number: int = None
	_round_number: int = None
	_discarded_cards: MutableSequence[Tuple[str, Player | int | None]] = None
	_votes_for_card: Mapping[Player | int | None, int] = None
	_game_started_at: float = None
	_bot_score: float = None
	_players_score: float = None
	_game_started: bool = None
	_round_association: str = None
	_game_took_time: float = None
	_players_count: int = None


EmptyHook: TypeAlias = Callable[[], None]


def empty_hook() -> None:
	pass


# This is already some kind of bullshit
def start_game(at_start_hook: EmptyHook = empty_hook,
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
		player.reset_features()
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
				player.cards = [get_random_card() for _ in range(rules_setup.cards_one_player_has)]

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
					player.cards = [get_random_card() for _ in range(rules_setup.cards_one_player_has)]

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
							if GameCondition._discarded_cards[player.chosen_card - 1][1] == GameCondition._leader.id:
								player.score += 3

			# Add missed cards
			if players_count >= 3:
				for player in players:
					player.cards.append(get_random_card())

			at_round_end_hook()

		# Check for victory
		if players_count == 2:
			if max(GameCondition._bot_score, GameCondition._players_score) >= rules_setup.winning_score:
				GameCondition._game_started = False
		else:
			if any(player.score >= rules_setup.winning_score for player in players):
				GameCondition._game_started = False

		at_circle_end_hook()

	GameCondition._game_took_time = time.time() - GameCondition._game_started_at

	at_end_hook()


def end_game() -> None:
	if GameCondition._game_started:
		GameCondition._game_started = False
	else:
		raise exceptions.GameIsEnded(
			'The game is already ended.')


def join(player: Player) -> None:
	if GameCondition._game_started:
		raise exceptions.GameIsStarted
	if player not in players:
		players.append(player)


def leave(player: Player) -> None:
	if GameCondition._game_started:
		raise exceptions.GameIsStarted
	if player in players:
		players.remove(player)
