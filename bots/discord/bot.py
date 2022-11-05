import asyncio
import os

import nest_asyncio

# To fix "RuntimeError: This event loop is already running"
# the "next_asyncio.apply()" have to be called before "discord" import.
nest_asyncio.apply()
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
import random
import chardet
import dotenv

import configuration
import Imaginarium
from Imaginarium.game import GameCondition

dotenv.load_dotenv()


class Player(Imaginarium.game.Player):
    def __init__(self, user):
        super().__init__(user.id, user.mention)

        self.user = user

    async def send(self, message, *args, **kwargs):
        await self.user.send(message, *args, **kwargs)


def extract_file_extension(filename):
    return filename[filename.rfind('.') + 1:]


async def iterate_sources(ctx, message, function):
    """Extract sources from attachments and process them.

    Extract separated by break sources from the file and the message and
    process them by the function."""

    async def iterate_lines(lines):
        for source in lines.replace('\r', '').split('\n'):
            await function(source)

    await iterate_lines(message)

    for attachment in ctx.message.attachments:
        filetype = extract_file_extension(attachment.filename)

        if filetype == 'txt':
            text = await attachment.read()
            await iterate_lines(text.decode(chardet.detect(text[:1000])['encoding']))
        else:
            await ctx.send('The "' + filetype + '" filetype is not supported.')


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
                         reaction_check=None, button_check=None, timeout=None):
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
        # TODO return not str
        return str(reply)

    raise asyncio.TimeoutError


bot = commands.Bot(command_prefix=configuration.PREFIX,
                   intents=discord.Intents.all())
bot.remove_command('help')


@bot.event
async def on_ready():
    DiscordComponents(bot)

    print('The bot is ready.')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            'The command does not exist. Write "' + configuration.PREFIX + 'help" to get available commands.')
    else:
        raise error


@bot.event
async def on_button_click(interaction):
    if not interaction.responded:
        await interaction.respond(type=6)


@bot.command(name='help')
async def guidance(ctx):
    await ctx.author.send('Godspeed.\n'
                          '*Useful information*')


@bot.command()
async def set_winning_score(ctx, score):
    if score.isdigit():
        Imaginarium.rules_setup.winning_score = int(score)
    else:
        await ctx.author.send('Score is supposed to be a number.')


@bot.command()
async def get_players_score(ctx):
    if Imaginarium.game.players:
        await ctx.author.send(
            'Players score:\n' + '\n'.join(
                (str(player) + ': ' + str(player.score) for player in Imaginarium.game.players)))
    else:
        await ctx.author.send('There are no any players.')


@bot.command()
async def get_used_cards(ctx):
    await ctx.author.send('\n'.join(Imaginarium.game.used_cards))


@bot.command()
async def reset_used_cards(ctx):
    Imaginarium.game.used_cards = set()

    await ctx.send('Used cards are reset.')


@bot.command()
async def set_step_minutes(ctx, minutes):
    if minutes.isdigit():
        Imaginarium.rules_setup.step_timeout = float(minutes) * 60
    else:
        await ctx.author.send('"Score" supposed to be a number.')


@bot.command()
async def get_used_sources(ctx):
    if Imaginarium.game.used_sources:
        await ctx.author.send('\n'.join(str(source) for source in Imaginarium.game.used_sources))
    else:
        await ctx.author.send('There are no any sources here yet.')


@bot.command()
async def reset_used_sources(ctx):
    Imaginarium.game.used_sources = set()

    await ctx.send('Sources are reset.')


@bot.command()
async def add_used_sources(ctx, *, message=''):
    async def move_source(source):
        if source:
            try:
                Imaginarium.game.used_sources.add(Imaginarium.game.create_source_object(source))
            except Imaginarium.exceptions.UnexpectedSource:
                await ctx.send('There is something wrong with source: ' + source)

    await iterate_sources(ctx, message, move_source)


@bot.command()
async def remove_source(ctx, *, message=''):
    async def move_source(source):
        if source:
            try:
                Imaginarium.game.used_sources.remove(source)
            except KeyError:
                await ctx.send('There is no the source: ' + source)

    await iterate_sources(ctx, message, move_source)


@bot.command()
async def get_players(ctx):
    if Imaginarium.game.players:
        await ctx.author.send('Players: \n' + '\n'.join(str(player) for player in Imaginarium.game.players))
    else:
        await ctx.author.send('There are no any players.')


@bot.command()
async def join(ctx):
    if GameCondition.game_started:
        await ctx.send('You can\'t join right now, the game is started.')
    elif ctx.author.id in Imaginarium.game.players:
        await ctx.send('You have already joined')
    else:
        Imaginarium.game.players.append(Player(ctx.author))
        await ctx.send('Player ' + ctx.author.mention + ' has joined the game.')


