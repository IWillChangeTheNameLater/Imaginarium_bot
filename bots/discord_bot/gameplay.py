import asyncio
import random

from discord.ext import commands
from discord_components import Button, ButtonStyle

import Imaginarium
from Imaginarium.gameplay import GameCondition
from messages_text import *


class Player(Imaginarium.gameplay.Player):
    def __init__(self, user):
        super().__init__(user.id, user.mention)

        self.user = user

    async def send(self, message, *args, **kwargs):
        await self.user.send(message, *args, **kwargs)


def filled_iter(iterator, filling=None):
    for i in iterator:
        yield i
    while True:
        yield filling


def generate_buttons(labels, styles=filled_iter((), 2),
                     urls=filled_iter(()),
                     disabled=filled_iter((), False),
                     emojis=filled_iter(())):
    """Return generated list of DiscordComponents.Button."""
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


async def wait_for_reply(recipient, message=None, reactions=(), components=None, message_check=None,
                         reaction_check=None, button_check=None, timeout=None, bot=None):
    if bot is None:
        # noinspection PyUnresolvedReferences
        bot = wait_for_reply.bot
    if timeout is None:
        timeout = Imaginarium.rules_setup.step_timeout

    reply = None

    msg = await recipient.send(message, components=components)
    for r in reactions:
        await msg.add_reaction(r)

    async def wait_for_message():
        nonlocal reply
        reply = (await bot.wait_for('message', check=message_check)).content

    async def wait_for_reaction_add():
        nonlocal reply
        reply = (await bot.wait_for('reaction_add', check=reaction_check))[0].emoji

    async def wait_for_button_click():
        nonlocal reply
        reply = (await bot.wait_for("button_click", check=button_check)).component.label

    pending_tasks = [wait_for_message(),
                     wait_for_reaction_add(),
                     wait_for_button_click()]
    pending_tasks = (await asyncio.wait(pending_tasks,
                                        timeout=timeout,
                                        return_when=asyncio.FIRST_COMPLETED))[1]
    for task in pending_tasks:
        task.cancel()

    if reply:
        return str(reply)

    raise asyncio.TimeoutError


def not_bot_message_check_decorator(func):
    def inner(message):
        if not message.author.bot:
            return func(message)
        return False

    return inner


def not_bot_button_check_decorator(func):
    def inner(interaction):
        if not interaction.author.bot:
            return func(interaction)
        return False

    return inner


def digit_message_check_decorator(func):
    def inner(message):
        if message.content.isdigit():
            return func(message)
        return False

    return inner


def digit_button_check_decorator(func):
    def inner(interaction):
        if interaction.component.label.isdigit():
            return func(interaction)
        return False

    return inner


def in_range_of_cards_message_check_decorator(func,
                                              start=1,
                                              stop=None,
                                              step=1):
    if stop is None:
        stop = Imaginarium.rules_setup.cards_one_player_has + 1

    def inner(message):
        if int(message.content) in range(start, stop, step):
            return func(message)

        return False

    return inner


def in_range_of_cards_button_check_decorator(func,
                                             start=1,
                                             stop=None,
                                             step=1):
    if stop is None:
        stop = Imaginarium.rules_setup.cards_one_player_has + 1

    def inner(interaction):
        if int(interaction.component.label) in range(start, stop, step):
            return func(interaction)
        return False

    return inner


def leader_message_check_decorator(func, leader=None):
    if leader is None:
        leader = GameCondition.leader

    def inner(message):
        if message.author == leader:
            return func(message)
        return False

    return inner


def leader_button_check_decorator(func, leader=None):
    if leader is None:
        leader = GameCondition.leader

    def inner(interaction):
        if interaction.author.id == leader.id:
            return func(interaction)
        return False

    return inner


def not_leader_message_check_decorator(func, leader=None):
    if leader is None:
        leader = GameCondition.leader

    def inner(message):
        if message.author != leader:
            return func(message)
        return False

    return inner


def not_leader_button_check_decorator(func, leader=None):
    if leader is None:
        leader = GameCondition.leader

    def inner(interaction):
        if interaction.author.id != leader.id:
            return func(interaction)
        return False

    return inner


def selected_card_message_check_decorator(func):
    func = in_range_of_cards_message_check_decorator(func)
    func = digit_message_check_decorator(func)
    func = not_bot_message_check_decorator(func)

    return func


