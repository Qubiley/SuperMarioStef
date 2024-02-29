import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from dungeon import Dungeon
from ui import UI

#test

class Game:
    def __init__(self):
        # game attributes
        self.max_level = 5
        self.max_health = 100
        self.current_health = 100
        self.coins = 0
        # audio
        self.level_bg_music = pygame.mixer.Sound('../audio/Ground Theme.mp3')
        self.overworld_bg_music = pygame.mixer.Sound('../audio/Underground.mp3')
        self.overworld_bg_music.set_volume(0.5)
        self.level_bg_music.set_volume(0.5)

        # overworld creation
        self.overworld = Overworld(5, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.overworld_bg_music.play(loops=-1)

        # user interface
        self.ui = UI(screen)

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_overworld, self.change_coins, self.change_health, self.create_dungeon)
        self.status = 'level'
        self.overworld_bg_music.stop()
        self.level_bg_music.play(loops=-1)

    def create_dungeon(self, current_level, power):
        self.dungeon = Dungeon(current_level, screen, self.create_level, self.change_coins, self.change_health, power)
        self.status = 'dungeon'
        self.level_bg_music.stop()

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.overworld_bg_music.play(loops=-1)
        self.level_bg_music.stop()

    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.current_health += amount

    def check_game_over(self):
        if self.current_health <= 0:
            self.current_health = 100
            self.coins = 0
            self.max_level = 0
            self.overworld = Overworld(0, self.max_level, screen, self.create_level)
            self.status = 'overworld'
            self.level_bg_music.stop()
            self.overworld_bg_music.play(loops=-1)

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        elif self.status == 'level':
            self.level.run()
            self.ui.show_health(self.current_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()
        elif self.status == 'dungeon':
            self.dungeon.run()
            self.ui.show_health(self.current_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()


pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()
pygame.display.set_caption("SuperMarioStef")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill('black')
    game.run()

    pygame.display.update()
    clock.tick(60)
