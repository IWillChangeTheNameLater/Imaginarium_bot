import collections
import math
import random
import time

import validators

from . import sources
from . import exceptions
from . import rules_setup

used_cards = set()
unused_cards = list()
used_sources = set()
players = list()


class Player:
	def __init__(self, player_id, name):
		self.id = player_id
		self.name = name

		self.cards = list()
		self.discarded_cards = list()

	def __hash__(self): return self.id

	def __repr__(self): return self.name

	def __str__(self): return self.name

	def __eq__(self, x): return self.id == x

	def __ne__(self, x): return self.id != x

	def __gt__(self, x): return self.score > x

	def __lt__(self, x): return self.score < x

	def __ge__(self, x): return self.score >= x

	def __le__(self, x): return self.score <= x

	def reset_features(self):
		self.score = 0

	score = 0
	chosen_card = None


def create_source_object(source):
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
		'The link format is not supported or an unavailable link is specified.')


def get_random_card():
	try:
		return random.choice(list(used_sources)).get_random_card()
	except exceptions.NoAnyPosts:
		return get_random_card()


def join(player):
	if GameCondition.game_started:
		raise exceptions.GameIsStarted
	if player not in players:
		players.append(player)


def leave(player):
	if GameCondition.game_started:
		raise exceptions.GameIsStarted
	if player in players:
		players.remove(player)


class GameCondition:
	"""A class which contains variables
	which contain information about
	the state of the game."""
	leader = None
	circle_number = None
	round_number = None
	discarded_cards = None
	votes_for_card = None
	game_started_at = None
	bot_score = None
	players_score = None
	game_started = None
	round_association = None
	game_took_time = None


def empty_hook_function():
	pass


def start_game(at_start_hook=empty_hook_function,
               at_circle_start_hook=empty_hook_function,
               at_round_start_hook=empty_hook_function,
               request_association_hook=empty_hook_function,
               show_association_hook=empty_hook_function,
               show_players_cards_hook=empty_hook_function,
               request_players_cards_2_hook=empty_hook_function,
               request_leader_card_hook=empty_hook_function,
               request_players_cards_hook=empty_hook_function,
               show_discarded_cards_hook=empty_hook_function,
               vote_for_target_card_2_hook=empty_hook_function,
               vote_for_target_card_hook=empty_hook_function,
               at_round_end_hook=empty_hook_function,
               at_circle_end_hook=empty_hook_function,
               at_end_hook=empty_hook_function):
	if GameCondition.game_started:
		raise exceptions.GameIsStarted('The game is already started.')
	if not used_sources:
		raise exceptions.NoAnyUsedSources('Sources are not specified.')
	if len(players) < 2:
		raise exceptions.NotEnoughPlayers('There are not enough players to start.')

	GameCondition.game_started_at = time.time()
	GameCondition.bot_score = 0
	GameCondition.players_score = 0
	for player in players:
		player.reset_features()
	GameCondition.game_started = True

	at_start_hook()

	GameCondition.circle_number = 1
	while True:
		if not GameCondition.game_started:
			break

		at_circle_start_hook()

		# Hand out cards
		if len(players) >= 3:
			for player in players:
				player.cards = list()
				for i in range(rules_setup.cards_one_player_has - 1):
					player.cards.append(get_random_card())

		GameCondition.round_number = 1
		for GameCondition.leader in players:
			if not GameCondition.game_started:
				break

			at_round_start_hook()

			GameCondition.votes_for_card = collections.defaultdict(int)
			GameCondition.discarded_cards = list()
			GameCondition.round_association = None
			# Add missed cards
			if len(players) == 2:
				for player in players:
					player.cards = [get_random_card() for _ in range(rules_setup.cards_one_player_has)]
			else:
				for player in players:
					player.cards.append(get_random_card())

			# Each player discards cards to the common deck
			if len(players) == 2:
				# Discard the bot's card
				GameCondition.discarded_cards.append((get_random_card(), None))

				request_association_hook()

				show_association_hook()

				show_players_cards_hook()

				request_players_cards_2_hook()

			else:
				if len(players) == 3:
					for i in range(2):
						GameCondition.discarded_cards.append((get_random_card(), None))

				show_players_cards_hook()

				request_leader_card_hook()

				request_association_hook()

				show_association_hook()

				request_players_cards_hook()

			random.shuffle(GameCondition.discarded_cards)

			show_discarded_cards_hook()

			# Each player votes for the target card
			if len(players) == 2:

				vote_for_target_card_2_hook()

			else:

				vote_for_target_card_hook()

			# Scoring
			if len(players) == 2:
				# Count bot's score
				match GameCondition.votes_for_card[None]:
					case 0:
						GameCondition.bot_score += 3
					case 1:
						GameCondition.players_score += 1
						GameCondition.bot_score += 1
					case 2:
						GameCondition.players_score += 2
			else:
				if GameCondition.votes_for_card[GameCondition.leader.id] == 0:
					for player in players:
						player.score += GameCondition.votes_for_card[player.id]
				else:
					if GameCondition.votes_for_card[GameCondition.leader.id] != len(players):
						GameCondition.leader.score += 3
					for player in players:
						if player != GameCondition.leader:
							if GameCondition.discarded_cards[player.chosen_card - 1][1] == GameCondition.leader.id:
								player.score += 3

			at_round_end_hook()

			GameCondition.round_number += 1

		at_circle_end_hook()

		GameCondition.circle_number += 1

		# Check for victory
		if len(players) == 2:
			if max(GameCondition.bot_score, GameCondition.players_score) >= rules_setup.winning_score:
				GameCondition.game_started = False
		else:
			if not all(player.score < rules_setup.winning_score for player in players):
				GameCondition.game_started = False

	GameCondition.game_took_time = time.time() - GameCondition.game_started_at

	at_end_hook()


def end_game():
	if GameCondition.game_started:
		GameCondition.game_started = False
	else:
		raise exceptions.GameIsEnded('The game is already ended.')
