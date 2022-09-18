import nest_asyncio
# To fix "RuntimeError: This event loop is already running"
nest_asyncio.apply()
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
import asyncio
import threading
import chardet
import time

from game import *
import game
import game_exceptions
import discord_bot_configuration


class player(player):
    def __init__(self, user:discord.Member):
        super().__init__(user.id, user.mention)
        
        self.user = user

    async def send(self, message, components=None):
        await self.user.send(message, components=components)


async def iterate_sourses(ctx, message, function):
    """Extract sourses from attachments and process them.
    
    Extract separated by break sourses from the file and the message and 
    process them by the function."""
    async def iterate_lines(text):
        for sourse in text.replace('\r', '').split('\n'):
            await function(sourse)
            
    await iterate_lines(message)
    
    for attachment in ctx.message.attachments:
        filetype = game.extract_file_extension(attachment.filename)
        
        if filetype == 'txt':
            text = await attachment.read()
            await iterate_lines(text.decode(chardet.detect(text[:1000])['encoding']))
        else:
            await ctx.send('Sorry, the "' + filetype + '" filetype is not supproted.')
    
def filled_iter(iterator, filling=None):
    for i in iterator:
        yield i 
    while True:
        yield filling

def generate_buttons(labels, styles=filled_iter((), 2), 
                             urls=filled_iter(()), 
                             disableds=filled_iter((), False), 
                             emojis=filled_iter(())):
    """Return generated list of DiscordComponents.Button."""
    labels = iter(labels)
    styles = iter(styles)
    urls = iter(urls)
    disableds = iter(disableds)
    emojis = iter(emojis)
    
    buttons = []
    for i in range(5):
        row = []
        for j in range(5):
            try:
                row.append(Button(label=next(labels), 
                                  style=next(styles), 
                                  url=next(urls), 
                                  disabled=next(disableds), 
                                  emoji=next(emojis)))
            except StopIteration:
                if row:
                    buttons.append(row)
                return buttons
        buttons.append(row)
    return buttons

async def wait_for_answer(recipient, message=None, reactions=(), components=None, message_check=None, reaction_check=None, button_check=None, timeout=None):
    answer = None
    msg = await recipient.send(message, components=components)
    for r in reactions:
        await msg.add_reaction(r)
    
    async def wait_for_message():
        nonlocal answer
        message = await bot.wait_for('message', check=message_check)
        answer = message.content
    async def wait_for_reaction_add():
        nonlocal answer
        reaction, _ = await bot.wait_for('reaction_add', check=reaction_check)
        answer = reaction.emoji
    async def wait_for_button_click():
        nonlocal answer 
        interaction = await bot.wait_for("button_click", check=button_check)
        answer = interaction.component.label
    
    pending_tasks = [wait_for_message(), 
                     wait_for_reaction_add(),
                     wait_for_button_click()]
    _, pending_tasks = await asyncio.wait(pending_tasks, 
                                          timeout=timeout, 
                                          return_when=asyncio.FIRST_COMPLETED)
    for task in pending_tasks:
        task.cancel()
    
    if answer:
        #TODO return not str
        return str(answer)
        
    raise asyncio.TimeoutError
    

bot = commands.Bot(command_prefix=discord_bot_configuration.PREFIX, 
                   intents=discord.Intents.all())
bot.remove_command('help')


@bot.event
async def on_ready():
    DiscordComponents(bot)
    
    print('The bot is ready.')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('The command does not exist. Write "' + discord_bot_configuration.PREFIX + 'help" to get available commands.')
    else:
        raise error


@bot.command()
async def help(ctx):
    await ctx.author.send(
'''Godspeed.
"Useful information"''')

@bot.command()
async def set_winning_score(ctx, score):
    if score.isdigit():
        winning_score = int(score)
    else:
        await ctx.author.send('Score is supposed to be a number.')

@bot.command()
async def get_used_cards(ctx):
    await ctx.author.send('\n'.join(used_cards))

@bot.command()
async def reset_used_cards(ctx):
    used_cards = set()

@bot.command()
async def set_step_minutes(ctx, minutes):
    if minutes.isdigit():
        game.step_timeout = float(minutes)*60
    else:
        await ctx.author.send('"Score" supposed to be a number.')

@bot.command()
async def get_sourses(ctx):
    if sourses:
        await ctx.author.send('\n'.join(str(sourse) for sourse in sourses))
    else:
        await ctx.author.send('Sorry, there are no sources here yet.')

@bot.command()
async def reset_sourses(ctx):
    sourses = set()

@bot.command()
async def add_sourses(ctx, *, message=''):
    async def move_sourse(sourse):
        if sourse:
            try:
                sourses.add(create_sourse_object(sourse))
            except game_exceptions.UnexpectedSourse:
                await ctx.send('Sorry, there is somthing wrong with sourse: ' + sourse)
            
    await iterate_sourses(ctx, message, move_sourse)

