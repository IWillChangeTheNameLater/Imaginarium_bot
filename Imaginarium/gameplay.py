import asyncio
from collections import defaultdict
from math import ceil
from random import choices, shuffle
from time import time
from typing import (
    MutableSequence,
    Tuple,
    Mapping,
    Any,
    TypeAlias,
    Callable,
    Awaitable,
    AsyncIterable)

import validators

from . import sources
from . import exceptions
from . import rules_setup


class Player:
    """A player in the game."""

    def __init__(self, player_id: int, name: str = None) -> None:
        """Create a new player.

        :param player_id: The player's ID.
        :param name: The player's name which can be generated automatically
        if it is not specified."""
        self.id: int = player_id
        self._name = name

        self.cards: MutableSequence[str] = []
        """The player's cards."""
        self.discarded_cards: MutableSequence[str] = []
        """The cards the player has discarded during a game."""
        self.score: float = 0
        """The player's score in a game."""
        self.chosen_card: int | None = None
        """The card the player has voted for in a round."""

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        try:
            return self.id == other.id
        except AttributeError:
            return self.id == other

    def __ne__(self, other: Any) -> bool:
        try:
            return self.id != other.id
        except AttributeError:
            return self.id != other

    def __gt__(self, other: Any) -> bool:
        try:
            return self.score > other.score
        except AttributeError:
            return self.score > other

    def __lt__(self, other: Any) -> bool:
        try:
            return self.score < other.score
        except AttributeError:
            return self.score < other

    def __ge__(self, other: Any) -> bool:
        try:
            return self.score >= other.score
        except AttributeError:
            return self.score >= other

    def __le__(self, other: Any) -> bool:
        try:
            return self.score <= other.score
        except AttributeError:
            return self.score <= other

    @property
    def name(self) -> str:
        if self._name is None:
            return f'Player {self.id}'
        else:
            return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = None

    def reset_state(self) -> None:
        """Reset the player's state to their default values."""
        self.score = 0


def create_source_object(source: str) -> sources.BaseSource:
    """Process the link to the source (email, url, etc.)
    and create a BaseSource object that can be used to get cards.

    :param source: A link to the source.
    :return: A BaseSource object that can be used to get cards."""
    if validators.url(source):
        domain_name = source[source.find('/') + 2:]
        domain_name = domain_name[:domain_name.find('/')]
        domain_name = domain_name.split('.')
        domain_name = domain_name[ceil(len(domain_name) / 2) - 1]

        match domain_name:
            case 'vk':
                return sources.Vk(source)
            case 'discord':
                pass
            case 'instagram':
                pass
            case 'twitter':
                pass
    elif validators.email(source):
        pass

    raise exceptions.UnsupportedSource(
        'The specified source is unsupported.')


default_source = sources.DefaultSource()


async def get_random_source() -> sources.BaseSource:
    """Get a random source from the list of sources.

    :return: A random source.

    :raise NoAnyUsedSources: If there are no sources in
    the list of sources.

    .. note:: Sources are selected depending on their cards count.
    That is, the more cards a source has, the more often it will be selected
    so that the same cards fall out less often.
    But if the source returns an infinite number
    (that is, the number of cards in it is unlimited),
    then its weight is set as the average weight of all resources."""
    if len(GameCondition._used_sources) == 0:
        raise exceptions.NoAnyUsedSources('There are no sources to use.')
    elif len(GameCondition._used_sources) == 1:
        return GameCondition._used_sources[0]
    else:
        weights = []
        for source in GameCondition._used_sources:
            weight = await source.get_cards_count()
            if weight != float('inf'):
                weights.append(weight)
            else:
                weights_sum = sum(await s.get_cards_count() for s in GameCondition._used_sources)
                weights_count = len(GameCondition._used_sources)
                weights.append(weights_sum / weights_count)

        return choices(population=GameCondition._used_sources,
                       weights=weights)[0]


