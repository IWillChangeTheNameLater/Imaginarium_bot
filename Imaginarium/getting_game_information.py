from typing import MutableSequence, Iterable, Tuple

from . import sources
from . import gameplay


def get_players() -> MutableSequence[gameplay.Player]:
	return gameplay.players


def get_players_score() -> Iterable[Tuple[str, float]]:
	"""Returns a list of tuples with player name and score."""
	if len(gameplay.players) == 2:
		return (('Players score', gameplay.GameCondition._players_score),
		        ('Bot score', gameplay.GameCondition._bot_score))
	else:
		return ((str(player), player.score) for player in gameplay.players)


def get_used_cards() -> MutableSequence[str]:
	return gameplay.used_cards


def get_used_sources() -> MutableSequence[sources.BaseSource]:
	return gameplay.used_sources