@bot.command()
async def remove_sourse(ctx, *, message=''):
    async def move_sourse(sourse):
        if sourse:
            try:
                sourses.remove(sourse)
            except KeyError:
                await ctx.send('Sorry, there is no the sourse: ' + sourse)
    
    await iterate_sourses(ctx, message, move_sourse)

@bot.command()
async def get_players(ctx):
    if players:
        await ctx.author.send('Players: \n' + '\n'.join(str(player) for player in players))
    else:
        await ctx.send('There are no players.')

@bot.command()
async def join(ctx):
    #TODO add person to queue for joining and move it to game.py
    if game.game_started:
        await ctx.send('You can\'t join right now, the game is started.')
    elif ctx.author.id in players:
        await ctx.send('You have already joined')
    else:
        players.append(player(ctx.author))
        await ctx.send('Player ' + ctx.author.mention + ' has joined the game.')
    
@bot.command()
async def leave(ctx):
    if game.game_started:
        await ctx.send('You can\'t leave the game now, it is started.')
    else:
        try:
            players.remove(ctx.author.id)
            await ctx.send('Players ' + ctx.author.mention + ' have left the game.')
        except ValueError:
            ctx.send('You have already left.')

@bot.command()
async def shuffle_players_order(ctx):
    random.shuffle(players)
    if players:
        await ctx.send('Now you walk in the following order: ' + '\n' + '\n'.join(str(player) for player in players))
    else:
        await ctx.send('There are no any players.')


def at_start():
    asyncio.run(start.ctx.channel.send('The game has started.'))

def at_round_start():
    asyncio.run(start.ctx.channel.send('The round ' + str(game.round_number) + ' has started.'))

def request_association():
    def message_check(message):
        if all((not message.author.bot, 
                message.author.id == game.leader.id)): return True
        return False
                        
    def button_check(interaction):
        if all((not interaction.author.bot, 
                interaction.author.id == game.leader.id)): return True
        return False
    
    game.round_association = asyncio.run(wait_for_answer(game.leader, message='Did you tell the association of the round? Write it below or confirm it by pressing the button.', components=[Button(style=ButtonStyle.green, label='Yes', emoji='✅')], message_check=message_check, button_check=button_check))

def show_association():
    if game.round_association:
        asyncio.run(start.ctx.channel.send('The association of the round is: ' + str(game.round_association)))

def request_players_cards_2():
    discarded_card = None
    
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot, 
                number >= 1, 
                number <= cards_one_player_has, 
                number != discarded_card)): return True
        return False
                        
    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot, 
                number >= 1, 
                number <= cards_one_player_has, 
                number != discarded_card)): return True
        return False
        
    
    for player in players:
        for line in ('Choose the first card you want to... choose?..', 
                     'Choose the second card you want to... choose?..'):
            try:
                card = int(asyncio.run(wait_for_answer(player, message=line +  '\n'.join(str(c) for c in player.cards), message_check=message_check, button_check=button_check, components=generate_buttons(range(1, cards_one_player_has+1)), timeout=game.step_timeout)))
                asyncio.run(player.send('You has choosed the card ' + player.cards[card-1] + '.'))
            except asyncio.TimeoutError:
                card = random.randrange(cards_one_player_has)
                asyncio.run(player.send('You was thinking too much. The card ' + player.cards[card-1] + ' was automatically selected for you.'))
    
            game.discarded_cards.append((player.cards[card-1], player.id))
            discarded_card = card

def request_leader_card():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot, 
                number >= 1, 
                number <= cards_one_player_has)): return True
        return False
        
    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot, 
                number >= 1, 
                number <= cards_one_player_has)): return True
        return False
        
        
    try:
        card = int(asyncio.run(wait_for_answer(game.leader, message='You are a leader now. Choose number of one of your cards:\n' +  '\n'.join(str(c) for c in game.leader.cards), message_check=message_check, button_check=button_check, components=generate_buttons(range(1, cards_one_player_has+1)), timeout=game.step_timeout)))
        asyncio.run(game.leader.send('You has choosed the card ' + game.leader.cards[card-1] + '.'))
    except asyncio.TimeoutError:
        card = random.randrange(cards_one_player_has)
        asyncio.run(game.leader.send('You was thinking too much. The card ' + game.leader.cards[card-1] + ' was automatically selected for you.'))
        
    game.discarded_cards.append((game.leader.cards.pop(card-1), game.leader.id))

