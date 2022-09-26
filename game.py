import collections
import random
import time

import game_exceptions
import game_rules

game_started = False
used_cards = set()
unused_cards = list()
sources = set()
players = list()

leader = None
circle_number = None
round_number = None
discarded_cards = None
votes_for_card = None
game_started_at = None
bot_score = None
players_score = None
round_association = None


class Player:
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
    chosen_card = None


def all_elements_true(iterable, function=lambda x: x):
    """Return True if all the elements processed by the function are True."""
    for i in iterable:
        if not function(i):
            return False
    return True


def get_random_card():
    try:
        return random.choice(list(sources)).get_random_card()
    except game_exceptions.NoAnyPosts:
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
    if not sources:
        raise TypeError('Sources are not specified.')
    if len(players) < 2:
        raise TypeError('There are not enough players to start.')

    global leader
    global circle_number
    global round_number
    global discarded_cards
    global votes_for_card
    global game_started_at
    global bot_score
    global players_score
    global game_started

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
                for i in range(game_rules.cards_one_player_has - 1):
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
                    player.cards = [get_random_card() for i in range(game_rules.cards_one_player_has)]
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

            # Scoring
            if len(players) == 2:
                if votes_for_card[None] == 2:
                    players_score += 2
                elif votes_for_card[None] == 1:
                    players_score += 1
                    bot_score += 1
                elif votes_for_card[None] == 0:
                    bot_score += 3
            else:
                if votes_for_card[leader.id] == 0:
                    for player in players:
                        player.score += votes_for_card[player.id]
                else:
                    if votes_for_card[leader.id] != len(players):
                        leader.score += 3
                    for player in player:
                        if player != leader:
                            if discarded_cards[player.chosen_card - 1][1] == leader.id:
                                player.score += 3

            at_round_end()

            round_number += 1

        at_circle_end()

        circle_number += 1

        # Check for victory
        if len(players) == 2:
            if max(bot_score, players_score) >= game_rules.winning_score:
                game_started = False
        else:
            if not all_elements_true(players, lambda p: p.score < game_rules.winning_score):
                game_started = False

    at_end()


def main():
    pass


if __name__ == '__main__':
    main()
