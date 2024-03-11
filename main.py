"""
Main
Wessel Martens
7-Jan-2024
"""

from perudo_game import *

game = Perudo(dice=5, players=["Wessel", "Floris", "Jelte"], bots=["StrategyManual", "StrategyZero", "StrategyZero"], dark=True)
game.play_game()
