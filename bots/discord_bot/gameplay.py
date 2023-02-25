import asyncio
import random
import functools
from typing import TypeAlias, Iterable, Callable, Any

import discord
from discord.ext import commands
from discord_components import Button, Interaction

import Imaginarium
from Imaginarium.gameplay import GameCondition
import messages_text as mt
from messages_text import users_languages as ul
import messages_components as mc


class Player(Imaginarium.gameplay.Player, discord.abc.User):
    """Class that inherits from "Imaginarium.gameplay.Player"
    and is used to work with players in discord bot."""

    def __init__(self, user: discord.Member) -> None:
        """Initialize the player.

        :param user: Discord member that is the player."""
        super().__init__(user.id, user.mention)

        self.user = user

        self._preferred_language: str | None = None
        """The locale specified by the user, 
        which does not depend on his locale in the settings."""

    def __hash__(self) -> int:
        return hash(self.user)

    @property
    def display_name(self):
        return self.user.display_name

    @property
    def mention(self):
        return self.user.mention

    @property
    def name(self) -> str:
        return self.user.mention

    @property
    def language(self) -> str | None:
        if self._preferred_language is None:
            try:
                return self.user.locale
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

    async def send(self, *args, **kwargs) -> None:
        """Send a message to the member that is the player."""
        await self.user.send(*args, **kwargs)


Reaction: TypeAlias = (discord.Reaction |
                       discord.Emoji |
                       discord.PartialEmoji |
                       str)


async def wait_for_reply(
        recipient: discord.abc.Messageable | Player,
        message: str = None,
        reactions: Iterable[Reaction] = (),
        buttons: Iterable[Iterable[Button]] = None,
        message_check: Callable[[discord.Message], bool] = None,
        reaction_check: Callable[[discord.Reaction], bool] = None,
        button_check: Callable[[Interaction], bool] = None,
        timeout: float = None,
        bot: discord.Client = None) -> str:
    """Wait for a reply from the recipient.

    Send a message to the recipient and wait for a correct reply
    with a message, reaction or button until time is up.

    :param recipient: Discord member or channel that will receive the message.
    :param message: Text that will be sent to the recipient.
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
    no correct reply was received."""

    if bot is None:
        # noinspection PyUnresolvedReferences
        bot = wait_for_reply.bot
    if timeout is None:
        timeout = Imaginarium.rules_setup.step_timeout

    reply = None

    message = await recipient.send(message, components=buttons)
    for r in reactions:
        await message.add_reaction(r)

    async def wait_for_message():
        nonlocal reply
        reply = (await bot.wait_for('message',
                                    check=message_check)).content

    async def wait_for_reaction_add():
        nonlocal reply
        reply = (await bot.wait_for('reaction_add',
                                    check=reaction_check))[0].emoji

    async def wait_for_button_click():
        nonlocal reply
        reply = (await bot.wait_for('button_click',
                                    check=button_check)).component.label

    pending_tasks = (wait_for_message(),
                     wait_for_reaction_add(),
                     wait_for_button_click())
    pending_tasks = (await asyncio.wait(pending_tasks,
                                        timeout=timeout,
                                        return_when=asyncio.FIRST_COMPLETED))[1]
    for task in pending_tasks:
        task.cancel()

    if reply:
        return str(reply)

    raise asyncio.TimeoutError()


MessageCheck: TypeAlias = Callable[[discord.Message], bool]
ButtonCheck: TypeAlias = Callable[[Interaction], bool]


def not_bot_message_check_decorator(func: MessageCheck) -> MessageCheck:
    """Decorator that checks if the message author is not a bot."""

    @functools.wraps(func)
    def inner(message):
        if not message.author.bot:
            return func(message)
        return False

    return inner


def not_bot_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
    """Decorator that checks if the button author is not a bot."""

    @functools.wraps(func)
    def inner(interaction):
        if not interaction.author.bot:
            return func(interaction)
        return False

    return inner


def digit_message_check_decorator(func: MessageCheck) -> MessageCheck:
    """Decorator that checks if the message content is a digit."""

    @functools.wraps(func)
    def inner(message):
        if message.content.isdigit():
            return func(message)
        return False

    return inner


def digit_button_check_decorator(func: ButtonCheck) -> ButtonCheck:
    """Decorator that checks if the button label is a digit."""

    @functools.wraps(func)
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
    that is in range of cards quantity."""
    if func is None:
        return lambda func: in_range_of_cards_message_check_decorator(
            func,
            start=start,
            stop=stop,
            step=step)

    if stop is None:
        stop = Imaginarium.rules_setup.cards_one_player_has + 1

    @functools.wraps(func)
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
    that is in range of cards quantity."""
    if func is None:
        return lambda func: in_range_of_cards_button_check_decorator(func,
                                                                     start=start,
                                                                     stop=stop,
                                                                     step=step)

    if stop is None:
        stop = Imaginarium.rules_setup.cards_one_player_has + 1

    @functools.wraps(func)
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

    @functools.wraps(func)
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

    @functools.wraps(func)
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

    @functools.wraps(func)
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

    @functools.wraps(func)
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