def selected_card_button_check_decorator(func):
    func = in_range_of_cards_button_check_decorator(func)
    func = digit_button_check_decorator(func)
    func = not_bot_button_check_decorator(func)

    return func


def at_start_hook():
    asyncio.run(Gameplay.start.ctx.channel.send(English.game_has_started()))


def at_round_start_hook():
    asyncio.run(Gameplay.start.ctx.channel.send(English.round_has_started()))


def request_association_hook():
    @not_bot_message_check_decorator
    @leader_message_check_decorator
    def message_check(message):
        return True

    @not_bot_button_check_decorator
    @leader_button_check_decorator
    def button_check(interaction):
        return True

    Imaginarium.gameplay.round_association = asyncio.run(wait_for_reply(GameCondition.leader,
                                                                        message=English.inform_association(),
                                                                        components=[Button(style=ButtonStyle.green,
                                                                                           label='Yes',
                                                                                           emoji='✅')],
                                                                        message_check=message_check,
                                                                        button_check=button_check))


def show_association_hook():
    if GameCondition.round_association:
        asyncio.run(Gameplay.start.ctx.channel.send(English.round_association()))


def request_players_cards_2_hook():
    discarded_card = None

    @selected_card_message_check_decorator
    def message_check(message):
        number = int(message.content)

        # Check the number is not equal to the previous discarded card
        if number != discarded_card:
            return True
        return False

    @selected_card_button_check_decorator
    def button_check(interaction):
        number = int(interaction.component.label)

        # Check the number is not equal to the previous discarded card
        if number != discarded_card:
            return True
        return False

    for player in Imaginarium.gameplay.players:
        for line in (English.choose_first_card(),
                     English.choose_second_card()):
            try:
                card = int(asyncio.run(wait_for_reply(player, message=line + '\n'.join(str(c) for c in player.cards),
                                                      message_check=message_check, button_check=button_check,
                                                      components=generate_buttons(
                                                          range(1, Imaginarium.rules_setup.cards_one_player_has + 1)))))
                asyncio.run(player.send(English.your_chosen_card(player.cards[card - 1])))
            except asyncio.TimeoutError:
                card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
                asyncio.run(player.send(English.card_selected_automatically(player.cards[card - 1])))

            GameCondition.discarded_cards.append((player.cards[card - 1], player.id))

            # Set the first discarded card
            discarded_card = card


def request_leader_card_hook():
    @selected_card_message_check_decorator
    @leader_message_check_decorator
    def message_check(message):
        return True

    @selected_card_button_check_decorator
    @leader_button_check_decorator
    def button_check(interaction):
        return True

    try:
        card = int(asyncio.run(wait_for_reply(GameCondition.leader,
                                              message=English.choose_your_leaders_card(),
                                              message_check=message_check,
                                              button_check=button_check,
                                              components=generate_buttons(range(1,
                                                                                Imaginarium.rules_setup.
                                                                                cards_one_player_has + 1)))))
        asyncio.run(GameCondition.leader.send(English.your_chosen_card(GameCondition.leader.cards[
                                                                           card - 1])))
    except asyncio.TimeoutError:
        card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
        asyncio.run(GameCondition.leader.send(
            English.card_selected_automatically(GameCondition.leader.cards[card - 1])))

    GameCondition.discarded_cards.append(
        (GameCondition.leader.cards.pop(card - 1), GameCondition.leader.id))


def request_players_cards_hook():
    @selected_card_message_check_decorator
    @not_leader_message_check_decorator
    def message_check(message):
        return True

    @selected_card_button_check_decorator
    @not_leader_button_check_decorator
    def button_check(interaction):
        return True

    for player in Imaginarium.gameplay.players:
        if player != GameCondition.leader:
            try:
                card = int(asyncio.run(wait_for_reply(player,
                                                      message=English.choose_card(player.cards),
                                                      message_check=message_check,
                                                      button_check=button_check,
                                                      components=generate_buttons(range(1,
                                                                                        Imaginarium.rules_setup.
                                                                                        cards_one_player_has + 1)))))
                asyncio.run(player.send(English.your_chosen_card(player.cards[card - 1])))
            except asyncio.TimeoutError:
                card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
                asyncio.run(player.send(English.card_selected_automatically(player.cards[card - 1])))

            GameCondition.discarded_cards.append((player.cards.pop(card - 1), player.id))


