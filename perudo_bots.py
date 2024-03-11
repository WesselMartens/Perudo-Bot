"""
Perudo bots
Wessel Martens
11-Mar-2024

Instructions:
    Create a strategy X by defining a class StrategyX(Bot) as a child class of Bot
    Write a bet function that returns a bet string which the Bot will play in the game
    Assign "StrategyX" to your player in the game
"""

import random
import numpy as np
from math import comb
from perudo_game import *
np.set_printoptions(suppress=True)

# Parent class for all bots
class Bot():
    def __init__(self, perudo_game, perudo_round, perudo_player):
        self.game = perudo_game
        self.round = perudo_round
        self.player = perudo_player
        
        self.load_game_info()
        self.load_round_info()
        self.load_bets_info()
        self.load_next_player_info()
        
        self.compute_valid_bets()
        self.compute_probability_grids()

    # Load information functions
    def load_game_info(self):
        self.amount_players = len(self.game.players)
        self.amount_dice = len(self.round.dice)
        
    def load_round_info(self):
        self.own_dice = self.player.show_dice()
        self.amount_own_dice = self.player.count_dice()
        self.amount_other_dice = self.amount_dice - self.amount_own_dice
    
    def load_bets_info(self):
        self.round_bet_strings = self.round.bet_strings
        self.round_bet_dice_amounts = self.round.bet_dice_amounts

        self.active_bet_string = (self.round_bet_strings or [None])[-1]
        self.active_bet_dice_amount = (self.round_bet_dice_amounts or [None])[-1]
     
    def load_next_player_info(self):
        self.next_player = self.game.players[(self.game.turn+1) % len(self.game.players)]
        self.next_player_dice_amount = self.next_player.count_dice()

    # Compute bet statistics functions
    def compute_valid_bets(self):
        if self.active_bet_string == None:
            grid = np.full([6, self.amount_dice+1], True)
            grid[:, 0] = False
        else:
            active_count, active_roll = self.decompose_bet_string(self.active_bet_string)
            row_idx, col_idx = np.indices((6, self.amount_dice+1))
            
            if active_roll == 1:
                c1 = (col_idx > active_count) & (row_idx == 0) # count up, roll perudo
                c2 = (col_idx > 2*active_count) # up to anything, count*2
                c3 = False
            else:
                c1 = (col_idx > active_count) # count up, roll anything
                c2 = (col_idx == active_count) & (row_idx > active_roll-1) # count same, roll up
                c3 = (col_idx >= int(np.ceil(active_count/2))) & (row_idx == 0) # down to perudo, count/2
                
            grid = np.where(c1 | c2 | c3, True, False)

        self.valid_bets = grid
        
    def compute_probability_grids(self): # to be vectorized
        grid = np.zeros([6, self.amount_dice+1])
        for roll in [1,2,3,4,5,6]:
            own_count = np.count_nonzero((self.own_dice == roll) | (self.own_dice == 1))
            for count in range(0, self.amount_dice+1):
                if count < own_count or count > self.amount_other_dice + own_count:
                    p_roll_count = 0
                else:
                    other_count = count - own_count
                    if roll == 1:
                        p_roll_count = comb(self.amount_other_dice, other_count) * (1/6)**other_count * (5/6)**(self.amount_other_dice-other_count)
                    else:
                        p_roll_count = comb(self.amount_other_dice, other_count) * (1/3)**other_count * (2/3)**(self.amount_other_dice-other_count)
                grid[roll-1, count] = p_roll_count
        self.exact_probability_grid = grid
        self.cumulative_probability_grid = np.cumsum(grid[:,::-1], axis=1)[:,::-1]    

    # Auxiliary functions
    def compose_bet_string(self, count, roll):
        return f"{count}x{roll}"

    def decompose_bet_string(self, bet_string):
        return map(int, bet_string.split("x"))
      
    def bet(self):
        return input("Strategy is missing bet function - player manually bets: ")

