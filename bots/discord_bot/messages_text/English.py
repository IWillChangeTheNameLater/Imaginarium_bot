from typing import Iterable

import Imaginarium
from Imaginarium.gameplay import GameCondition


# Gameplay
##############################################################################
def game_has_started() -> str:
	return 'The game has started. '


def round_has_started(number: int = None) -> str:
	if number is None:
		number = GameCondition._round_number

	return f'The round {number} has started.'


def inform_association() -> str:
	return 'Did you tell the association of the round? ' \
	       'Write it below  or confirm it by pressing the button.'


def round_association(association: str = None) -> str:
	if association is None:
		association = GameCondition._round_association

	return f'The association of the round is: ' \
	       f'{association}.'


def choose_card(cards: Iterable[str]) -> str:
	cards = '\n'.join(card for card in cards)

	return f'Choose the card you want to... Choose?..: \n{cards}'


def choose_first_card() -> str:
	return 'Choose the first card you want to... choose?.. \n'


def choose_second_card() -> str:
	return 'Choose the second card you want to... choose?.. \n'


def your_chosen_card(card: str) -> str:
	return f'You has chosen the card {card}'


def card_selected_automatically(card: str) -> str:
	return f'You was thinking too much. The card {card} was automatically selected for you.'


def choose_your_leaders_card(cards: Iterable[str] = None) -> str:
	if cards is None:
		if GameCondition._leader is not None:
			cards = GameCondition._leader.cards

	cards = '\n'.join(card for card in cards)

	return f'You are a leader now. Choose number of one of your cards: \n {cards}'


def choose_enemy_card(cards: Iterable[str] = None) -> str:
	if cards is None:
		cards = (card[0] for card in GameCondition._discarded_cards)

	cards = '\n'.join(card for card in cards)

	return f'Choose the enemy\'s card: \n{cards}'


def game_took_time(took: float = None) -> str:
	if took is None:
		if GameCondition._game_took_time is None:
			took = 0
		else:
			took = GameCondition._game_took_time

	return f'The game took: {int(took // 60)} minutes and {int(took % 60)} seconds.'


def loss_score(score: float = None) -> str:
	if score is None:
		score = GameCondition._players_score

	return f'You lose with score: {score}!'


def win_score(score: float = None) -> str:
	if score is None:
		score = GameCondition._players_score

	return f'You win with score: {score}!'


def draw_score() -> str:
	return f'Победила дружба (сырок)!'


def winning_rating(rating: str = None) -> str:
	if rating is None:
		rating = '\n'.join(f'{place}. {player}' for place, player in
		                   enumerate(sorted(Imaginarium.gameplay.players)[:3], start=1))

	return f'The winners: \n{rating}'


def you_already_joined() -> str:
	return 'You have already joined the game.'


def player_joined(player: Imaginarium.gameplay.Player | str) -> str:
	return f'Player {player} has joined the game.'


def you_cannot_join_now() -> str:
	return 'You cannot join right now, the game is started.'


def you_already_left() -> str:
	return 'You have already left the game.'


def player_left(player: Imaginarium.gameplay.Player | str) -> str:
	return f'Player {player} has left the game.'


def you_cannot_leave_now() -> str:
	return 'You cannot leave the game now, it is started.'


def game_already_started() -> str:
	return 'The game is already started.'


def game_cannot_start_game_now() -> str:
	return 'The game cannot start yet. Specify all data and start the game again.'


def game_will_end() -> str:
	return 'The game will be ended as soon as possible.'


def game_already_ended() -> str:
	return 'The game is already ended.'


def no_any_used_sources() -> str:
	return 'Sources are not specified.'


def not_enough_players() -> str:
	return 'There are not enough players to start.'


##############################################################################


# Getting game information
##############################################################################
def help_guidance() -> str:
	return 'Godspeed. \n *Useful information*'


def players_list(players: Iterable[Imaginarium.gameplay.Player] = None) -> str:
	if players is None:
		players = Imaginarium.getting_game_information.get_players()

	players = '\n'.join(str(player) for player in players)

	return f'Players: \n{players}'


def no_any_players() -> str:
	return 'There are no any players.'


def players_score(score: str = None) -> str:
	if score is None:
		score = '\n'.join(f'{ps[0]}: {ps[1]}' for ps in
		                  Imaginarium.getting_game_information.get_players_score())

	return f'Players score: \n{score}'


def used_cards_list(used_cards: Iterable[str] = None) -> str:
	if used_cards is None:
		used_cards = '\n'.join(str(used_card) for used_card in
		                       Imaginarium.getting_game_information.get_used_cards())

	return f'Used cards: \n{used_cards}'


def no_any_used_cards() -> str:
	return 'There are no any used cards.'


def used_sources_list(sources: Iterable = None) -> str:
	if sources is None:
		sources = '\n'.join(str(used_source) for used_source in
		                    Imaginarium.getting_game_information.get_used_sources())

	return f'Used sources: \n{sources}'


def no_any_sources() -> str:
	return 'There are no any sources.'


##############################################################################


# Listeners
##############################################################################
def bot_ready() -> str:
	return 'The discord bot is ready.'


def command_does_not_exist(command_prefix: str) -> str:
	return f'The command does not exist. Write "{command_prefix}help" to get available commands.'


##############################################################################


# Setting up game
##############################################################################
def filetype_is_not_supported(filetype: str) -> str:
	return f'The "{filetype}" filetype is not supported'


def score_must_be_number() -> str:
	return 'The score is supposed to be a number.'


def step_timeout_must_be_number() -> str:
	return 'The step timeout is supposed to be a number.'


def used_cards_successfully_reset() -> str:
	return 'Used cards are successfully reset.'


def sources_successfully_reset() -> str:
	return 'Sources are successfully reset.'


def wrong_source(source: str) -> str:
	return f'There is something wrong with the source: \n{source}'


def no_source(source: str) -> str:
	return f'There is no the source: \n{source}'


def current_following_order(following_order: Iterable[Imaginarium.gameplay.Player] = None) -> str:
	if following_order is None:
		following_order = Imaginarium.getting_game_information.get_players()

	following_order = '\n'.join(str(player) for player in following_order)

	return f'Now you walk in the following order: \n{following_order}'


def you_cannot_shuffle_players_now() -> str:
	return 'You cannot shuffle players now, the game is started.'
##############################################################################