@bot.command()
async def leave(ctx):
    if GameCondition.game_started:
        await ctx.send('You can\'t leave the game now, it is started.')
    else:
        try:
            Imaginarium.game.players.remove(ctx.author.id)
            await ctx.send('Players ' + ctx.author.mention + ' have left the game.')
        except ValueError:
            ctx.send('You have already left.')


@bot.command()
async def shuffle_players_order(ctx):
    random.shuffle(Imaginarium.game.players)
    if Imaginarium.game.players:
        await ctx.send(
            'Now you walk in the following order: ' + '\n' + '\n'.join(
                str(player) for player in Imaginarium.game.players))
    else:
        await ctx.send('There are no any players.')


def at_start():
    asyncio.run(start.ctx.channel.send('The game has started.'))


def at_round_start():
    asyncio.run(
        start.ctx.channel.send('The round ' + str(GameCondition.round_number) + ' has started.'))


def request_association():
    def message_check(message):
        if all((not message.author.bot,
                message.author == GameCondition.leader)):
            return True
        return False

    def button_check(interaction):
        if all((not interaction.author.bot,
                interaction.author.id == GameCondition.leader.id)):
            return True
        return False

    Imaginarium.game.round_association = asyncio.run(wait_for_reply(GameCondition.leader,
                                                                    message='Did you tell the association '
                                                                            'of the round? Write it below '
                                                                            'or confirm it by pressing the button.',
                                                                    components=[Button(style=ButtonStyle.green,
                                                                                       label='Yes',
                                                                                       emoji='✅')],
                                                                    message_check=message_check,
                                                                    button_check=button_check))


def show_association():
    if GameCondition.round_association:
        asyncio.run(
            start.ctx.channel.send(
                'The association of the round is: ' + str(GameCondition.round_association)))


def request_players_cards_2():
    discarded_card = None

    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has,
                number != discarded_card)):
            return True
        return False

    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has,
                number != discarded_card)):
            return True
        return False

    for player in Imaginarium.game.players:
        for line in ('Choose the first card you want to... choose?..',
                     'Choose the second card you want to... choose?..'):
            try:
                card = int(asyncio.run(wait_for_reply(player, message=line + '\n'.join(str(c) for c in player.cards),
                                                      message_check=message_check, button_check=button_check,
                                                      components=generate_buttons(
                                                          range(1, Imaginarium.rules_setup.cards_one_player_has + 1)),
                                                      timeout=Imaginarium.rules_setup.step_timeout)))
                asyncio.run(player.send('You has chosen the card ' + player.cards[card - 1] + '.'))
            except asyncio.TimeoutError:
                card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
                asyncio.run(player.send('You was thinking too much. The card ' + player.cards[
                    card - 1] + ' was automatically selected for you.'))

            GameCondition.discarded_cards.append((player.cards[card - 1], player.id))
            discarded_card = card


def request_leader_card():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has)):
            return True
        return False

    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has)):
            return True
        return False

    try:
        card = int(asyncio.run(wait_for_reply(GameCondition.leader,
                                              message='You are a leader now. Choose number of one of your cards:\n' +
                                                      '\n'.join(
                                                          str(c) for c in GameCondition.leader.cards),
                                              message_check=message_check,
                                              button_check=button_check,
                                              components=generate_buttons(range(1,
                                                                                Imaginarium.rules_setup.
                                                                                cards_one_player_has + 1)),
                                              timeout=Imaginarium.rules_setup.step_timeout)))
        asyncio.run(GameCondition.leader.send('You has chosen the card ' +
                                              GameCondition.leader.cards[
                                                  card - 1] + '.'))
    except asyncio.TimeoutError:
        card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
        asyncio.run(GameCondition.leader.send('You was thinking too much. The card ' +
                                              GameCondition.leader.cards[card - 1] +
                                              ' was automatically selected for you.'))

    GameCondition.discarded_cards.append(
        (GameCondition.leader.cards.pop(card - 1), GameCondition.leader.id))


def request_players_cards():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has)):
            return True
        return False

    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has)):
            return True
        return False

    for player in Imaginarium.game.players:
        if player != GameCondition.leader:
            try:
                card = int(asyncio.run(wait_for_reply(player,
                                                      message='Choose the card you want to... Choose?..:\n' +
                                                              '\n'.join(str(c) for c in player.cards),
                                                      message_check=message_check,
                                                      button_check=button_check,
                                                      components=generate_buttons(range(1,
                                                                                        Imaginarium.rules_setup.
                                                                                        cards_one_player_has + 1)),
                                                      timeout=Imaginarium.rules_setup.step_timeout)))
                asyncio.run(player.send('You has chosen the card ' + player.cards[card - 1] + '.'))
            except asyncio.TimeoutError:
                card = random.randrange(Imaginarium.rules_setup.cards_one_player_has)
                asyncio.run(player.send('You was thinking too much. The card ' +
                                        player.cards[card - 1] +
                                        ' was automatically selected for you.'))

            GameCondition.discarded_cards.append((player.cards.pop(card - 1), player.id))


