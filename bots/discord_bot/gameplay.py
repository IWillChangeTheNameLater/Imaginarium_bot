import asyncio
from functools import wraps, partial
from io import BytesIO
from random import randrange, randint
from typing import (
    TypeAlias,
    Iterable,
    Callable,
    Any
)

import discord
import discord_components
from aiohttp import ClientSession
from discord.ext import commands

import Imaginarium
import messages_components as mc
import messages_text as mt
from Imaginarium.gameplay import GameCondition
from messages_text import users_languages as ul


class Player(Imaginarium.gameplay.Player, discord.abc.User):
    """Class that inherits from "Imaginarium.gameplay.Player"
    and is used to work with players in discord bot."""

    def __init__(self, user: discord.Member) -> None:
        """Initialize the player.

        :param user: Discord member that is the player."""
        super().__init__(user.id, user.mention)

        self._user = user

        self._preferred_language: str | None = None
        """The locale specified by the user, 
        which does not depend on his locale in the settings."""

    def __hash__(self) -> int:
        return hash(self._user)

    @property
    def display_name(self):
        return self._user.display_name

    @property
    def mention(self):
        return self._user.mention

    @property
    def name(self) -> str:
        return self._user.mention

    @property
    def language(self) -> str | None:
        if self._preferred_language is None:
            try:
                return self._user.locale
            except AttributeError:
                return None
        else:
            return self._preferred_language

    @language.setter
    def language(self, value: str | None) -> None:
        self._preferred_language = value

    @language.deleter
    def language(self) -> None:
        self._preferred_language = None

    async def send(self, *args, **kwargs) -> discord.Message:
        """Send a message to the member that is the player."""
        return await self._user.send(*args, **kwargs)


DiscordReply: TypeAlias = (discord.Message |
                           discord.Reaction |
                           discord_components.Interaction)


class Reply:
    """Represents the user's response that was given to the request
    using some kind of interaction (message, reaction or button).

    :raises AttributeError: If the init argument
    is not one of the supported replies.

    .. note:: The 'text' argument contains different information
    for each reply type:
    message — content,
    reaction — emoji,
    discord components interaction — the component's label."""

    def __init__(self, discord_reply: DiscordReply) -> None:
        self.discord_reply: DiscordReply = discord_reply
        self.text: str = ''
        match discord_reply:
            case discord.Message():
                self.text = self.discord_reply.content
            case discord.Reaction():
                self.text = self.discord_reply.emoji
            case discord_components.Interaction():
                self.text = self.discord_reply.component.label
            case _:
                raise AttributeError(
                    f'The "reply" argument is an unknown type. '
                    f'It must be one of the following: '
                    f'discord.Message, discord.Reaction, discord_components.Interaction')

    def __repr__(self):
        return self.discord_reply.__repr__()

    def __str__(self):
        return self.text

    def __int__(self):
        return int(self.text)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.discord_reply == other.discord_reply
        else:
            return self.text == other

    def __ne__(self, other):
        if isinstance(other, type(self)):
            return self.discord_reply != other.discord_reply
        else:
            return self.text != other


ReactionAlias: TypeAlias = (discord.Reaction |
                            discord.Emoji |
                            discord.PartialEmoji |
                            str)


