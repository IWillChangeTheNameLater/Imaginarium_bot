# Gameplay
##############################################################################
def game_has_started() -> str:
    return 'The game has started.'


def round_has_started(number: int) -> str:
    return f'The round {number} has started.'


def inform_association() -> str:
    return 'Did you tell the association of the round? ' \
           'Write it below  or confirm it by pressing the button.'


# noinspection DuplicatedCode
def association_selected_automatically(association: str) -> str:
    return f'You was thinking too much. ' \
           f'The association {association} was automatically selected for you.'


# noinspection DuplicatedCode
def round_association(association: str) -> str:
    return f'The association of the round is: ' \
           f'{association}'


def choose_card(cards: str) -> str:
    return f'Choose the card you want to... Choose?..: \n{cards}'


def choose_first_card(cards: str) -> str:
    return f'Choose the first card you want to... choose?.. \n{cards}'


def choose_second_card(cards: str) -> str:
    return f'Choose the second card you want to... choose?.. \n{cards}'


def your_chosen_card(card: str) -> str:
    return f'You has chosen the card: {card}'


def card_selected_automatically(card: str) -> str:
    return f'You was thinking too much. ' \
           f'The card {card} was automatically selected for you.'


def choose_your_leaders_card(cards: str) -> str:
    return f'You are a leader now. Choose number of one of your cards: \n {cards}'


def choose_enemy_card(cards: str) -> str:
    return f'Choose the enemy\'s card: \n{cards}'


def game_took_time(took: float) -> str:
    return f'The game took: {int(took // 60)} minutes and {int(took % 60)} seconds.'


def loss_score(score: float) -> str:
    return f'You lose with score: {score}! Noob.'


def win_score(score: float) -> str:
    return f'Winner, Winner, Chicken, Dinner! ' \
           f'\nYou win with score: {score}!'


def draw_score() -> str:
    return f'You did not lose! \nBut you did not win either...'


def winning_rating(rating: str) -> str:
    return f'The winners: \n{rating}'


def you_already_joined() -> str:
    return 'You have already joined the game.'


def player_joined(player: str) -> str:
    return f'Player {player} has joined the game.'


def you_cannot_join_now() -> str:
    return 'You cannot join right now, the game is started.'


def you_already_left() -> str:
    return 'You have already left the game.'


def player_left(player: str) -> str:
    return f'Player {player} has left the game.'


def you_cannot_leave_now() -> str:
    return 'You cannot leave the game now, it is started.'


def game_already_started() -> str:
    return 'The game is already started.'


def fault_because_game_started() -> str:
    return 'You cannot do this because the game is started.'


def game_cannot_start_game_now() -> str:
    return 'The game cannot start yet. Specify all data and start the game again.'


def game_will_end() -> str:
    return 'The game will be ended as soon as possible.'


def game_already_ended() -> str:
    return 'The game is already ended.'


def fault_because_game_ended() -> str:
    return 'You cannot do this because the game is not started.'


def no_any_used_sources() -> str:
    return 'Sources are not specified.'


def not_enough_players() -> str:
    return 'There are not enough players to start.'


##############################################################################


# Getting game information
##############################################################################
def help_guidance() -> str:
    return 'Godspeed. \n *Useful information*'


def players_list(players: str) -> str:
    return f'Players: \n{players}'


def no_any_players() -> str:
    return 'There are no any players.'


def players_score(score: str) -> str:
    return f'Players score: \n{score}'


def used_cards_list(used_cards: str) -> str:
    return f'Used cards: \n{used_cards}'


def no_any_used_cards() -> str:
    return 'There are no any used cards.'


def used_sources_list(sources: str) -> str:
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


def missing_required_argument(argument: str) -> str:
    return f'{argument} is a required argument that is missing.'


##############################################################################


# Main
##############################################################################
def extension_does_not_exist(extension: str, available_extensions: str) -> str:
    return f'The "{extension}" extension does not exist.' \
           f'Try one of the following: \n{available_extensions}'


##############################################################################


# Setting up game
##############################################################################
def filetype_is_not_supported(filetype: str) -> str:
    return f'The "{filetype}" filetype is not supported.'


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


def current_following_order(following_order: str) -> str:
    return f'Now you walk in the following order: \n{following_order}'


def you_cannot_shuffle_players_now() -> str:
    return 'You cannot shuffle players now, the game is started.'


def your_language_is_not_set() -> str:
    return 'Your language is not set.'


def language_is_not_supported(language: str) -> str:
    return f'The language "{language}" is not supported.'


def your_language_is(language: str) -> str:
    return f'Your language is: {language}.'


def your_language_reset() -> str:
    return 'Your language is reset.'


##############################################################################


# Messages components
##############################################################################
def confirm() -> str:
    return 'Yes!'
##############################################################################
