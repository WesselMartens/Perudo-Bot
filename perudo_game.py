"""
Perudo game
Wessel Martens
7-Jan-2024
"""

import numpy as np
import perudo_bots as perudo_bots
from itertools import cycle, islice

class Player():
    def __init__(self, name, bot, amount_dice):
        self.name = name
        self.bot = bot
        self.dice = np.zeros(amount_dice)
        self.alive = True

    def is_alive(self):
        return self.alive

    def get_name(self):
        return self.name
    
    def count_dice(self):
        return len(self.dice)
    
    def show_dice(self):
        return self.dice
    
    def roll_dice(self):
        self.dice = np.random.choice([1,2,3,4,5,6], size=self.count_dice())
    
    def reset_dice(self):
        self.dice = np.zeros(self.count_dice())
      
    def gain_dice(self):
        self.dice = np.append(self.dice, 0)
        self.reset_dice()
        
    def lose_dice(self):
        self.dice = self.dice[:-1]
        if self.count_dice() > 0:
            self.reset_dice()
        else:
            self.alive = False
            print(f"Player {self.get_name()} eliminated")

class Round():
    def __init__(self, game):
        self.game = game
        self.live = True
        
        self.dice = np.array([])
        self.counts = {}
        
        self.bets = []
        
    def play(self):
        input(f"\nPress a key to play round: {self.game.round_number}")
        self.roll_count_dice()
        self.run_player_turns()
        self.update_players()
    
    def roll_count_dice(self):
        for player in self.game.players:
            player.roll_dice()
            self.dice = np.append(self.dice, player.show_dice())

        for roll in [1,2,3,4,5,6]:
            roll_count = np.count_nonzero((self.dice == roll) | (self.dice == 1))
            self.counts[roll] = roll_count

    def run_player_turns(self):
        memory_player, memory_bet = None, None
        round_cycle = list(islice(cycle(self.game.players), self.game.turn, 100))
        for player in round_cycle:
            if self.live == True:
                if self.game.dark: print("\n"*25)
                print("\nBets this round: ", *self.bets)
                print(f"{player.get_name()} has dice:", player.show_dice())
                
                # Invoke bot
                PlayerBot = getattr(perudo_bots, player.bot)
                bot = PlayerBot(self.game, self, player)
                player_bet = bot.bet()
                
                memory_player, memory_bet = self.evaluate_turn(player, player_bet, memory_player, memory_bet)
                self.bets.append(player_bet)
    
    def update_players(self):
        for player in self.game.players:
            if not player.is_alive():
                self.game.players.remove(player)
                if len(self.game.players) == 1:
                    self.game.game_over = True
        print("Round over")
                
    def validate_turn(self, player_bet, memory_bet):
        if memory_bet == None:
            if self.check_bet_string(player_bet):
                player_count, player_roll = map(int, player_bet.split("x"))
                c1 = (player_count <= self.game.amount_dice * self.game.amount_players)
                c2 = (player_roll in [1,2,3,4,5,6])
                if c1 and c2:
                    return True
        else:
            if player_bet == "B" or player_bet == "E":
                return True
            elif self.check_bet_string(player_bet):
                player_count, player_roll = map(int, player_bet.split("x"))
                memory_count, memory_roll = map(int, memory_bet.split("x"))
                c1 = (player_count <= self.game.amount_dice * self.game.amount_players)
                c2 = (player_roll in [1,2,3,4,5,6])
                if memory_roll == 1:
                    c3 = (player_count > memory_count and player_roll == 1)
                    c4 = (player_count > 2*memory_count and player_roll > 1)
                    c5 = False
                else:
                    c3 = (player_count > memory_count)
                    c4 = (player_count == memory_count and player_roll > memory_roll)
                    c5 = (player_count >= int(np.ceil(memory_count/2)) and player_roll == 1)
                if c1 and c2 and (c3 or c4 or c5):
                    return True
        return False
    
    def evaluate_turn(self, player, player_bet, memory_player, memory_bet):
        if player_bet == "B":
            if self.check_bluff(memory_bet):
                print(f"\nBluff bet correct! Player {memory_player.get_name()} loses dice.")
                memory_player.lose_dice()
                self.game.turn -= 1
            else:
                print(f"\nBluff bet incorrect! Player {player.get_name()} loses dice.")
                player.lose_dice()
            self.show_roll_count()
            self.live = False
        elif player_bet == "E":
            if self.check_equal(memory_bet):
                print(f"\nEqual bet correct! Player {player.get_name()} gains dice.")
                player.gain_dice()
            else:
                print(f"\nEqual bet incorrect! Player {player.get_name()} loses dice.")
                player.lose_dice()
            self.show_roll_count()
            self.live = False
        else:
            memory_player = player
            memory_bet = player_bet
            self.game.turn += 1
        return memory_player, memory_bet
        
    def show_roll_count(self):
        for roll in self.counts:
            if roll == 1:
                print(f"Dice {roll} had count: {self.counts[roll]}")
            else:
                print(f"Dice {roll} had count: {self.counts[roll]} ({self.counts[roll]-self.counts[1]}+{self.counts[1]})")
              
    def check_bluff(self, bet):
        count, roll = map(int, bet.split("x"))
        if self.counts[roll] < count:
            return True
        else:
            return False
    
    def check_equal(self, bet):
        count, roll = map(int, bet.split("x"))
        if self.counts[roll] == count:
            return True
        else:
            return False
    
    def check_bet_string(self, bet):
        try:
            count, roll = map(int, bet.split("x"))
        except:
            return False
        else:
            return True

class Perudo():
    def __init__(self, dice, players, bots, dark=True):
        self.dark = dark
        
        self.amount_dice = dice
        self.amount_players = len(players)
        
        self.game_over = False
        self.round_number = 0
        self.turn = 0
        
        self.players = [Player(name, bot, dice) for name, bot in zip(players, bots)]
        self.round = None
    
    def play_game(self):
        self.welcome()
        while self.game_over == False:
            self.round_number += 1
            self.play_round()
            self.summary()
        print(f"Game over - Player {self.players[0].get_name()} wins Perudo!")
    
    def play_round(self):
        self.round = Round(self)
        self.round.play()
    
    def welcome(self):
        print("Welcome to Perudo!")
        print("Each turn, play either \"NxM\" for N dice with M pips, \"B\" for bluff or \"E\" for equal.")
        print("\nInitialised game with players:")
        for player in self.players:
            print(f"{player.get_name()}: {player.count_dice()} dice")
        print("Good luck!")

    def summary(self):
        print("\nOverview of current game:")
        print(f"Rounds played: {self.round_number}")
        for player in self.players:
            print(f"{player.get_name()}: {player.count_dice()} dice")
            
if __name__ == '__main__':
    yes_or_no = input("Do you want to play Perudo? y/n ")
    if yes_or_no == "y":
        dice = int(input("Please provide a number of dice: "))
        players = input("Please provide player names separated by a space: ").split()
        bots = ["StrategyManual"]*len(players)
        print()
        perudo = Perudo(dice, players, bots)
        perudo.play_game()
    else:
        print("Have a nice day!")
    