async def wait_for_reply(
        recipient: discord.abc.Messageable | Player,
        message_text: str = None,
        reactions: Iterable[ReactionAlias] = (),
        buttons: Iterable[Iterable[discord_components.Button]] = None,
        message_check: Callable[[discord.Message], bool] = None,
        reaction_check: Callable[[discord.Reaction], bool] = None,
        button_check: Callable[[discord_components.Interaction], bool] = None,
        timeout: float = None,
        bot: discord.Client = None) -> Reply:
    """Wait for a reply from the recipient.

    Send a message to the recipient and wait for a correct reply
    with a message, reaction or button until time is up.

    :param recipient: Discord member or channel that will receive the message.
    :param message_text: Text that will be sent to the recipient.
    :param reactions: Reactions that will be added to the message.
    :param buttons: Buttons that will be added to the message.
    :param message_check: Function that checks if the message is correct.
    :param reaction_check: Function that checks if the reaction is correct.
    :param button_check: Function that checks if the button is correct.
    :param timeout: Time in seconds after which the function will
    raise asyncio.TimeoutError.
    :param bot: Discord client that will be used to wait for a reply.

    :return: Text of the message, label of the button or
    emoji of the reaction.

    :raise asyncio.TimeoutError: If the time is up and
    no correct reply was received.

    .. note:: This function waits for messages only in the recipient context.
    That is, if the message was sent to the channel,
    then only messages from the same channel will be expected,
    and if the message was sent directly to the user,
    then messages in a private channel with this user will be expected."""
    if bot is None:
        # noinspection PyUnresolvedReferences
        bot = wait_for_reply.bot
    if timeout is None:
        timeout = Imaginarium.rules_setup.step_timeout

    sent_message = await recipient.send(message_text, components=buttons)
    for reaction in reactions:
        await sent_message.add_reaction(reaction)

    def wrapped_message_check(message: discord.Message) -> bool:
        return True if all((
            sent_message.channel == message.channel,
            message_check(message))) else False

    def wrapped_reaction_check(reaction: discord.Reaction) -> bool:
        return True if all((
            sent_message.channel == reaction.message.channel,
            reaction_check(reaction))) else False

    def wrapped_button_check(button: discord_components.Interaction) -> bool:
        return True if all((
            sent_message.channel == button.message.channel,
            button_check(button))) else False

    async def wait_for_message():
        return await bot.wait_for(event='message',
                                  check=wrapped_message_check)

    async def wait_for_reaction_add():
        return (await bot.wait_for(event='reaction_add',
                                   check=wrapped_reaction_check))[0]

    async def wait_for_button_click():
        return await bot.wait_for(event='button_click',
                                  check=wrapped_button_check)

    tasks = (
        wait_for_message(),
        wait_for_reaction_add(),
        wait_for_button_click())
    tasks = [asyncio.create_task(c) for c in tasks]
    done, pending = await asyncio.wait(
        tasks,
        timeout=timeout,
        return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()

    if done:
        return Reply(done.pop().result())
    else:
        raise asyncio.TimeoutError(
            'Time is up and no correct reply was received.'
        )


async def discord_file_from_url(url: str) -> discord.File:
    """Create a discord.File from an url."""
    async with ClientSession() as session:
        async with session.get(url) as response:
            img = await response.read()
            with BytesIO(img) as file:
                filename = url[url.rfind('/'):]
                if filename.rfind('?') != -1:
                    filename = filename[:filename.rfind('?')]

                return discord.File(file, filename)


async def discord_files_from_urls(urls: Iterable) -> list[discord.File]:
    """Apply the discord_file_from_url function on the Iterable."""
    # noinspection PyTypeChecker
    return await asyncio.gather(*(discord_file_from_url(url) for url in urls))


def try_until(action: Callable[[], Any], check: Callable[[Any], bool]):
    """Execute the action until its result passes check.

    :param action: A function which returns the result to be checked.
    :param check: A predicate that checks the result for correctness."""
    while True:
        result = action()
        if check(result):
            return result


MessageCheck: TypeAlias = Callable[[discord.Message], bool]
ButtonCheck: TypeAlias = Callable[[discord_components.Interaction], bool]


def not_bot_message_check_decorator(func: MessageCheck) -> MessageCheck:
    """Decorator that checks if the message author is not a bot."""

    @wraps(func)
    def inner(message):
        if not message.author.bot:
            return func(message)
        return False

    return inner


def not_bot_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
    """Decorator that checks if the button author is not a bot."""

    @wraps(func)
    def inner(interaction):
        if not interaction.author.bot:
            return func(interaction)
        return False

    return inner


def digit_message_check_decorator(func: MessageCheck) -> MessageCheck:
    """Decorator that checks if the message content is a digit."""

    @wraps(func)
    def inner(message):
        if message.content.isdigit():
            return func(message)
        return False

    return inner


def digit_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
    """Decorator that checks if the button label is a digit."""

    @wraps(func)
    def inner(interaction):
        if interaction.component.label.isdigit():
            return func(interaction)
        return False

    return inner


def in_range_of_cards_message_check_decorator(func: MessageCheck = None,
                                              *,
                                              start: int = 1,
                                              stop: int = None,
                                              step: int = 1) \
        -> MessageCheck | Callable[[], MessageCheck]:
    """Decorator that checks if the message content is a digit
    that is in range of cards count."""
    if func is None:
        return lambda func: in_range_of_cards_message_check_decorator(
            func,
            start=start,
            stop=stop,
            step=step)

    if stop is None:
        stop = Imaginarium.rules_setup.cards_per_player + 1

    @wraps(func)
    def inner(message):
        if int(message.content) in range(start, stop, step):
            return func(message)

        return False

    return inner


def in_range_of_cards_button_check_decorator(func: ButtonCheck = None,
                                             *,
                                             start: int = 1,
                                             stop: int = None,
                                             step: int = 1) \
        -> ButtonCheck | Callable[[], ButtonCheck]:
    """Decorator that checks if the button label is a digit
    that is in range of cards count."""
    if func is None:
        return lambda func: in_range_of_cards_button_check_decorator(func,
                                                                     start=start,
                                                                     stop=stop,
                                                                     step=step)

    if stop is None:
        stop = Imaginarium.rules_setup.cards_per_player + 1

    @wraps(func)
    def inner(interaction):
        if int(interaction.component.label) in range(start, stop, step):
            return func(interaction)
        return False

    return inner


def leader_message_check_decorator(func: MessageCheck = None,
                                   *,
                                   leader: Player = None) \
        -> MessageCheck | Callable[[], MessageCheck]:
    """Decorator that checks if the message author is the leader."""
    if func is None:
        return lambda func: leader_message_check_decorator(func,
                                                           leader=leader)

    if leader is None:
        leader = GameCondition._leader

    @wraps(func)
    def inner(message):
        if message.author == leader:
            return func(message)
        return False

    return inner


def leader_button_check_decorator(func: ButtonCheck = None,
                                  *,
                                  leader: Player = None) \
        -> ButtonCheck | Callable[[], ButtonCheck]:
    """Decorator that checks if the button author is the leader."""
    if func is None:
        return lambda func: leader_button_check_decorator(func,
                                                          leader=leader)

    if leader is None:
        leader = GameCondition._leader

    @wraps(func)
    def inner(interaction):
        if interaction.author == leader:
            return func(interaction)
        return False

    return inner


def not_leader_message_check_decorator(func: MessageCheck = None,
                                       *,
                                       leader: Player = None) \
        -> MessageCheck | Callable[[], MessageCheck]:
    """Decorator that checks if the message author is not the leader."""
    if func is None:
        return lambda func: not_leader_message_check_decorator(func,
                                                               leader=leader)

    if leader is None:
        leader = GameCondition._leader

    @wraps(func)
    def inner(message):
        if message.author != leader:
            return func(message)
        return False

    return inner


def not_leader_button_check_decorator(func: ButtonCheck = None,
                                      *,
                                      leader: Player = None):
    """Decorator that checks if the button author is not the leader."""
    if func is None:
        return lambda func: not_leader_button_check_decorator(func,
                                                              leader=leader)

    if leader is None:
        leader = GameCondition._leader

    @wraps(func)
    def inner(interaction):
        if interaction.author.id != leader.id:
            return func(interaction)
        return False

    return inner


def selected_card_message_check_decorator(func: MessageCheck) -> MessageCheck:
    """Decorator that checks if the message content can be interpreted
    as a selected card."""
    func = in_range_of_cards_message_check_decorator(func)
    func = digit_message_check_decorator(func)
    func = not_bot_message_check_decorator(func)

    return func


def selected_card_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
    """Decorator that checks if the button label can be interpreted
    as a selected card."""
    func = in_range_of_cards_button_check_decorator(func)
    func = digit_button_check_decorator(func)
    func = not_bot_button_check_decorator(func)

    return func


async def at_start_hook():
    """Send a message to the channel that the game has started."""
    await Gameplay.start.ctx.send(mt.game_has_started())


async def at_round_start_hook():
    """Send a message to the channel that the round has started."""
    await Gameplay.start.ctx.send(mt.round_has_started())


# noinspection PyTypeChecker
async def request_association_hook():
    """Do not continue the game until the association is specified."""

    @not_bot_message_check_decorator
    @leader_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        return True

    @not_bot_button_check_decorator
    @leader_button_check_decorator
    def button_check(message: discord_components.Interaction) -> bool:
        return True

    try:
        association = \
            await wait_for_reply(
                recipient=GameCondition._leader,
                message_text=mt.inform_association(message_language=ul[GameCondition._leader]),
                buttons=mc.confirm_association(message_language=ul[GameCondition._leader]),
                message_check=message_check,
                button_check=button_check)
        if isinstance(association.discord_reply, discord_components.Interaction):
            association = r'¯\_(ツ)_/¯'
    except asyncio.TimeoutError:
        association = r'¯\_(ツ)_/¯'

        await GameCondition._leader.send(
            mt.association_selected_automatically(
                association=association,
                message_language=ul[GameCondition._leader])
        )

    GameCondition._round_association = association


async def show_association_hook():
    """Send the association to the channel."""
    if GameCondition._round_association:
        await Gameplay.start.ctx.send(mt.round_association())


async def request_players_cards_2_hook():
    """Request each player to choose 2 cards to discard in two-player mode
    or choose the cards automatically if the player's time is up."""
    # Remember discarded card to not allow the player to choose it again.
    discarded_card = None

    @selected_card_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        num = int(message.content)

        # Check the number is not equal to the previous discarded card
        if num != discarded_card:
            return True
        return False

    @selected_card_button_check_decorator
    def button_check(interaction: discord_components.Interaction) -> bool:
        num = int(interaction.component.label)

        # Check the number is not equal to the previous discarded card
        if num != discarded_card:
            return True
        return False

    async def request_card_from_one_player(player):
        nonlocal discarded_card

        for message in (
                mt.choose_first_card(
                    player.cards,
                    message_language=ul[player]),
                mt.choose_second_card(
                    player.cards,
                    message_language=ul[player])):
            try:
                card = int(await wait_for_reply(
                    recipient=player,
                    message_text=message,
                    message_check=message_check,
                    button_check=button_check,
                    buttons=mc.players_cards()))
            except asyncio.TimeoutError:
                card = try_until(
                    partial(randrange, Imaginarium.rules_setup.cards_per_player),
                    lambda num: num != discarded_card)
                await player.send(
                    mt.card_selected_automatically(
                        player.cards[card - 1],
                        message_language=ul[player]))
            else:
                await player.send(mt.your_chosen_card(
                    player.cards[card - 1],
                    message_language=ul[player]))

            GameCondition._discarded_cards.append((player.cards[card - 1],
                                                   player.id))

            # Set the first discarded card
            discarded_card = card

    tasks = []
    for player in GameCondition._players:
        tasks.append(request_card_from_one_player(player))

    await asyncio.gather(*tasks)


async def request_leader_card_hook():
    """Request the leader to choose a card to discard."""

    @selected_card_message_check_decorator
    @leader_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        return True

    @selected_card_button_check_decorator
    @leader_button_check_decorator
    def button_check(interaction: discord_components.Interaction) -> bool:
        return True

    try:
        card = int(await wait_for_reply(
            recipient=GameCondition._leader,
            message_text=mt.choose_your_leaders_card(
                message_language=ul[GameCondition._leader]),
            message_check=message_check,
            button_check=button_check,
            buttons=mc.players_cards()))
    except asyncio.TimeoutError:
        card = randrange(Imaginarium.rules_setup.cards_per_player)
        await GameCondition._leader.send(
            mt.card_selected_automatically(
                GameCondition._leader.cards[card - 1],
                message_language=ul[GameCondition._leader]))
    else:
        await GameCondition._leader.send(mt.your_chosen_card(
            GameCondition._leader.cards[card - 1],
            message_language=ul[GameCondition._leader]))

    GameCondition._discarded_cards.append(
        (GameCondition._leader.cards.pop(card - 1),
         GameCondition._leader.id))


async def request_players_cards_hook():
    """Request each player except the leader to choose a card to discard
    or choose the card automatically if the player's time is up."""

    @selected_card_message_check_decorator
    @not_leader_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        return True

    @selected_card_button_check_decorator
    @not_leader_button_check_decorator
    def button_check(message: discord.Message) -> bool:
        return True

    async def request_cards_from_one_player(player):
        try:
            card = int(await wait_for_reply(
                recipient=player,
                message_text=mt.choose_card(
                    player.cards,
                    message_language=ul[player]),
                message_check=message_check,
                button_check=button_check,
                buttons=mc.players_cards()))
        except asyncio.TimeoutError:
            card = randrange(Imaginarium.rules_setup.cards_per_player)
            await player.send(
                mt.card_selected_automatically(
                    player.cards[card - 1],
                    message_language=ul[player]))
        else:
            await player.send(mt.your_chosen_card(
                player.cards[card - 1],
                message_language=ul[player]))

        GameCondition._discarded_cards.append((player.cards.pop(card - 1),
                                               player.id))

    tasks = []
    for player in GameCondition._players:
        if player != GameCondition._leader:
            tasks.append(request_cards_from_one_player(player))

    await asyncio.gather(*tasks)


def select_target_card_automatically(player: Player) -> int:
    """Select a card that was not discarded by the player himself."""
    return try_until(
        partial(randint, 1, GameCondition._players_count),
        lambda num: GameCondition._discarded_cards[num - 1][1] != player.id)


# noinspection DuplicatedCode
async def vote_for_target_card_2_hook():
    """Request each player to vote for the bot's card in two-player mode."""

    @selected_card_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        if GameCondition._discarded_cards[int(message.content) - 1][1] != \
                message.author.id:
            return True
        return False

    @selected_card_button_check_decorator
    def button_check(interaction: discord_components.Interaction) -> bool:
        if GameCondition._discarded_cards[int(interaction.component.label) - 1][1] != \
                interaction.user.id:
            return True
        return False

    async def one_player_vote_for_target_card(player):
        try:
            card = int(
                await wait_for_reply(
                    recipient=player,
                    message_text=mt.choose_enemy_card(
                        message_language=ul[player]),
                    message_check=message_check,
                    button_check=button_check,
                    buttons=mc.discarded_cards()))
        except asyncio.TimeoutError:
            card = select_target_card_automatically(player)
            await player.send(
                mt.card_selected_automatically(
                    GameCondition._discarded_cards[card - 1][0],
                    message_language=ul[player]))
        else:
            await player.send(mt.your_chosen_card(
                GameCondition._discarded_cards[card - 1][0],
                message_language=ul[player]))

        GameCondition._votes_for_card[
            GameCondition._discarded_cards[card - 1][1]] += 1

        player.chosen_card = card

    tasks = []
    for player in GameCondition._players:
        tasks.append(one_player_vote_for_target_card(player))

    await asyncio.gather(*tasks)


# noinspection DuplicatedCode
async def vote_for_target_card_hook():
    """Request each player to vote for the leader's card."""

    @selected_card_message_check_decorator
    @not_leader_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        if GameCondition._discarded_cards[int(message.content) - 1][1] != \
                message.author.id:
            return True
        return False

    @selected_card_button_check_decorator
    @not_leader_button_check_decorator
    def button_check(interaction: discord_components.Interaction) -> bool:
        if GameCondition._discarded_cards[int(interaction.component.label) - 1][1] != \
                interaction.user.id:
            return True
        return False

    async def one_player_vote_for_target_card(player):
        try:
            card = int(await wait_for_reply(
                recipient=player,
                message_text=mt.choose_enemy_card(
                    message_language=ul[player]),
                message_check=message_check,
                button_check=button_check,
                buttons=mc.discarded_cards()))
        except asyncio.TimeoutError:
            card = select_target_card_automatically(player)
            await player.send(
                mt.card_selected_automatically(
                    GameCondition._discarded_cards[card - 1][0],
                    message_language=ul[player]))
        else:
            await player.send(mt.your_chosen_card(
                GameCondition._discarded_cards[card - 1][0],
                message_language=ul[player]))

        GameCondition._votes_for_card[
            GameCondition._discarded_cards[card - 1][1]] += 1

        player.chosen_card = card

    tasks = []
    for player in GameCondition._players:
        if player != GameCondition._leader:
            tasks.append(one_player_vote_for_target_card(player))

    await asyncio.gather(*tasks)


async def at_end_hook():
    """Announce the results of the game."""
    await Gameplay.start.ctx.send(mt.game_took_time())

    if GameCondition._players_count == 2:
        if GameCondition._bot_score > GameCondition._players_score:
            await Gameplay.start.ctx.send(mt.loss_score())
        elif GameCondition._bot_score < GameCondition._players_score:
            await Gameplay.start.ctx.send(mt.win_score())
        else:
            await Gameplay.start.ctx.send(mt.draw_score())
    else:
        await Gameplay.start.ctx.send(mt.winning_rating())


class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Join the game."""
        try:
            Imaginarium.gameplay.join(Player(ctx.author))
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.author.send(mt.you_cannot_join_now(
                message_language=ul[ctx.author]))
        except Imaginarium.exceptions.PlayerAlreadyJoined:
            await ctx.author.send(mt.you_already_joined(
                message_language=ul[ctx.author]))
        else:
            await ctx.send(mt.player_joined(ctx.author.mention))

    @commands.command()
    async def leave(self, ctx):
        """Leave the game."""
        try:
            Imaginarium.gameplay.leave(ctx.author.id)
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.author.send(mt.you_cannot_leave_now(
                message_language=ul[ctx.author]))
        except Imaginarium.exceptions.PlayerAlreadyLeft:
            await ctx.author.send(mt.you_already_left(
                message_language=ul[ctx.author]))
        else:
            await ctx.send(mt.player_left(ctx.author.mention))

    @commands.command()
    async def start(self, ctx):
        """Start the game."""
        Gameplay.start.ctx = ctx

        try:
            await Imaginarium.gameplay.start_game(
                at_start_hook=at_start_hook,
                at_round_start_hook=at_round_start_hook,
                request_association_hook=request_association_hook,
                show_association_hook=show_association_hook,
                request_players_cards_2_hook=request_players_cards_2_hook,
                request_leader_card_hook=request_leader_card_hook,
                request_players_cards_hook=request_players_cards_hook,
                vote_for_target_card_2_hook=vote_for_target_card_2_hook,
                vote_for_target_card_hook=vote_for_target_card_hook,
                at_end_hook=at_end_hook)
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.send(mt.game_already_started())
        except Imaginarium.exceptions.NoAnyUsedSources:
            await ctx.send(mt.no_any_used_sources())
        except Imaginarium.exceptions.NotEnoughPlayers:
            await ctx.send(mt.not_enough_players())

    @commands.command()
    async def end(self, ctx):
        """End the game."""
        try:
            Imaginarium.gameplay.end_game()
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.send(mt.game_already_ended())
        else:
            await ctx.send(mt.game_will_end())


def setup(bot):
    wait_for_reply.bot = bot

    bot.add_cog(cog=Gameplay(bot))