def at_start_hook() -> None:
    """Send a message to the channel that the game has started."""
    asyncio.run(Gameplay.start.ctx.send(mt.game_has_started()))


def at_round_start_hook() -> None:
    """Send a message to the channel that the round has started."""
    asyncio.run(Gameplay.start.ctx.send(mt.round_has_started()))


# noinspection PyTypeChecker
def request_association_hook() -> None:
    """Do not continue the game until the leader specifies an association."""

    @not_bot_message_check_decorator
    @leader_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        return True

    @not_bot_button_check_decorator
    @leader_button_check_decorator
    def button_check(interaction: Any) -> bool:
        return True

    try:
        association = \
            asyncio.run(wait_for_reply(
                recipient=GameCondition._leader,
                message=mt.inform_association(message_language=ul[GameCondition._leader]),
                buttons=mc.confirm_association(message_language=ul[GameCondition._leader]),
                message_check=message_check,
                button_check=button_check))
    except asyncio.TimeoutError:
        association = '...'
        asyncio.run(GameCondition._leader.send(
            mt.association_selected_automatically(
                association=association,
                message_language=ul[GameCondition._leader])
        ))
    Imaginarium.gameplay.round_association = association


def show_association_hook() -> None:
    """Send the association to the channel."""
    if GameCondition._round_association:
        asyncio.run(Gameplay.start.ctx.send(mt.round_association()))


def request_players_cards_2_hook() -> None:
    """Request each player to choose 2 cards to discard in two-player mode
    or choose the cards automatically if the player's time is up."""
    # Remember discarded card to not allow the player to choose it again.
    discarded_card = None

    @selected_card_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        number = int(message.content)

        # Check the number is not equal to the previous discarded card
        if number != discarded_card:
            return True
        return False

    @selected_card_button_check_decorator
    def button_check(interaction: Any) -> bool:
        number = int(interaction.component.label)

        # Check the number is not equal to the previous discarded card
        if number != discarded_card:
            return True
        return False

    for player in Imaginarium.gameplay.players:
        for message in (
                mt.choose_first_card(
                    player.cards,
                    message_language=ul[player]),
                mt.choose_second_card(
                    player.cards,
                    message_language=ul[player])):
            try:
                card = int(asyncio.run(wait_for_reply(
                    recipient=player,
                    message=message,
                    message_check=message_check,
                    button_check=button_check,
                    buttons=mc.players_cards())))
            except asyncio.TimeoutError:
                card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
                asyncio.run(player.send(
                    mt.card_selected_automatically(
                        player.cards[card - 1],
                        message_language=ul[player])))
            else:
                asyncio.run(player.send(mt.your_chosen_card(
                    player.cards[card - 1],
                    message_language=ul[player])))

            GameCondition._discarded_cards.append((player.cards[card - 1],
                                                   player.id))

            # Set the first discarded card
            discarded_card = card


def request_leader_card_hook() -> None:
    """Request the leader to choose a card to discard."""

    @selected_card_message_check_decorator
    @leader_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        return True

    @selected_card_button_check_decorator
    @leader_button_check_decorator
    def button_check(interaction: Any) -> bool:
        return True

    try:
        card = int(asyncio.run(wait_for_reply(
            recipient=GameCondition._leader,
            message=mt.choose_your_leaders_card(
                message_language=ul[GameCondition._leader]),
            message_check=message_check,
            button_check=button_check,
            buttons=mc.players_cards())))
    except asyncio.TimeoutError:
        card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
        asyncio.run(GameCondition._leader.send(
            mt.card_selected_automatically(
                GameCondition._leader.cards[card - 1],
                message_language=ul[GameCondition._leader])))
    else:
        asyncio.run(GameCondition._leader.send(mt.your_chosen_card(
            GameCondition._leader.cards[card - 1],
            message_language=ul[GameCondition._leader])))

    GameCondition._discarded_cards.append(
        (GameCondition._leader.cards.pop(card - 1),
         GameCondition._leader.id))


def request_players_cards_hook() -> None:
    """Request each player except the leader to choose a card to discard
    or choose the card automatically if the player's time is up."""

    @selected_card_message_check_decorator
    @not_leader_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        return True

    @selected_card_button_check_decorator
    @not_leader_button_check_decorator
    def button_check(interaction: Any) -> bool:
        return True

    for player in Imaginarium.gameplay.players:
        if player != GameCondition._leader:
            try:
                card = int(asyncio.run(wait_for_reply(
                    recipient=player,
                    message=mt.choose_card(
                        player.cards,
                        message_language=ul[player]),
                    message_check=message_check,
                    button_check=button_check,
                    buttons=mc.players_cards())))
            except asyncio.TimeoutError:
                card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
                asyncio.run(player.send(
                    mt.card_selected_automatically(
                        player.cards[card - 1],
                        message_language=ul[player])))
            else:
                asyncio.run(player.send(mt.your_chosen_card(
                    player.cards[card - 1],
                    message_language=ul[player])))

            GameCondition._discarded_cards.append((player.cards.pop(card - 1),
                                                   player.id))


