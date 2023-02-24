import os
import importlib.util
from types import ModuleType
from functools import wraps
import inspect
from typing import Iterable, TypeAlias, Any, Callable

import Imaginarium
from Imaginarium.gameplay import GameCondition


def import_module(module_name: str,
                  module_directory: str = os.path.dirname(__file__)) -> ModuleType:
	"""Import module from the specified directory and execute it to make it usable.

	:param module_name: Name of the module to import.

	:param module_directory: Directory where the module is located.

	:return: The imported usable module."""
	module_full_path = module_directory + os.sep + module_name + ".py"
	spec = importlib.util.spec_from_file_location(module_name, module_full_path)
	module = importlib.util.module_from_spec(spec)
	# Execute the module to make it usable
	spec.loader.exec_module(module)

	return module


# The languages are specified in "ISO 639-1" encoding
language_modules_map: dict[str, ModuleType] = {
	'en': import_module('English'),
	'ru': import_module('Russian'),
	'uk': import_module('Ukrainian'),
}
default_language = 'en'

Arguments: TypeAlias = tuple[tuple, dict[str, Any]]


def translate_decorator(preprocessing_func: Callable[[...], Arguments]) \
		-> Callable[[...], str]:
	"""Find equivalent message function.

	Replace the decorated function with function that
	returns the equivalent message function and executes it.


	:param preprocessing_func: Function that processes the arguments and
	returns a tuple of arguments
	(a tuple of positional arguments and a dictionary of keyword arguments)
	to pass them to the message function.

	:return: The decorated function that processes the arguments of the function
	by the decorated preprocessing function,
	tries to find the function with the same name in the language module or
	in the default language module,
	and returns the result of the found function with the processed arguments.

	:raise ValueError: If the decorated function does not have a
	language keyword argument.
	:raise AttributeError: If the function with the same name is not found
	either in the language module or in the default language module.

	::note: The decorated function must have a language keyword argument."""
	language_arg_name = 'message_language'

	@wraps(preprocessing_func)
	def inner(*args, **kwargs) -> str:
		language = None
		try:  # to extract the language from the passed or default keyword arguments.
			language = kwargs.pop(language_arg_name)
		except KeyError:
			for name, param in inspect.signature(preprocessing_func).parameters.items():
				if param.default != inspect.Parameter.empty:
					if name == language_arg_name:
						language = param.default
						break
			else:
				raise ValueError(
					f'The decorated function must have a '
					f'passed "{language_arg_name}" keyword argument or '
					f'a default "{language_arg_name}" keyword argument in the function signature.'
				) from None

		# Specify arguments without the language keyword argument.
		args, kwargs = preprocessing_func(*args, **kwargs)

		# Try to find the equivalent function
		try:
			return getattr(language_modules_map[language],
			               preprocessing_func.__name__)(*args, **kwargs)
		except (KeyError, AttributeError):
			# Try to find the default text if it has sense
			if language != default_language:
				return getattr(language_modules_map[default_language],
				               preprocessing_func.__name__)(*args, **kwargs)
			else:
				raise AttributeError(
					'The function with the same name is not found either '
					'in the language module or in the default language module.'
				)

	return inner


# Gameplay
##############################################################################
@translate_decorator
def game_has_started(*, message_language=None):
	return (), {}


@translate_decorator
def round_has_started(number: int = None, *,
                      message_language=None):
	if number is None:
		number = GameCondition._round_number

	return (number,), {}


@translate_decorator
def inform_association(*, message_language=None):
	return (), {}


@translate_decorator
def association_selected_automatically(association, *,
                                       message_language=None):
	return (association,), {}


@translate_decorator
def round_association(association: str = None, *,
                      message_language=None):
	if association is None:
		association = GameCondition._round_association

	return (association,), {}


@translate_decorator
def choose_card(cards: Iterable[str], *,
                message_language=None):
	cards = '\n'.join(card for card in cards)

	return (cards,), {}


@translate_decorator
def choose_first_card(cards: Iterable[str], *,
                      message_language=None):
	cards = '\n'.join(card for card in cards)
	return (cards,), {}


@translate_decorator
def choose_second_card(cards: Iterable[str], *,
                       message_language=None):
	cards = '\n'.join(card for card in cards)
	return (cards,), {}


@translate_decorator
def your_chosen_card(card: str, *,
                     message_language=None):
	return (card,), {}


@translate_decorator
def card_selected_automatically(card: str, *,
                                message_language=None):
	return (card,), {}


@translate_decorator
def choose_your_leaders_card(cards: Iterable[str] = None, *,
                             message_language=None):
	if cards is None:
		if GameCondition._leader is not None:
			cards = GameCondition._leader.cards

	cards = '\n'.join(card for card in cards)

	return (cards,), {}


@translate_decorator
def choose_enemy_card(cards: Iterable[str] = None, *,
                      message_language=None):
	if cards is None:
		cards = (card[0] for card in GameCondition._discarded_cards)

	cards = '\n'.join(card for card in cards)

	return (cards,), {}


@translate_decorator
def game_took_time(took: float = None, *,
                   message_language=None):
	if took is None:
		if GameCondition._game_took_time is None:
			took = 0
		else:
			took = GameCondition._game_took_time

	return (took,), {}


@translate_decorator
def loss_score(score: float = None, *,
               message_language=None):
	if score is None:
		score = GameCondition._players_score

	return (score,), {}


