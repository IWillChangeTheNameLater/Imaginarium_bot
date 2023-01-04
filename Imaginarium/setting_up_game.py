import random

from . import sources
from . import exceptions
from . import gameplay
from . import rules_setup


def set_winning_score(score: float) -> None:
	rules_setup.winning_score = score


def set_step_timeout(minutes: float) -> None:
	rules_setup.step_timeout = minutes * 60


def reset_used_cards() -> None:
	gameplay.used_cards = set()


def reset_used_sources() -> None:
	gameplay.used_sources = set()


def add_used_source(source: str) -> None:
	gameplay.used_sources.append(gameplay.create_source_object(source))


def remove_used_source(source: sources.BaseSource) -> None:
	if not gameplay.GameCondition._game_started:
		gameplay.used_sources.remove(source)
	else:
		raise exceptions.GameIsStarted


def shuffle_players_order() -> None:
	random.shuffle(gameplay.players)
