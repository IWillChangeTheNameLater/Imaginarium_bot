# Gameplay
##############################################################################
def game_has_started() -> str:
    return 'Гра почалася.'


def round_has_started(number: int) -> str:
    return f'Раунд {number} почався.'


def inform_association() -> str:
    return 'Ви повідомили асоціацію про раунд? ' \
           'Напишіть її нижче або підтвердити натиснувши кнопку.'


# noinspection DuplicatedCode
def association_selected_automatically(association: str) -> str:
    return f'Ви дуже довго думали. ' \
           f'Асоціація {association} була автоматично обрана для вас.'


def round_association(association: str) -> str:
    return f'Асоціація раунду: {association}'


def choose_card(cards: str) -> str:
    return f'Оберіть карту, яку ви хочете обрати: \n{cards}'


def choose_first_card(cards: str) -> str:
    return f'Оберіть першу карту, яку ви хочете обрати: \n{cards}'


def choose_second_card(cards: str) -> str:
    return f'Оберіть другу карту, яку ви хочете обрати: \n{cards}'


def your_chosen_card(card: str) -> str:
    return f'Ви обрали карту: {card}'


def card_selected_automatically(card: str) -> str:
    return f'Ви дуже довго думали. ' \
           f'Карта {card} була автоматично обрана для вас.'


def choose_your_leaders_card(cards: str) -> str:
    return f'Ви тепер лідер. Оберіть номер однієї з ваших карт: \n {cards}'


def choose_enemy_card(cards: str) -> str:
    return f'Виберіть карту ворога: \n{cards}'


def game_took_time(took: float) -> str:
    return f'Гра тривала: {int(took // 60)} хвилин та {int(took % 60)} секунд.'


def loss_score(score: float) -> str:
    return f'Ви програли з рахунком: {score}! Нуб.'


def win_score(score: float) -> str:
    return f'Переможець, Переможець, Курка, Вечеря! ' \
           f'\nВи виграли з рахунком: {score}!'


def draw_score() -> str:
    return f'Ви не програли! \nАле ви також не виграли...'


def winning_rating(rating: str) -> str:
    return f'Переможці: \n{rating}'


def you_already_joined() -> str:
    return 'Ви вже приєдналися до гри.'


def player_joined(player: str) -> str:
    return f'Гравець {player} приєднався до гри.'


def you_cannot_join_now() -> str:
    return 'Ви не можете приєднатися зараз, гра почалася.'


def you_already_left() -> str:
    return 'Ви вже покинули гру.'


def player_left(player: str) -> str:
    return f'Гравець {player} покинув гру.'


def you_cannot_leave_now() -> str:
    return 'Ви не можете зараз покинути гру, тому що вона вже почалась.'


def game_already_started() -> str:
    return 'Гра вже почалась.'


def fault_because_game_started() -> str:
    return 'Ви не можете зробити це, тому що гра вже почалась.'


def game_cannot_start_game_now() -> str:
    return 'Гра не може початися. Вкажіть всі дані та спробуйте знову.'


def game_will_end() -> str:
    return 'Гра буде завершена якомога швидше.'


def game_already_ended() -> str:
    return 'Гра вже завершена.'


def fault_because_game_ended() -> str:
    return 'Ви не можете зробити це, тому що гра ще не почалась.'


def no_any_used_sources() -> str:
    return 'Джерела не вказані.'


def not_enough_players() -> str:
    return 'Недостатньо гравців для початку.'


##############################################################################


# Getting game information
##############################################################################
def help_guidance() -> str:
    return '*Корисна інформація*'


def players_list(players: str) -> str:
    return f'Гравці: \n{players}'


def no_any_players() -> str:
    return 'Немає жодного гравця.'


def players_score(score: str) -> str:
    return f'Результати гравців: \n{score}'


def used_cards_list(used_cards: str) -> str:
    return f'Використані карти: \n{used_cards}'


def no_any_used_cards() -> str:
    return 'Немає жодної використаної карти.'


def used_sources_list(sources: str) -> str:
    return f'Використані джерела: \n{sources}'


def no_any_sources() -> str:
    return 'Немає жодного джерела.'


##############################################################################


# Listeners
##############################################################################
def bot_ready() -> str:
    return 'Дискорд бот приготувався.'


def command_does_not_exist(command_prefix: str) -> str:
    return f'Команда не існує. Напишіть "{command_prefix}help" щоб отримати доступні команди.'


def missing_required_argument(argument: str) -> str:
    return f"{argument} — це обов'язковий аргумент, який відсутній."


##############################################################################


# Setting up game
##############################################################################
def filetype_is_not_supported(filetype: str) -> str:
    return f'Тип файлу "{filetype}" не підтримується.'


def score_must_be_number() -> str:
    return 'Очки мають бути числом.'


def step_timeout_must_be_number() -> str:
    return 'Таймаут ходу має бути числом.'


def used_cards_successfully_reset() -> str:
    return 'Використані карти успішно скинуті.'


def sources_successfully_reset() -> str:
    return 'Джерела успішно скинуті.'


def wrong_source(source: str) -> str:
    return f'Щось не так з джерелом: \n{source}'


def no_source(source: str) -> str:
    return f'Немає такого джерела: \n{source}'


def current_following_order(following_order: str) -> str:
    return f'Тепер ви йдете в наступному порядку: \n{following_order}'


def you_cannot_shuffle_players_now() -> str:
    return 'Ви не можете перемішати гравців зараз, гра почалася.'


def your_language_is_not_set() -> str:
    return 'Ваша мова не встановлена.'


def language_is_not_supported(language: str) -> str:
    return f'Мова "{language}" не підтримується.'


def your_language_is(language: str) -> str:
    return f'Ваша мова: {language}.'


def your_language_reset() -> str:
    return 'Ваша мова встановлена за замовчуванням.'


##############################################################################


# Messages components
##############################################################################
def confirm() -> str:
    return 'Так!'
##############################################################################