def vote_for_target_card_2():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has,
                GameCondition.discarded_cards[int(message.content) - 1][1] != message.author.id)):
            return True
        return False

    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has,
                GameCondition.discarded_cards[int(interaction.component.label) - 1][
                    1] != interaction.user.id)):
            return True
        return False

    for player in Imaginarium.game.players:
        try:
            card = int(asyncio.run(wait_for_reply(player, message='Choose the enemy\'s card: \n' + '\n'.join(
                str(c[0]) for c in GameCondition.discarded_cards), message_check=message_check,
                                                  button_check=button_check,
                                                  components=generate_buttons(
                                                      range(1,
                                                            len(GameCondition.discarded_cards) + 1)),
                                                  timeout=Imaginarium.rules_setup.step_timeout)))
            asyncio.run(player.send(
                'You has chosen the card ' + GameCondition.discarded_cards[card - 1][0] + '.'))
        except asyncio.TimeoutError:
            card = random.randint(1, len(Imaginarium.game.players))
            asyncio.run(player.send('You was thinking too much. The card ' +
                                    GameCondition.discarded_cards[card - 1] +
                                    ' was automatically selected for you.'))

        GameCondition.votes_for_card[
            GameCondition.discarded_cards[card - 1][1]] += 1
        player.chosen_card = card


def vote_for_target_card():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has,
                GameCondition.discarded_cards[int(message.content) - 1][1] != message.author.id)):
            return True
        return False

    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot,
                number >= 1,
                number <= Imaginarium.rules_setup.cards_one_player_has,
                GameCondition.discarded_cards[int(interaction.component.label) - 1][
                    1] != interaction.user.id)):
            return True
        return False

    for player in Imaginarium.game.players:
        if player != GameCondition.leader:
            try:
                card = int(asyncio.run(wait_for_reply(player, message='Choose the enemy\'s card: \n' + '\n'.join(
                    str(c[0]) for c in GameCondition.discarded_cards), message_check=message_check,
                                                      button_check=button_check,
                                                      components=generate_buttons(
                                                          range(1,
                                                                len(GameCondition.discarded_cards) + 1)),
                                                      timeout=Imaginarium.rules_setup.step_timeout)))
                asyncio.run(
                    player.send('You has chosen the card ' + GameCondition.discarded_cards[card - 1][
                        0] + '.'))
            except asyncio.TimeoutError:
                card = random.randint(1, len(Imaginarium.game.players))
                asyncio.run(player.send('You was thinking too much. The card ' +
                                        GameCondition.discarded_cards[card - 1] +
                                        ' was automatically selected for you.'))

            GameCondition.votes_for_card[
                GameCondition.discarded_cards[card - 1][1]] += 1
            player.chosen_card = card


def at_end():
    game_took_time = Imaginarium.game.time.time() - GameCondition.game_started_at
    asyncio.run(start.ctx.send('The game took: ' + str(int(game_took_time // 60)) + ' minutes and ' + str(
        int(game_took_time % 60)) + ' seconds.'))

    if len(Imaginarium.game.players) == 2:
        if GameCondition.bot_score > GameCondition.players_score:
            asyncio.run(start.ctx.send('You lose with score: ' + str(GameCondition.players_score)))
        if GameCondition.players_score > GameCondition.bot_score:
            asyncio.run(start.ctx.send('You win with score: ' + str(GameCondition.players_score)))
        else:
            asyncio.run(start.ctx.send('Победила дружба (сырок)!'))
    else:
        asyncio.run(start.ctx.send('The winners: \n' +
                                   '\n'.join((str(place) + '. ' + str(player) for place, player in
                                              enumerate(sorted(Imaginarium.game.players)[:3], start=1)))))


@bot.command()
async def start(ctx):
    start.ctx = ctx

    try:
        Imaginarium.game.start_game(at_start=at_start,
                                    at_round_start=at_round_start,
                                    request_association=request_association,
                                    show_association=show_association,
                                    request_players_cards_2=request_players_cards_2,
                                    request_leader_card=request_leader_card,
                                    request_players_cards=request_players_cards,
                                    vote_for_target_card_2=vote_for_target_card_2,
                                    vote_for_target_card=vote_for_target_card,
                                    at_end=at_end)
    except TypeError:
        await ctx.send('The game cannot start yet. Specify all data and start the game again.')


@bot.command()
async def end(ctx):
    if GameCondition.game_started:
        GameCondition.game_started = False
        await ctx.send('The game will be ended as soon as possible.')
    else:
        await ctx.send('The game is already ended.')


bot.run(os.environ['DISCORD_BOT_TOKEN'])
