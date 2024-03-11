"""
Main
Wessel Martens
7-Jan-2024
"""

from perudo_game import *

game = Perudo(dice=5, players=["Wessel", "Floris", "Jelte"], bots=["StrategyManual", "StrategyBotZero", "StrategyBotZero"], dark=False)
game.play_game()