# noinspection DuplicatedCode
def vote_for_target_card_2_hook() -> None:
    """Request each player to vote for the bot's card in two-player mode."""

    @selected_card_message_check_decorator
    def message_check(message: discord.Message) -> bool:
        if GameCondition._discarded_cards[int(message.content) - 1][1] != \
                message.author.id:
            return True
        return False

    @selected_card_button_check_decorator
    def button_check(interaction: Any) -> bool:
        if GameCondition._discarded_cards[int(interaction.component.label) - 1][1] != \
                interaction.user.id:
            return True
        return False

    for player in Imaginarium.gameplay.players:
        try:
            card = int(
                asyncio.run(wait_for_reply(
                    recipient=player,
                    message=mt.choose_enemy_card(
                        message_language=ul[player]),
                    message_check=message_check,
                    button_check=button_check,
                    buttons=mc.discarded_cards())))
        except asyncio.TimeoutError:
            card = random.randint(1, len(Imaginarium.gameplay.players))
            asyncio.run(player.send(
                mt.card_selected_automatically(
                    GameCondition._discarded_cards[card - 1][0],
                    message_language=ul[player])))
        else:
            asyncio.run(player.send(mt.your_chosen_card(
                GameCondition._discarded_cards[card - 1][0],
                message_language=ul[player])))

        GameCondition._votes_for_card[
            GameCondition._discarded_cards[card - 1][1]] += 1

        player.chosen_card = card


# noinspection DuplicatedCode
def vote_for_target_card_hook() -> None:
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
    def button_check(interaction: Any) -> bool:
        if GameCondition._discarded_cards[int(interaction.component.label) - 1][1] != \
                interaction.user.id:
            return True
        return False

    for player in Imaginarium.gameplay.players:
        if player != GameCondition._leader:
            try:
                card = int(
                    asyncio.run(wait_for_reply(
                        recipient=player,
                        message=mt.choose_enemy_card(
                            message_language=ul[player]),
                        message_check=message_check,
                        button_check=button_check,
                        buttons=mc.discarded_cards())))
            except asyncio.TimeoutError:
                card = random.randint(1, len(Imaginarium.gameplay.players))
                asyncio.run(player.send(
                    mt.card_selected_automatically(
                        GameCondition._discarded_cards[card - 1][0],
                        message_language=ul[player])))
            else:
                asyncio.run(player.send(mt.your_chosen_card(
                    GameCondition._discarded_cards[card - 1][0],
                    message_language=ul[player])))

            GameCondition._votes_for_card[
                GameCondition._discarded_cards[card - 1][1]] += 1

            player.chosen_card = card


def at_end_hook() -> None:
    """Announce the results of the game."""
    asyncio.run(Gameplay.start.ctx.send(mt.game_took_time()))

    if len(Imaginarium.gameplay.players) == 2:
        if GameCondition._bot_score > GameCondition._players_score:
            asyncio.run(Gameplay.start.ctx.send(mt.loss_score()))
        elif GameCondition._bot_score < GameCondition._players_score:
            asyncio.run(Gameplay.start.ctx.send(mt.win_score()))
        else:
            asyncio.run(Gameplay.start.ctx.send(mt.draw_score()))
    else:
        asyncio.run(Gameplay.start.ctx.send(mt.winning_rating()))


class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Join the game."""
        try:
            try:
                Imaginarium.gameplay.join(Player(ctx.author))
            except Imaginarium.exceptions.PlayerAlreadyJoined:
                await ctx.author.send(mt.you_already_joined(
                    message_language=ul[ctx.author]))
            else:
                await ctx.send(mt.player_joined(ctx.author.mention))
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.author.send(mt.you_cannot_join_now(
                message_language=ul[ctx.author]))

    @commands.command()
    async def leave(self, ctx):
        """Leave the game."""
        try:
            try:
                Imaginarium.gameplay.leave(ctx.author.id)
            except Imaginarium.exceptions.PlayerAlreadyLeft:
                await ctx.author.send(mt.you_already_left(
                    message_language=ul[ctx.author]))
            else:
                await ctx.send(mt.player_left(ctx.author.mention))
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.author.send(mt.you_cannot_leave_now(
                message_language=ul[ctx.author]))

    @commands.command()
    async def start(self, ctx):
        """Start the game."""
        Gameplay.start.ctx = ctx

        try:
            Imaginarium.gameplay.start_game(
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

    bot.add_cog(Gameplay(bot))
