import Imaginarium
from Imaginarium.gameplay import GameCondition


# Gameplay
##############################################################################
def game_has_started():
    return 'The game has started. '


def round_has_started(number=None):
    if number is None:
        number = GameCondition.round_number

    return f'The round {number} has started.'


def inform_association():
    return 'Did you tell the association of the round? ' \
           'Write it below  or confirm it by pressing the button.'


def round_association(association=None):
    if association is None:
        association = GameCondition.round_association

    return f'The association of the round is: ' \
           f'{association}.'


def choose_card(cards):
    cards = '\n'.join(str(card) for card in cards)

    return f'Choose the card you want to... Choose?..: \n{cards}'


def choose_first_card():
    return 'Choose the first card you want to... choose?.. \n'


def choose_second_card():
    return 'Choose the second card you want to... choose?.. \n'


def your_chosen_card(card):
    return f'You has chosen the card {card}'


def card_selected_automatically(card):
    return f'You was thinking too much. The card {card} was automatically selected for you.'


def choose_your_leaders_card(cards=None):
    if cards is None:
        if GameCondition.leader is not None:
            cards = GameCondition.leader.cards

    cards = '\n'.join(str(c) for c in cards)

    return f'You are a leader now. Choose number of one of your cards: \n {cards}'


def choose_enemy_card(cards=None):
    if cards is None:
        if GameCondition.discarded_cards is None:
            cards = ()
        else:
            cards = (card[0] for card in GameCondition.discarded_cards)

    cards = '\n'.join(str(card) for card in cards)

    return f'Choose the enemy\'s card: \n{cards}'


def game_took_time(took=None):
    if took is None:
        if GameCondition.game_took_time is None:
            took = 0
        else:
            took = GameCondition.game_took_time

    return f'The game took: {int(took // 60)} minutes and {int(took % 60)} seconds.'


def loss_score(score=None):
    if score is None:
        score = GameCondition.players_score

    return f'You lose with score: {score}!'


def win_score(score=None):
    if score is None:
        score = GameCondition.players_score

    return f'You win with score: {score}!'


def draw_score():
    return f'Победила дружба (сырок)!'


def winning_rating(rating=None):
    if rating is None:
        rating = '\n'.join((str(place) + '. ' + str(player) for place, player in
                            enumerate(sorted(Imaginarium.gameplay.players)[:3], start=1)))

    return f'The winners: \n{rating}'


def you_already_joined():
    return 'You have already joined the game.'


def player_joined(player):
    return f'Player {player} has joined the game.'


def you_cannot_join_now():
    return 'You can\'t join right now, the game is started.'


def you_already_left():
    return 'You have already left the game.'


def player_left(player):
    return f'Player {player} has left the game.'


def you_cannot_leave_now():
    return 'You can\'t leave the game now, it is started.'


def game_already_started():
    return 'The game is already started.'


def game_cannot_start_game_now():
    return 'The game cannot start yet. Specify all data and start the game again.'


def game_will_end():
    return 'The game will be ended as soon as possible.'


def game_already_ended():
    return 'The game is already ended.'


def no_any_used_sources():
    return 'Sources are not specified.'


def not_enough_players():
    return 'There are not enough players to start.'


##############################################################################


# Getting game information
##############################################################################
def help_guidance():
    return 'Godspeed. \n *Useful information*'


def players_list(players=None):
    if players is None:
        players = Imaginarium.getting_game_information.get_players()

    players = '\n'.join(str(player) for player in players)

    return f'Players: \n{players}'


def no_any_players():
    return 'There are no any players.'


def players_score(score=None):
    if score is None:
        score = '\n'.join(
            str(ps[0]) + ': ' + str(ps[1]) for ps in Imaginarium.getting_game_information.get_players_score())

    return f'Players score: \n{score}'


def used_cards_list(used_cards=None):
    if used_cards is None:
        used_cards = '\n'.join(str(used_card) for used_card in Imaginarium.getting_game_information.get_used_cards())

    return f'Used cards: \n{used_cards}'


def no_any_used_cards():
    return 'There are no any used cards.'


def used_sources_list(sources=None):
    if sources is None:
        sources = '\n'.join(str(used_source) for used_source in Imaginarium.getting_game_information.get_used_sources())

    return f'Used sources: \n{sources}'


def no_any_sources():
    return 'There are no any sources.'


##############################################################################


# Listeners
##############################################################################
def bot_ready():
    return 'The bot is ready.'


def command_does_not_exist(write_for_help):
    return f'The command does not exist. Write "{write_for_help}help" to get available commands.'


##############################################################################


# Setting up game
##############################################################################
def filetype_is_not_supported(filetype):
    return f'The "{filetype}" filetype is not supported'


def score_must_be_number():
    return 'The score is supposed to be a number.'


def step_timeout_must_be_number():
    return 'The step timeout is supposed to be a number.'


def used_cards_successfully_reset():
    return 'Used cards are successfully reset.'


def sources_successfully_reset():
    return 'Sources are successfully reset.'


def wrong_source(source):
    return f'There is something wrong with the source: \n{source}'


def no_source(source):
    return f'There is no the source: \n{source}'


def current_following_order(following_order=None):
    if following_order is None:
        following_order = Imaginarium.getting_game_information.get_players()

    following_order = '\n'.join(
        str(player) for player in Imaginarium.getting_game_information.get_players())

    return f'Now you walk in the following order: \n{following_order}'


def you_cannot_shuffle_players_now():
    return 'You can\'t shuffle players now, the game is started.'
##############################################################################