@translate_decorator
def win_score(score: float = None, *,
              message_language=None):
	if score is None:
		score = GameCondition._players_score

	return (score,), {}


@translate_decorator
def draw_score(*, message_language=None):
	return (), {}


@translate_decorator
def winning_rating(rating: str = None, *,
                   message_language=None):
	if rating is None:
		rating = '\n'.join(f'{place}. {player}' for place, player in
		                   enumerate(sorted(Imaginarium.gameplay.players)[:3], start=1))

	return (rating,), {}


@translate_decorator
def you_already_joined(*, message_language=None):
	return (), {}


@translate_decorator
def player_joined(player: Imaginarium.gameplay.Player | str, *,
                  message_language=None):
	return (player,), {}


@translate_decorator
def you_cannot_join_now(*, message_language=None):
	return (), {}


@translate_decorator
def you_already_left(*, message_language=None):
	return (), {}


@translate_decorator
def player_left(player: Imaginarium.gameplay.Player | str, *,
                message_language=None):
	return (player,), {}


@translate_decorator
def you_cannot_leave_now(*, message_language=None):
	return (), {}


@translate_decorator
def game_already_started(*, message_language=None):
	return (), {}


@translate_decorator
def fault_because_game_started(*, message_language=None):
	return (), {}


@translate_decorator
def game_cannot_start_game_now(*, message_language=None):
	return (), {}


@translate_decorator
def game_will_end(*, message_language=None):
	return (), {}


# noinspection DuplicatedCode
@translate_decorator
def game_already_ended(*, message_language=None):
	return (), {}


@translate_decorator
def fault_because_game_ended(*, message_language=None):
	return (), {}


@translate_decorator
def no_any_used_sources(*, message_language=None):
	return (), {}


@translate_decorator
def not_enough_players(*, message_language=None):
	return (), {}


##############################################################################


# Getting game information
##############################################################################
@translate_decorator
def help_guidance(*, message_language=None):
	return (), {}


# noinspection DuplicatedCode
@translate_decorator
def players_list(players: Iterable[Imaginarium.gameplay.Player] = None, *,
                 message_language=None):
	if players is None:
		players = Imaginarium.getting_game_information.get_players()

	players = '\n'.join(str(player) for player in players)

	return (players,), {}


@translate_decorator
def no_any_players(*, message_language=None):
	return (), {}


@translate_decorator
def players_score(score: str = None, *,
                  message_language=None):
	if score is None:
		score = '\n'.join(f'{ps[0]}: {ps[1]}' for ps in
		                  Imaginarium.getting_game_information.get_players_score())

	return (score,), {}


@translate_decorator
def used_cards_list(used_cards: Iterable[str] = None, *,
                    message_language=None):
	if used_cards is None:
		used_cards = '\n'.join(str(used_card) for used_card in
		                       Imaginarium.getting_game_information.get_used_cards())

	return (used_cards,), {}


@translate_decorator
def no_any_used_cards(*, message_language=None):
	return (), {}


@translate_decorator
def used_sources_list(sources: Iterable = None, *,
                      message_language=None):
	if sources is None:
		sources = '\n'.join(str(used_source) for used_source in
		                    Imaginarium.getting_game_information.get_used_sources())

	return (sources,), {}


# noinspection DuplicatedCode
@translate_decorator
def no_any_sources(*, message_language=None):
	return (), {}


##############################################################################


# Listeners
##############################################################################
@translate_decorator
def bot_ready(*, message_language=None):
	return (), {}


@translate_decorator
def command_does_not_exist(command_prefix: str, *,
                           message_language=None):
	return (command_prefix,), {}


@translate_decorator
def missing_required_argument(argument: str, *,
                              message_language=None):
	return (argument,), {}


##############################################################################


# Setting up game
##############################################################################
@translate_decorator
def filetype_is_not_supported(filetype: str, *,
                              message_language=None):
	return (filetype,), {}


@translate_decorator
def score_must_be_number(*, message_language=None):
	return (), {}


@translate_decorator
def step_timeout_must_be_number(*, message_language=None):
	return (), {}


@translate_decorator
def used_cards_successfully_reset(*, message_language=None):
	return (), {}


@translate_decorator
def sources_successfully_reset(*, message_language=None):
	return (), {}


@translate_decorator
def wrong_source(source: str, *, message_language=None):
	return (source,), {}


@translate_decorator
def no_source(source: str, *, message_language=None):
	return (source,), {}


# noinspection DuplicatedCode
@translate_decorator
def current_following_order(following_order: Iterable[Imaginarium.gameplay.Player] = None, *,
                            message_language=None):
	if following_order is None:
		following_order = Imaginarium.getting_game_information.get_players()

	following_order = '\n'.join(str(player) for player in following_order)

	return (following_order,), {}


@translate_decorator
def you_cannot_shuffle_players_now(*, message_language=None):
	return (), {}


@translate_decorator
def your_language_is_not_set(*, message_language=None):
	return (), {}


@translate_decorator
def language_is_not_supported(language, *,
                              message_language=None):
	return (language,), {}


@translate_decorator
def your_language_is(user_language: str | None = None, *,
                     message_language=None):
	if user_language is None:
		user_language = default_language

	return (user_language,), {}


@translate_decorator
def your_language_reset(*, message_language=None):
	return (), {}


##############################################################################


# Messages components
##############################################################################
@translate_decorator
def confirm(*, message_language=None):
	return (), {}
##############################################################################
