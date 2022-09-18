import random
import collections
import time 
import math

import validators
import vk_api

import game_configuration


include_used_cards = False
game_started = False
step_timeout = 60
used_cards = set()
unused_cards = list()
cards_one_player_has = 6
sourses = set()
players = list()
winning_score = 5
turn = 0
included_types = ('photo', )
excluded_types = ()


class UnexpectedSourse(Exception):
    pass
class NoAnyPosts(Exception):
    pass
class EnvironmentError(Exception):
    pass


class player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
        self.cards = list()
        self.discarded_cards = list()
    def __hash__(self): return self.id
    def __repr__(self): return self.name
    def __str__(self): return self.name
    def __eq__(self, x): return self.id == x
    def __ne__(self, x): return self.id != x
    def __gt__(self, x): return self.score > x
    def __lt__(self, x): return self.score < x
    def __ge__(self, x): return self.score >= x
    def __le__(self, x): return self.score <= x
    
    def reset_features(self):
        self.score = 0
    
    score = 0
    choosed_card = None
    


class Sourse:
    pass

vk_requests = vk_api.VkApi(token=game_configuration.VK_TOKEN).get_api()

class vk(Sourse):
    def __init__(self, link):
        self.link = link
        self.domain = link[link.rfind(r'/')+1:]
        self.included_types = {y for i in included_types if (y := vk.types.get(i))}
        self.excluded_types = {y for i in excluded_types if (y := vk.types.get(i))}
    def __eq__(self, other):
        return self.link == other
    def __ne__(self, other):
        return self.link != other
    def __str__(self):
        return self.link
    def __hash__(self):
        return hash(self.link)
    
    # Change specified types to vk attachment types
    types = {'photo':'photo', 
             'video':'video'}
    
    def get_cards_quantity(self):
        return vk_requests.wall.get(domain=self.domain, count=1)['count']
    
    def set_cards_quantity(self):
        self.cards_num = self.get_cards_quantity()

    def get_random_card(self):
        def exctact_content_from_attachment(attachment):
            if attachment['type'] == 'photo':
                return attachment[attachment['type']]['sizes'][-1]['url']
            elif attachment['type'] == 'video':
                video_id = str(attachment[attachment['type']]['owner_id'])
                video_id += '_' + str(attachment[attachment['type']]['id'])
                return vk_requests.video.get(videos=video_id)['items'][0]['player']
                    
        self.set_cards_quantity()
        if self.cards_num == 0: 
            raise NoAnyPosts
            
        try:
            attachments = vk_requests.wall.get(domain=self.domain, 
                                               offset=random.randrange(self.cards_num), 
                                               count=1)['items'][0]['attachments']
        except KeyError:
            return self.get_random_card()
        
        # If attachments are found, then get the random one
        random.shuffle(attachments)
        for attachment in attachments:
            if attachment['type'] not in self.excluded_types:
                if self.included_types: 
                    if attachment['type'] not in self.included_types:
                        continue
                return exctact_content_from_attachment(attachment)
        
        return self.get_random_card()

class link:
    def __init__(self, link):
        # return what link takes to
        pass


def all_elements_true(iterable, function=lambda x: x):
    """Return True if all the elements processed by the function are True."""
    for i in iterable:
        if not function(i): return False
    return True

def extract_file_extension(filename):
    return filename[filename.rfind('.')+1:]

def create_sourse_object(sourse):
    """Return an object of class "Sourse". 
    
    Process the link to the sourse (email, url, etc.) and create a "Sourse" 
    object that can be used to get some cards."""
    if validators.url(sourse):
        domain_name = sourse[sourse.find('/')+2:]
        domain_name = domain_name[:domain_name.find('/')]
        domain_name = (domain_name := domain_name.split('.'))[math.ceil(len(domain_name)/2)-1]
        
        if domain_name == 'vk':
            return vk(sourse) 
        elif domain_name == 'discord':
            pass
        elif domain_name == 'instagram':
            pass
        elif domain_name == 'tiktok':
            pass
    elif validators.email(sourse):
        pass
    raise UnexpectedSourse('The link format is not supported or an unavailable link is specified.')

def get_random_card(): 
    try:
        return random.choice(list(sourses)).get_random_card()
    except NoAnyPosts:
        return get_random_card()


def empty_function():
    pass

def start_game(at_start=empty_function,  
               at_circle_start=empty_function, 
               at_round_start=empty_function, 
               request_association=empty_function, 
               show_association=empty_function, 
               show_players_cards=empty_function, 
               request_players_cards_2=empty_function, 
               request_leader_card=empty_function, 
               request_players_cards=empty_function, 
               show_discarded_cards=empty_function, 
               vote_for_target_card_2=empty_function, 
               vote_for_target_card=empty_function, 
               at_round_end=empty_function, 
               at_circle_end=empty_function, 
               at_end=empty_function):
    if not sourses: raise TypeError('Sources are not specified.')
    if len(players) <= 1: raise TypeError('There are not enough players to start.')
    
    global leader
    global circle_number
    global round_number
    global discarded_cards
    global votes_for_card
    global game_started_at
    
    game_started_at = time.time()
    bot_score = 0
    players_score = 0
    for player in players: 
        player.reset_features()
    game_started = True
    
    at_start()
    
    circle_number = 1
    while True:
        if not game_started: break
        
        at_circle_start()
        
        # Hand out cards
        if len(players) >= 3:
            for player in players:
                player.cards = list()
                for i in range(cards_one_player_has-1):
                    player.cards.append(get_random_card())
                
        round_number = 1
        for leader in players:
            if not game_started: break
            
            at_round_start()
            
            votes_for_card = collections.defaultdict(int)
            discarded_cards = list()
            round_association = None 
            # Add missed cards
            if len(players) == 2:
                for player in players:
                    player.cards = [get_random_card() for i in range(cards_one_player_has)]
            else:
                for player in players:
                    player.cards.append(get_random_card())
            
            # Each player discards cards to the common deck
            if len(players) == 2:
                # Discard the bot's card
                discarded_cards.append((get_random_card(), None))
                request_association()
                show_association()
                show_players_cards()
                request_players_cards_2()
            else:
                if len(players) == 3:
                    for i in range(2):
                        discarded_cards.append((get_random_card(), None))
                show_players_cards()
                request_leader_card()
                request_association()
                show_association()
                request_players_cards()
            
            random.shuffle(discarded_cards)
            
            # Each player votes for the target card
            show_discarded_cards()
            if len(players) == 2:
                vote_for_target_card_2()
            else:
                vote_for_target_card()
            
            # Score
            if len(players) == 2:
                if votes_for_card[None] == 2:
                    players_score += 2
                elif votes_for_card[None] == 1:
                    players_score += 1
                    bot_score += 1
                elif votes_for_card[None] == 0:
                    bot_score += 3 
            else:
                if votes_for_card[leader.id] not in (0, len(players)):
                    leader.score += 3
                    for player in players:
                        if player != leader:
                            if discarded_cards[player.choosed_card - 1][0] == leader.id:
                                player.score += 3
                    for player in players:
                        player.score += votes_for_card[player.id]
            
            at_round_end()
            
            round_number += 1
            
        at_circle_end()
        
        circle_number += 1
        
        # Check for victory
        if len(players) == 2:
            if max(bot_score, players_score) >= winning_score:
                game_started = False
        else:
            if all_elements_true(players, lambda p: not p.score < winning_score):
                game_started = False
    
    at_end()


def main():
    pass

if __name__ == '__main__':
    main()