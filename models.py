#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jack River'

from random import shuffle, randint
from itertools import cycle

CARD_2_VALUE = 13
CARD_A_VALUE = 12


class Card():
    SUITS = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
    VALUES = range(3, 14)  # value 12 = 'A' | value 13 = '2'

    def __init__(self, suit, value):
        if (suit in self.SUITS or suit == 'Joker') and value in self.VALUES:
            self.suit = suit
            self.value = value
        else:
            raise AttributeError()

    def print_card(self):
        print('%s %d\n' % (self.suit, self.value))


def cards_in_same_value(cards):
    not_joker_cards = []
    has_joker = False
    for card in cards:
        if card.suit == 'Joker':
            has_joker = True
        else:
            not_joker_cards.append(card)

    if has_joker and not_joker_cards[0].value == CARD_2_VALUE:
        # joker cant replace 2
        raise AttributeError()
    elif has_joker:
        return cards_in_same_value(not_joker_cards)
    else:
        value = not_joker_cards[0].value
        result = True
        for card in cards:
            if not card.value == value:
                result = False

        return result


def cards_in_sequence_pair_value(cards):
    return True


def compare_cards(a, b):
    return a.value > b.value


def cards_in_sequence_value(cards):
    not_joker_cards = []
    has_joker = False
    joker_count = 0
    for card in cards:
        if card.suit == 'Joker':
            has_joker = True
            joker_count += 1
        else:
            not_joker_cards.append(card)

    if has_joker and not_joker_cards[0].value == CARD_2_VALUE:
        # joker cant replace 2
        raise AttributeError()
    elif has_joker:
        not_joker_cards = sorted(not_joker_cards, cmp=compare_cards)
        return ((not_joker_cards[-1].value - not_joker_cards[0].value) + 1) == (len(not_joker_cards) + joker_count)
    else:
        not_joker_cards = sorted(not_joker_cards, cmp=compare_cards)
        return (not_joker_cards[-1].value - not_joker_cards[0].value + 1) == len(not_joker_cards)


def cards_in_allowed_patterns(cards):
    if len(cards) == 1:
        # single card
        return 1
    elif len(cards) == 2:
        # pair of same cards
        return cards[0].value == cards[1].value
    elif len(cards) == 3 and cards_in_same_value(cards):
        # three same cards
        return True
    elif len(cards) == 4 and cards_in_same_value(cards):
        # bomb
        return True
    elif len(cards) >= 3 and cards_in_sequence_value(cards):
        # sequence of cards >= 3
        return True
    elif len(cards) >= 4 and len(cards) % 2 == 0 and cards_in_sequence_pair_value(cards):
        # sequence pair of cards >= 4
        return True


class Deck():

    def __init__(self):
        self.cards = []

        for suit in Card.SUITS:
            for value in Card.VALUES:
                self.cards.append(Card(suit, value))

        # insert two joker cards
        self.cards.extend([Card('Joker', 3), Card('Joker', 3)])

    def shuffle(self):
        shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()


class Player():

    def __init__(self, nickname):
        self.nickname = nickname
        self.hand_cards = []

    def take_card(self, card):
        self.hand_cards.append(card)

    def play(self, play_callback):
        print('Hello %s, you have following cards:\n')
        index = 0
        for card in self.hand_cards:
            print('%d: ' % index)
            index += 1
            card.print_card()

        played_cards = []
        input_numbers = [int(x) for x in raw_input('Choose some cards to play(index seperated by spaces): ').split(' ')]
        input_numbers = set(sorted(input_numbers, reverse=True))
        for index in input_numbers:
            if index < len(self.hand_cards):
                played_cards.append(self.hand_cards.pop(index))
            else:
                raise IndexError('Index out of range!')

        if not play_callback(played_cards, self):
            # if played invalid cards, then try again
            print('Invalid played cards, try again!')
            self.hand_cards.extend(played_cards)
            self.play(play_callback)


class Game():

    def __init__(self):
        self.deck = Deck()
        self.dealer = None
        self.all_players = []
        self.players = []
        self.previous_played_cards = None
        self.winner = None

    def valid_game(self):
        """ if it is a valid game to start
        """
        return len(self.all_players) >= 2

    def join_game(self, player):
        """ player join current game
        """
        self.players.append(player)
        self.all_players.append(player)

    def decide_dealer(self):
        """ choose a player become dealer randomly
        """
        self.dealer = self.players.pop(randint(0, len(self.all_players) - 1))

    def deal(self):
        """ deal initial cards
        """
        for i in range(0, 6):
            self.dealer.take_card(self.deck.deal_card())
        for player in self.players:
            for i in range(0, 5):
                player.take_card(self.deck.deal_card())

    def decide(self, cards):
        """ decide if player give out cards following the game rules
        """
        if not self.previous_played_cards and cards_in_allowed_patterns(cards):
            # initial
            self.previous_played_cards = cards
            return True

        if len(cards) == 1 and len(self.previous_played_cards) == 1:
            # single card
            if len(self.previous_played_cards) == 1 and cards[0].value == self.previous_played_cards[0].vale + 1:
                self.previous_played_cards = cards
                return True
            else:
                return False
        elif len(cards) == 2 and len(self.previous_played_cards) == 2:
            if cards_in_same_value(cards) and cards_in_same_value(self.previous_played_cards) and cards[0].value == self.previous_played_cards[0].value + 1:
                self.previous_played_cards = cards
                return True
            else:
                return False
        if len(cards) == 3 and len(self.previous_played_cards) == 3 and cards_in_same_value(cards) and cards_in_same_value(self.previous_played_cards):
            if cards[0].value == self.previous_played_cards[0].value:
                self.previous_played_cards = cards

    def is_game_ended(self):
        """ decide if current game is ended

        Condition:
            deck is empty or one of the player played out all cards
        """
        game_ended = False
        for player in self.all_players:
            if len(player.hand_cards) == 0:
                # played all cards
                game_ended = True
                self.winner = player

        if len(self.deck.cards) == 0:
            game_ended = True
            self.winner = None

        return game_ended

    def play_callback(self, cards, player):
        """ play callback function after player give out cards
        """
        return self.decide(cards)

    def start(self):
        """ start a game
        """
        if not self.valid_game():
            raise AttributeError('Invalid game!')

        self.decide_dealer()
        self.deal()

        for player in cycle(self.all_players):
            if self.is_game_ended():
                break

            player.play(self.play_callback)

        if self.winner:
            print('Winner is %s!' % self.winner.nickname)
        else:
            print('A tie!')


