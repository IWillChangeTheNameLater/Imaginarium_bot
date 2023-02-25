from itertools import repeat
from typing import TypeAlias, Iterable, MutableSequence

from discord import Emoji, PartialEmoji
from discord_components import Button, ButtonStyle

import Imaginarium
from Imaginarium.gameplay import GameCondition
import messages_text as mt

Emoji: TypeAlias = Emoji | PartialEmoji | str

ButtonsComponent: TypeAlias = MutableSequence[MutableSequence[Button]] | \
                              MutableSequence[Button]


def generate_buttons(labels: Iterable[str | int],
                     styles: Iterable[int] = repeat(2),
                     urls: Iterable[str] = repeat(None),
                     disabled: Iterable[bool] = repeat(False),
                     emojis: Iterable[Emoji] = repeat(None)) \
        -> ButtonsComponent:
    """Generate list of lists of DiscordComponents.Button.

    :param labels: Text that will be displayed on the buttons.
    :param styles: Color of the buttons.
    :param urls: URL that will be opened when the buttons are clicked.
    :param disabled: Buttons that will be disabled.
    :param emojis: Emojis that will be displayed on the buttons.

    :return: List of lists of DiscordComponents.Button.

    .. note:: The maximum size of the list is 5x5.
    """
    labels = iter(labels)
    styles = iter(styles)
    urls = iter(urls)
    disabled = iter(disabled)
    emojis = iter(emojis)

    buttons = []
    for i in range(5):
        row = []
        for j in range(5):
            try:
                row.append(Button(label=next(labels),
                                  style=next(styles),
                                  url=next(urls),
                                  disabled=next(disabled),
                                  emoji=next(emojis)))
            except StopIteration:
                if row:
                    buttons.append(row)
                return buttons
        buttons.append(row)
    return buttons


def cards_numbers(cards_count: int) -> ButtonsComponent:
    """Generate list of DiscordComponents.Button with cards
    and its numbers.

    :param cards_count: Number of cards.

    :return: List of lists of DiscordComponents.Button."""
    return generate_buttons(range(1, cards_count + 1))


def confirm_association(message_language=None) -> ButtonsComponent:
    return [Button(style=ButtonStyle.green,
                   label=mt.confirm(message_language=message_language),
                   emoji='✅')]


def players_cards() -> ButtonsComponent:
    """Generate a list of lists of DiscordComponents.Button with
    player's cards he can choose from."""
    return cards_numbers(Imaginarium.rules_setup.cards_one_player_has)


def discarded_cards() -> ButtonsComponent:
    """Generate a list of lists of DiscordComponents.Button with
    discarded cards players can vote for."""
    return cards_numbers(len(GameCondition._discarded_cards))
