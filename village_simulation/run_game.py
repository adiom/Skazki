#!/usr/bin/env python3
"""
Запуск игровой демонстрации симуляции деревни
"""

from village_simulation.game.game import VillageGame

def main():
    game = VillageGame()
    game.run()

if __name__ == "__main__":
    main() 