def vote_for_target_card_2_hook():
    @selected_card_message_check_decorator
    def message_check(message):
        if GameCondition.discarded_cards[int(message.content) - 1][1] != message.author.id:
            return True
        return False

    @selected_card_button_check_decorator
    def button_check(interaction):
        if GameCondition.discarded_cards[int(interaction.component.label) - 1][1] != interaction.user.id:
            return True
        return False

    for player in Imaginarium.gameplay.players:
        try:
            card = int(
                asyncio.run(wait_for_reply(player, message=English.choose_enemy_card(), message_check=message_check,
                                           button_check=button_check,
                                           components=generate_buttons(
                                               range(1,
                                                     len(GameCondition.discarded_cards) + 1)))))
            asyncio.run(player.send(English.your_chosen_card(GameCondition.discarded_cards[card - 1][0])))
        except asyncio.TimeoutError:
            card = random.randint(1, len(Imaginarium.gameplay.players))
            asyncio.run(player.send(English.card_selected_automatically(GameCondition.discarded_cards[card - 1])))

        GameCondition.votes_for_card[
            GameCondition.discarded_cards[card - 1][1]] += 1
        player.chosen_card = card


def vote_for_target_card_hook():
    @selected_card_message_check_decorator
    @not_leader_message_check_decorator
    def message_check(message):
        if GameCondition.discarded_cards[int(message.content) - 1][1] != message.author.id:
            return True
        return False

    @selected_card_button_check_decorator
    @not_leader_button_check_decorator
    def button_check(interaction):
        if GameCondition.discarded_cards[int(interaction.component.label) - 1][1] != interaction.user.id:
            return True
        return False

    for player in Imaginarium.gameplay.players:
        if player != GameCondition.leader:
            try:
                card = int(
                    asyncio.run(wait_for_reply(player, message=English.choose_enemy_card(), message_check=message_check,
                                               button_check=button_check,
                                               components=generate_buttons(
                                                   range(1,
                                                         len(GameCondition.discarded_cards) + 1)))))
                asyncio.run(
                    player.send(English.your_chosen_card(GameCondition.discarded_cards[card - 1][
                                                             0])))
            except asyncio.TimeoutError:
                card = random.randint(1, len(Imaginarium.gameplay.players))
                asyncio.run(player.send(English.card_selected_automatically(GameCondition.discarded_cards[card - 1])))

            GameCondition.votes_for_card[
                GameCondition.discarded_cards[card - 1][1]] += 1
            player.chosen_card = card


def at_end_hook():
    asyncio.run(Gameplay.start.ctx.send(English.game_took_time()))

    if len(Imaginarium.gameplay.players) == 2:
        if GameCondition.bot_score > GameCondition.players_score:
            asyncio.run(Gameplay.start.ctx.send(English.loss_score()))
        if GameCondition.players_score > GameCondition.bot_score:
            asyncio.run(Gameplay.start.ctx.send(English.win_score()))
        else:
            asyncio.run(Gameplay.start.ctx.send(English.draw_score()))
    else:
        asyncio.run(Gameplay.start.ctx.send(English.winning_rating()))


class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        try:
            if ctx.author.id in Imaginarium.gameplay.players:
                await ctx.send(English.you_already_joined())
            else:
                Imaginarium.gameplay.join(Player(ctx.author))

                await ctx.send(English.player_joined(ctx.author.mention))
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.send(English.you_cannot_join_now())

    @commands.command()
    async def leave(self, ctx):
        try:
            if ctx.author.id not in Imaginarium.gameplay.players:
                await ctx.send(English.you_already_left())
            else:
                Imaginarium.gameplay.leave(ctx.author.id)

                await ctx.send(English.player_left(ctx.author.mention))
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.send(English.you_cannot_leave_now())

    @commands.command()
    async def start(self, ctx):
        Gameplay.start.ctx = ctx

        try:
            Imaginarium.gameplay.start_game(at_start_hook=at_start_hook,
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
            await ctx.send(English.game_already_started())
        except Imaginarium.exceptions.NoAnyUsedSources:
            await ctx.send(English.no_any_used_sources())
        except Imaginarium.exceptions.NotEnoughPlayers:
            await ctx.send(English.not_enough_players())

    @commands.command()
    async def end(self, ctx):
        try:
            Imaginarium.gameplay.end_game()

            await ctx.send(English.game_will_end())
        except Imaginarium.exceptions.GameIsStarted:
            await ctx.send(English.game_already_ended())


def setup(bot):
    wait_for_reply.bot = bot

    bot.add_cog(Gameplay(bot))
