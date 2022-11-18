import random

from . import exceptions
from . import gameplay
from . import rules_setup


def set_winning_score(score):
    rules_setup.winning_score = score


def set_step_minutes(minutes):
    rules_setup.step_timeout = minutes * 60


def reset_used_cares():
    gameplay.used_sources = set()


def reset_used_sources():
    gameplay.used_sources = set()


def add_used_source(source):
    gameplay.used_sources.add(gameplay.create_source_object(source))


def remove_used_source(source):
    if not gameplay.GameCondition.game_started:
        gameplay.used_sources.remove(source)
    else:
        raise exceptions.GameIsStarted


def shuffle_players_order():
    random.shuffle(gameplay.players)
