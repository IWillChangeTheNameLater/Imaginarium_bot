from . import gameplay


def get_players():
    return gameplay.players


def get_players_score():
    if len(gameplay.players) == 2:
        return (('Players score', gameplay.GameCondition.players_score),
                ('Bot score', gameplay.GameCondition.bot_score))
    else:
        return [(player, player.score) for player in gameplay.players]


def get_used_cards():
    return gameplay.used_cards


def get_used_sources():
    return gameplay.used_sources