# Demo strategy bots
class StrategyManual(Bot): # asks user to place a manual bet
    def __init__(self, perudo_game, perudo_round, perudo_player):
        super().__init__(perudo_game, perudo_round, perudo_player)
    
    def bet(self):
        return input(f"{self.player.get_name()} manually bets: ")

class StrategyBluff(Bot): # calls bluff on any bet
    def __init__(self, perudo_game, perudo_round, perudo_player):
        super().__init__(perudo_game, perudo_round, perudo_player)
        
    def bet(self):
        if self.active_bet_string:
            bet = "B"
        else:
            bet_count = 1
            bet_roll = np.random.choice([1,2,3,4,5,6])
            bet = self.compose_bet_string(bet_count, bet_roll)
        print(f"{self.player.get_name()}'s bot bets: {bet}")
        return bet

class Strategy1up(Bot): # increases the count on any bet
    def __init__(self, perudo_game, perudo_round, perudo_player):
        super().__init__(perudo_game, perudo_round, perudo_player)
    
    def bet(self):
        if self.active_bet_string:
            active_count, active_roll = self.decompose_bet_string(self.active_bet_string)
            bet_count = active_count + 1
            bet_roll = active_roll
        else:
            bet_count = 1
            bet_roll = np.random.choice([1,2,3,4,5,6])
        bet = self.compose_bet_string(bet_count, bet_roll)
        print(f"{self.player.get_name()}'s bot bets: {bet}")
        return bet

# Proper strategy bot
class StrategyZero(Bot):
    def __init__(self, perudo_game, perudo_round, perudo_player):
        super().__init__(perudo_game, perudo_round, perudo_player)
        
    def bet(self):
        
        bet_proposal = self.compute_bet_proposal(0.6)
        bet_final = self.determine_final_bet(bet_proposal)
        
        return bet_final
    
    def compute_bet_proposal(self, threshold):
        
        valid_probability_grid = np.where(self.valid_bets, self.cumulative_probability_grid, 0)
        good_probability_grid = np.where((valid_probability_grid == valid_probability_grid.max()) | (valid_probability_grid > threshold), valid_probability_grid, 0)
        
        xs,ys = np.nonzero(good_probability_grid) # note: can be empty if no bets have probability
        indexes = list(zip(xs, ys))
        index = random.choice(indexes)
        
        bet_count, bet_roll = self.count_roll_from_index(index)
        bet_string = self.compose_bet_string(bet_count, bet_roll)
        
        return bet_string
    
    def determine_final_bet(self, bet_proposal):
        
        if self.active_bet_string == None:
            final_bet = bet_proposal
        else:
            active_count, active_roll = self.decompose_bet_string(self.active_bet_string)
            active_bet_prob = self.get_bet_probability(active_count, active_roll)
            
            proposal_bet_count, proposal_bet_roll = self.decompose_bet_string(bet_proposal)
            proposal_bet_prob = self.get_bet_probability(proposal_bet_count, proposal_bet_roll)
        
            # Compare max bet to active bet
            c1 = (active_bet_prob < 0.1)
            c2 = (proposal_bet_prob < 0.1)
            c3 = (proposal_bet_prob < 0.55) and (active_bet_prob < 0.5) and (proposal_bet_prob < active_bet_prob - 0.2)
            c4 = (active_bet_prob < 0.3) and (proposal_bet_prob < active_bet_prob + 0.2)
            
            if c1 or c2 or c3 or c4:
                final_bet = "B"
            else:
                final_bet = bet_proposal
            print(f"{self.player.get_name()}'s bot bets: {final_bet}")
            print(self.active_bet_string, active_bet_prob)
            print(bet_proposal, proposal_bet_prob)
        
        return final_bet
    
    def get_bet_probability(self, count, roll):
        return self.cumulative_probability_grid[roll-1, count]
    
    def count_roll_from_index(self, index):
        return index[1], index[0]+1


