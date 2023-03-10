from random import shuffle

from .gameplay import GameCondition

from . import sources
from . import exceptions
from . import gameplay
from . import rules_setup


def set_winning_score(score: float) -> None:
    """Set score to win the game."""
    rules_setup.winning_score = score


def set_step_timeout(minutes: float) -> None:
    """Set time to make a step."""
    rules_setup.step_timeout = minutes * 60


def reset_used_cards() -> None:
    """Reset cards that were used in the game."""
    GameCondition._used_cards = set()


def reset_used_sources() -> None:
    """Reset sources that are used in the game."""
    GameCondition._used_sources = set()


def add_used_source(source: str) -> None:
    """Add source to sources that are used in the game.

    :raises InvalidSource: If the source is invalid for some reason."""
    source = gameplay.create_source_object(source)
    if source.is_valid():
        GameCondition._used_sources.append(source)


def remove_used_source(source: sources.BaseSource) -> None:
    """Remove source from sources that are used in the game."""
    if not gameplay.GameCondition._game_started:
        GameCondition._used_sources.remove(source)
    else:
        raise exceptions.GameIsStarted()


def shuffle_players_order() -> None:
    if GameCondition._game_started:
        raise exceptions.GameIsStarted()
    else:
        shuffle(GameCondition._players)
