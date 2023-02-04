# Gameplay
##############################################################################
def game_has_started() -> str:
	return 'Игра началась'


def round_has_started(number: int) -> str:
	return f'{number}-й раунд начался.'


def inform_association() -> str:
	return 'Вы сообщили ассоциацию раунда? ' \
		   'Напишите ее ниже или подтвердите это, нажав на кнопку ниже.'


def round_association(association: str) -> str:
	return f'Ассоциация раунда: {association}.'


def choose_card(cards: str) -> str:
	return f'Выберите карту, которую вы хотите... Выбрать?..: \n{cards}'


def choose_first_card(cards: str) -> str:
	return f'Выберите первую карту, которую вы хотите... Выбрать?..: \n{cards}'


def choose_second_card(cards: str) -> str:
	return f'Выберите вторую карту, которую вы хотите... Выбрать?..: \n{cards}'


def your_chosen_card(card: str) -> str:
	return f'Вы выбрали карту: {card}'


def card_selected_automatically(card: str) -> str:
	return f'Вы — тормоз. Карта {card} была автоматически выбрана за вас.'


def choose_your_leaders_card(cards: str) -> str:
	return f'Теперь вы — ведущий. Выберите номер одной из своих карт: \n {cards}'


def choose_enemy_card(cards: str) -> str:
	return f'Выберите вражескую карту: \n{cards}'


def game_took_time(took: float) -> str:
	return f'Игра длилась: {int(took // 60)} минут и {int(took % 60)} секунд.'


def loss_score(score: float) -> str:
	return f'Вы проиграли со счетом: {score}! Вы — попуск.'


def win_score(score: float) -> str:
	return f'Вы победили со счетом: {score}! Красаучик!'


def draw_score() -> str:
	return f'Победила дружба (сырок)!'


def winning_rating(rating: str) -> str:
	return f'Победители: \n{rating}'


def you_already_joined() -> str:
	return 'Вы уже присоединились к игре.'


def player_joined(player: str) -> str:
	return f'Игрок {player} присоединился к игре.'


def you_cannot_join_now() -> str:
	return 'Сейчас вы не можете присоединиться, игра уже началась.'


def you_already_left() -> str:
	return 'Вы уже покинули игру.'


def player_left(player: str) -> str:
	return f'Игрок {player} покинул игру.'


def you_cannot_leave_now() -> str:
	return 'Сейчас вы не можете покинуть игру, игра уже началась.'


def game_already_started() -> str:
	return 'Игра уже началась.'


def fault_because_game_started() -> str:
	return 'Вы не можете это сделать, так как идет игра.'


def game_cannot_start_game_now() -> str:
	return 'Вы еще не можете начать игру. ' \
		   'Укажите все требуемые параметры и попробуйте начать игру снова.'


def game_will_end() -> str:
	return 'Игра закончится так скоро, как это возможно.'


def game_already_ended() -> str:
	return 'Игра уже завершилась.'


def fault_because_game_ended() -> str:
	return 'Вы не можете это сделать, так как игра не начата.'


def no_any_used_sources() -> str:
	return 'Ресурсы не указаны.'


def not_enough_players() -> str:
	return 'Недостаточно игроков, чтобы начать игру.'


##############################################################################


# Getting game information
##############################################################################
def help_guidance() -> str:
	return 'Бог в помощь!'


def players_list(players: str) -> str:
	return f'Игроки: \n{players}'


def no_any_players() -> str:
	return 'К игре не присоединилось ни одного игрока.'


def players_score(score: str) -> str:
	return f'Счет: \n{score}'


def used_cards_list(used_cards: str) -> str:
	return f'Сброшенные карты: \n{used_cards}'


def no_any_used_cards() -> str:
	return 'Использованных карт нет.'


def used_sources_list(sources: str) -> str:
	return f'Используемые источники: \n{sources}'


def no_any_sources() -> str:
	return 'Источников нет.'


##############################################################################


# Listeners
##############################################################################
def bot_ready() -> str:
	return 'Дискорд бот готов к работе!'


def command_does_not_exist(command_prefix: str) -> str:
	return f'Данная команда не существует. Напишите "{command_prefix}help", чтобы получить помощь.'


##############################################################################


# Setting up game
##############################################################################
def filetype_is_not_supported(filetype: str) -> str:
	return f'Расширение файлов "{filetype}" не поддерживается.'


def score_must_be_number() -> str:
	return 'Счет должен быть числом.'


def step_timeout_must_be_number() -> str:
	return 'Время хода должно быть числом.'


def used_cards_successfully_reset() -> str:
	return 'Сброшенные карты успешно очищены.'


def sources_successfully_reset() -> str:
	return 'Источники успешно очищены.'


def wrong_source(source: str) -> str:
	return f'Что-то не так с этим ресурсом: \n{source}'


def no_source(source: str) -> str:
	return f'Данного ресурса нет: \n{source}'


def current_following_order(following_order: str) -> str:
	return f'Теперь вы ходите в следующем порядке: \n{following_order}'


def you_cannot_shuffle_players_now() -> str:
	return 'Вы не можете перемешать порядок сейчас, игра уже началась.'


def your_language_is_not_set() -> str:
	return 'Ваш язык не указан.'


def your_language_is(language: str) -> str:
	return f'Ваш язык: {language}.'
##############################################################################