async def get_random_card(
        timeout: float | None = None,
        raise_timeout_error: bool = False) -> str:
    """Get a random card from a random source in the list of sources.

    Try to get a random card from a random source in a certain amount of time,
    but if it comes out, try to get a card as quickly as possible
    from this random source or the default source.

    :param timeout: The time in seconds for which the card can be received.
    If it is None, then the timeout is rules_setup.cards_receiving.timeout.
    :param raise_timeout_error: If True, then if the card timeout is exceeded,
    the asyncio.TimeoutError exception is raised.

    :return: A link to a random card.
    .. note:: The card will not necessarily be received before the timeout,
    but after the timeout, attempts will begin to get some card
    as soon as possible.

    :raise asyncio.TimeoutError: If the timeout is exceeded."""
    try:
        source = await get_random_source()
    except exceptions.NoAnyUsedSources:
        source = default_source

    try:
        if raise_timeout_error:
            return await asyncio.wait_for(
                asyncio.create_task(source.get_random_card()),
                timeout=timeout)
        # If we do not have to raise the "TimeoutError" exception,
        # then just in case, run both tasks at the same time.
        else:
            source_task = asyncio.create_task(
                source.get_random_card())
            default_source_task = asyncio.create_task(
                default_source.get_random_card())

            done, _ = await asyncio.wait((source_task,), timeout=timeout)

            # If the selected source has been waiting too long,
            # then try to get the result as soon as possible from both sources.
            if not done:
                done, pending = await asyncio.wait(
                    (source_task, default_source_task),
                    return_when=asyncio.FIRST_COMPLETED)
                for task in pending:
                    task.cancel()

            return done.pop().result()
    except exceptions.InvalidSource:
        return await get_random_card()


async def async_generate_random_cards(
        cards_count: int,
        timeout: float | None = None,
        raise_timeout_error: bool = False) -> AsyncIterable[str]:
    """Return an asynchronous iterator with random cards.

    The iterator returns cards received by the get_random_card function.

    :param cards_count: The count of cards that have to be received.
    :param timeout: The time in seconds for which each card can be received.
    If it is None, then the timeout is rules_setup.cards_receiving.timeout.
    :param raise_timeout_error: If True, then if some card timeout is exceeded,
    the asyncio.TimeoutError exception is raised.

    :return: An asynchronous iterator.

    :raise asyncio.TimeoutError: If the timeout is exceeded."""
    tasks = [get_random_card(timeout=timeout,
                             raise_timeout_error=raise_timeout_error)
             for _ in range(cards_count)]
    for future in asyncio.as_completed(tasks):
        yield await future


async def get_random_cards(
        cards_count: int,
        timeout: float | None = None,
        raise_timeout_error: bool = False) -> list[str]:
    """Get random cards from a random source in the list of sources.

    :param cards_count: The count of cards that have to be received.
    :param timeout: The time in seconds for which each card can be received.
    If it is None, then the timeout is rules_setup.cards_receiving.timeout.
    :param raise_timeout_error: If True, then if some card timeout is exceeded,
    the asyncio.TimeoutError exception is raised.

    :return: Links to random cards.

    :raise asyncio.TimeoutError: If the timeout is exceeded."""
    return [f async for f in
            async_generate_random_cards(
                cards_count,
                timeout=timeout,
                raise_timeout_error=raise_timeout_error)]


class GameCondition:
    """Contains variables with information about the state of the game.

    :param _leader: The player who is the leader in the current round.
    :param _circle_num: The number of the current circle.
    :param _round_num: The number of the current round.
    :param _discarded_cards: The tuples of cards and
    the players who discarded them.
    The player is None if the card was discarded by the bot.
    :param _votes_for_card: The map of players and
    the number of votes for their cards.
    :param _game_started_at: The moment at which the game was started.
    :param _bot_score: The bot's score in two-person mode.
    :param _players_score: The players' score in two-person mode.
    :param _game_started: Whether the game has started.
    :param _round_association: The association of the current round,
    which is set by the leader.
    :param _game_took_time: The time that the game lasted.
    :param _players_count: The count of players in the game.
    :param _used_cards: The cards that have already been used in the game.
    :param _unused_cards: The cards that will be used in the game.
    :param _used_sources: The sources that are used in a game.
    :param _players: The players that are playing."""
    _leader: Any = None
    _circle_num: int = None
    _round_num: int = None
    _discarded_cards: MutableSequence[Tuple[str, Player | int | None]] = None
    _votes_for_card: Mapping[Player | int | None, int] = None
    _game_started_at: float = None
    _bot_score: float = None
    _players_score: float = None
    _game_started: bool = None
    _round_association: str = None
    _game_took_time: float = None
    _players_count: int = None
    _used_cards: MutableSequence[str] = []
    _unused_cards: MutableSequence[str] = []
    _used_sources: MutableSequence[sources.BaseSource] = []
    _players: MutableSequence[Any] = []


