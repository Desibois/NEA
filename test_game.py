import pygame
from spritesheet import *
from tiles import *
from level import *
from player import *

pygame.init()
width, height = 1500, 1000
screen = pygame.display.set_mode((width, height))

player = Player()
water_level = Level('water', screen, 'Images/Levels/Water', [player.spritesheets[player.state]])
running = True
clock = pygame.time.Clock()
FPS = 50

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    player.handle_input()
    player.update_position(water_level)
    
    water_level.sprites = [player.spritesheets[player.state]]
    water_level.draw()

    
    pygame.display.flip()