def request_players_cards():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot, 
                number >= 1, 
                number <= cards_one_player_has)): return True
        return False
                        
    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot, 
                number >= 1, 
                number <= cards_one_player_has)): return True
        return False
        
        
    for player in players:
        try:
            card = int(asyncio.run(wait_for_answer(player, message='Choose the card you want to... Choose?..:\n' +  '\n'.join(str(c) for c in player.cards), message_check=message_check, button_check=button_check, components=generate_buttons(range(1, cards_one_player_has+1)), timeout=game.step_timeout)))
            asyncio.run(player.send('You has choosed the card ' + player.cards[card-1] + '.'))
        except asyncio.TimeoutError:
            card = random.randrange(cards_one_player_has)
            asyncio.run(player.send('You was thinking too much. The card ' + player.cards[card-1] + ' was automatically selected for you.'))
            
        game.discarded_cards.append((player.cards.pop(card-1), player.id))

def vote_for_target_card_2():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot,  
                number >= 1, 
                number <= cards_one_player_has, 
                game.discarded_cards[int(message.content) - 1][1] != message.author.id)): return True
        return False
        
    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot, 
                number >= 1, 
                number <= cards_one_player_has, 
                game.discarded_cards[int(interaction.component.label) - 1][1] != interaction.user.id)): return True
        return False
        
    
    for player in players:
        try:
            card = int(asyncio.run(wait_for_answer(player, message='Choose the enemy\'s card: \n' + '\n'.join(str(c[0]) for c in game.discarded_cards), message_check=message_check, button_check=button_check, components=generate_buttons(range(1, len(game.discarded_cards)+1)), timeout=step_timeout)))
            asyncio.run(player.send('You has choosed the card ' + game.discarded_cards[card-1][0] + '.'))
        except asyncio.TimeoutError:
            card = random.randint(1, len(players))
            asyncio.run(player.send('You was thinking too much. The card ' + game.discarded_cards[card-1] + ' was automatically selected for you.'))
        
        game.votes_for_card[game.discarded_cards[card - 1][1]] += 1
        player.choosed_card = card

def vote_for_target_card():
    def message_check(message):
        try:
            number = int(message.content)
        except ValueError:
            return False
        if all((not message.author.bot,  
                number >= 1, 
                number <= cards_one_player_has, 
                game.discarded_cards[int(message.content) - 1][1] != message.author.id)): return True
        return False
        
    def button_check(interaction):
        try:
            number = int(interaction.component.label)
        except ValueError:
            return False
        if all((not interaction.user.bot, 
                number >= 1, 
                number <= cards_one_player_has, 
                game.discarded_cards[int(interaction.component.label) - 1][1] != interaction.user.id)): return True
        return False
        
    
    for player in players:
        if player != game.leader:
            try:
                card = int(asyncio.run(wait_for_answer(player, message='Choose the enemy\'s card: \n' + '\n'.join(str(c[0]) for c in game.discarded_cards), message_check=message_check, button_check=button_check, components=generate_buttons(range(1, len(game.discarded_cards)+1)), timeout=step_timeout)))
                asyncio.run(player.send('You has choosed the card ' + game.discarded_cards[card-1][0] + '.'))
            except asyncio.TimeoutError:
                card = random.randint(1, len(players))
                asyncio.run(player.send('You was thinking too much. The card ' + game.discarded_cards[card-1] + ' was automatically selected for you.'))
            
            game.votes_for_card[game.discarded_cards[card - 1][1]] += 1
            player.choosed_card = card

def at_end():
    game_took_time = time.time() - game.game_started_at
    asyncio.run(start.ctx.send('The game took: ' + str(int(game_took_time // 60)) + ' minutes and ' + str(int(game_took_time % 60)) + ' seconds.'))
    
    if len(players) == 2:
        if game.bot_score > game.players_score:
            asyncio.run(start.ctx.send('You lose with score: ' + str(game.players_score)))
        if game.players_score > game.bot_score:
            asyncio.run(start.ctx.send('You win with score: ' + str(game.players_score)))
        else:
            asyncio.run(start.ctx.send('Победила дружба (сырок)!'))
    else:
        asyncio.run(start.ctx.send('The winners: \n' + 
                                   '\n'.join((str(place) + '. ' + str(player) for place, player in enumerate(sorted(players)[:3], start=1)))))

@bot.command()
async def start(ctx):
    start.ctx = ctx
    
    try:
        game.start_game(at_start=at_start, 
                        at_round_start=at_round_start, 
                        request_association=request_association, 
                        show_association=show_association, 
                        request_players_cards_2=request_players_cards_2, 
                        request_leader_card=request_leader_card, 
                        request_players_cards=request_players_cards, 
                        vote_for_target_card_2=vote_for_target_card_2, 
                        vote_for_target_card=vote_for_target_card, 
                        at_end=at_end)
    except TypeError as error:
        await ctx.send('The game cannot start yet. Specify all data and start the game again.')

@bot.command()
async def end(ctx):
    pass            
    
@bot.command(name='pause')
async def pause_game(ctx):
    pass

@bot.command(name='continue')
async def continue_game(ctx):
    pass


bot.run(discord_bot_configuration.TOKEN)