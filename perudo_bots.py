"""
Perudo bots
Wessel Martens
7-Jan-2024

Instructions:
    Create a strategy X by defining a class StrategyX(Bot) as a child class of Bot
    Write a bet function that returns a bet string which the Bot will play in the game
"""

import numpy as np
from perudo_game import *

# Parent class for all bots
class Bot():
    def __init__(self, perudo_game, perudo_round, perudo_player):
        self.game = perudo_game
        self.round = perudo_round
        self.player = perudo_player
        
        self.load_game_info()
        self.load_round_info()
    
    def load_game_info(self):
        self.amount_players = len(self.game.players)
        self.amount_dice = len(self.round.dice)
        
    def load_round_info(self):
        self.own_dice = self.player.show_dice()
        self.own_dice_amount = self.player.count_dice()
        self.round_bets = self.round.bets
        self.active_bet = (self.round_bets or [None])[-1]

    def compose_bet_string(self, count, roll):
        return f"{count}x{roll}"

    def decompose_bet_string(self, bet_string):
        return map(int, bet_string.split("x"))
      
    def bet(self):
        return input("Strategy is missing bet function - {self.player.get_name()} manually bets:")

# Demo strategy bots
class StrategyManual(Bot):
    def __init__(self, perudo_game, perudo_round, perudo_player):
        super().__init__(perudo_game, perudo_round, perudo_player)
    
    def bet(self):
        return input(f"{self.player.get_name()} manually bets: ")

class StrategyBluff(Bot):
    def __init__(self, perudo_game, perudo_round, perudo_player):
        super().__init__(perudo_game, perudo_round, perudo_player)
        
    def bet(self):
        if self.active_bet:
            bet = "B"
        else:
            bet_count = 1
            bet_roll = np.random.choice([1,2,3,4,5,6])
            bet = self.compose_bet_string(bet_count, bet_roll)
        print(f"{self.player.get_name()}'s bot bets: {bet}")
        return bet

class Strategy1up(Bot):
    def __init__(self, perudo_game, perudo_round, perudo_player):
        super().__init__(perudo_game, perudo_round, perudo_player)
    
    def bet(self):
        if self.active_bet:
            active_count, active_roll = self.decompose_bet_string(self.active_bet)
            bet_count = active_count + 1
            bet_roll = active_roll
        else:
            bet_count = 1
            bet_roll = np.random.choice([1,2,3,4,5,6])
        bet = self.compose_bet_string(bet_count, bet_roll)
        print(f"{self.player.get_name()}'s bot bets: {bet}")
        return bet