AsyncEmptyHook: TypeAlias = Callable[[], Awaitable[None]]


async def async_empty_hook() -> None:
    """Do nothing perfectly."""
    pass


# This is already some kind of bullshit
async def start_game(
        at_start_hook: AsyncEmptyHook = async_empty_hook,
        at_circle_start_hook: AsyncEmptyHook = async_empty_hook,
        at_round_start_hook: AsyncEmptyHook = async_empty_hook,
        request_association_hook: AsyncEmptyHook = async_empty_hook,
        show_association_hook: AsyncEmptyHook = async_empty_hook,
        show_players_cards_hook: AsyncEmptyHook = async_empty_hook,
        request_players_cards_2_hook: AsyncEmptyHook = async_empty_hook,
        request_leader_card_hook: AsyncEmptyHook = async_empty_hook,
        request_players_cards_hook: AsyncEmptyHook = async_empty_hook,
        show_discarded_cards_hook: AsyncEmptyHook = async_empty_hook,
        vote_for_target_card_2_hook: AsyncEmptyHook = async_empty_hook,
        vote_for_target_card_hook: AsyncEmptyHook = async_empty_hook,
        at_round_end_hook: AsyncEmptyHook = async_empty_hook,
        at_circle_end_hook: AsyncEmptyHook = async_empty_hook,
        at_end_hook: AsyncEmptyHook = async_empty_hook) -> None:
    """Call the function inside another module to start the game
    with following order and the module's own hooks.

    :param at_start_hook: A hook that is called when the game starts.
    :param at_circle_start_hook: A hook that is called when a circle starts.
    :param at_round_start_hook: A hook that is called when a round starts.
    :param request_association_hook: A hook that is called
    to require the association of the round from a leader.
    :param show_association_hook: A hook that is called
    to show an association
    to players.
    :param show_players_cards_hook: A hook that is called
    to show players their cards.
    :param request_players_cards_2_hook: A hook that is called
    to require players' cards they want to discard
    in two-person mode.
    :param request_leader_card_hook: A hook that is called
    to require a leader's card he wants to discard.
    :param request_players_cards_hook: A hook that is called
    to require players' cards they want to discard.
    :param show_discarded_cards_hook: A hook that is called
    to show discarded cards to players.
    :param vote_for_target_card_2_hook: A hook that is called
    to require a vote for a target card
    in two-person mode.
    :param vote_for_target_card_hook: A hook that is called
    to require a vote for a target card.
    :param at_round_end_hook: A hook that is called when a round ends.
    :param at_circle_end_hook: A hook that is called when a circle ends.
    :param at_end_hook: A hook that is called when the game ends.
    """
    if GameCondition._game_started:
        raise exceptions.GameIsStarted(
            'The game is already started.')
    GameCondition._players_count = len(GameCondition._players)
    if GameCondition._players_count < 2:
        raise exceptions.NotEnoughPlayers(
            'There are not enough players to start.')

    GameCondition._game_started_at = time()
    GameCondition._bot_score = 0
    GameCondition._players_score = 0
    for player in GameCondition._players:
        player.reset_state()
    GameCondition._game_started = True

    await at_start_hook()

    GameCondition._circle_num = 0
    # Circle starts
    while True:
        if not GameCondition._game_started:
            break

        GameCondition._circle_num += 1
        # Hand out cards
        if GameCondition._players_count >= 3:
            cards = await get_random_cards(rules_setup.cards_per_player *
                                           GameCondition._players_count)
            for i, player in enumerate(GameCondition._players):
                player.cards = cards[i * rules_setup.cards_per_player:
                                     (i + 1) * rules_setup.cards_per_player]

        await at_circle_start_hook()

        GameCondition._round_num = 0
        # Round starts
        for GameCondition._leader in GameCondition._players:
            if not GameCondition._game_started:
                break

            GameCondition._round_num += 1
            GameCondition._votes_for_card = defaultdict(int)
            GameCondition._discarded_cards = []
            GameCondition._round_association = None
            # Refresh cards
            if GameCondition._players_count == 2:
                cards = await get_random_cards(rules_setup.cards_per_player *
                                               GameCondition._players_count)
                for i, player in enumerate(GameCondition._players):
                    player.cards = cards[i * rules_setup.cards_per_player:
                                         (i + 1) * rules_setup.cards_per_player]

            await at_round_start_hook()

            # Each player discards cards to the common deck
            if GameCondition._players_count == 2:
                # Discard the bot's card
                GameCondition._discarded_cards.append((await get_random_card(), None))

                await request_association_hook()

                await show_association_hook()

                await show_players_cards_hook()

                await request_players_cards_2_hook()

            else:
                if GameCondition._players_count == 3:
                    for card in await get_random_cards(2):
                        GameCondition._discarded_cards.append((card, None))

                await show_players_cards_hook()

                await request_leader_card_hook()

                await request_association_hook()

                await show_association_hook()

                await request_players_cards_hook()

            shuffle(GameCondition._discarded_cards)

            await show_discarded_cards_hook()

            # Each player votes for the target card
            if GameCondition._players_count == 2:
                await vote_for_target_card_2_hook()

            else:
                await vote_for_target_card_hook()

            # Scoring
            if GameCondition._players_count == 2:
                # Count bot's score
                # noinspection PyTypeChecker
                match GameCondition._votes_for_card[None]:
                    case 0:
                        GameCondition._bot_score += 3
                    case 1:
                        GameCondition._players_score += 1
                        GameCondition._bot_score += 1
                    case 2:
                        GameCondition._players_score += 2
            else:
                if GameCondition._votes_for_card[GameCondition._leader.id] == 0:
                    for player in GameCondition._players:
                        player.score += GameCondition._votes_for_card[player.id]
                else:
                    if GameCondition._votes_for_card[GameCondition._leader.id] != GameCondition._players_count:
                        GameCondition._leader.score += 3
                    for player in GameCondition._players:
                        if player != GameCondition._leader:
                            if GameCondition._discarded_cards[player.chosen_card - 1][1] == \
                                    GameCondition._leader.id:
                                player.score += 3

            # Add missed cards
            if GameCondition._players_count >= 3:
                for player, card in zip(
                        GameCondition._players,
                        await get_random_cards(GameCondition._players_count)):
                    player.cards.append(card)

            await at_round_end_hook()

        # Check for victory
        if GameCondition._players_count == 2:
            if max(GameCondition._bot_score, GameCondition._players_score) >= \
                    rules_setup.winning_score:
                GameCondition._game_started = False
        else:
            if any(player.score >= rules_setup.winning_score
                   for player in GameCondition._players):
                GameCondition._game_started = False

        await at_circle_end_hook()

    GameCondition._game_took_time = time() - GameCondition._game_started_at

    await at_end_hook()


def end_game() -> None:
    """End the game as soon as possible."""
    if GameCondition._game_started:
        GameCondition._game_started = False
    else:
        raise exceptions.GameIsEnded(
            'The game is already ended.')


def join(player: Player) -> None:
    if GameCondition._game_started:
        raise exceptions.GameIsStarted
    elif player in GameCondition._players:
        raise exceptions.PlayerAlreadyJoined
    else:
        GameCondition._players.append(player)


def leave(player: Player) -> None:
    if GameCondition._game_started:
        raise exceptions.GameIsStarted
    elif player not in GameCondition._players:
        raise exceptions.PlayerAlreadyLeft
    else:
        GameCondition._players.remove(player)
