from typing import MutableSequence, Iterable, Tuple

from Imaginarium.gameplay import GameCondition
from . import exceptions
from . import sources
from . import gameplay


def get_players() -> MutableSequence[gameplay.Player]:
    return GameCondition._players


def get_players_score() -> Iterable[Tuple[str, float]]:
    """Returns a list of tuples with player name and score."""
    if not GameCondition._game_started:
        raise exceptions.GameIsEnded()

    if GameCondition._players_count == 2:
        return (('Players score', GameCondition._players_score),
                ('Bot score', GameCondition._bot_score))
    else:
        return ((str(player), player.score) for player in GameCondition._players)


def get_used_cards() -> MutableSequence[str]:
    return GameCondition._used_cards


def get_used_sources() -> MutableSequence[sources.BaseSource]:
    return GameCondition._used_sources
