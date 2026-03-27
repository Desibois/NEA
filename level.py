import pygame
import os
from spritesheet import *
from tiles import *
from spells import *

class Level:

    def __init__(self, element, screen, directory, entities):
        self.element = element # Elementally themed level
        self.screen = screen
        self.entities = entities # All sprites that are presen on  the level
        self.tile_sheet = Spritesheet(f'{directory}/tileset') # tile sheet for tile map
        self.tile_map = Tilemap( f'{directory}/map.json', self.tile_sheet) # tile map for rendering tiles on screen
        self.decorative_map =  Tilemap(f'{directory}/map.json', self.tile_sheet, 1) # Decorative elements for level
        self.backgrounds = []

        for background_path in sorted(os.listdir(f'{directory}/backgrounds')): # Loop through paths to background images
            path = f'{directory}/backgrounds/{background_path}'
            if path.endswith('png'):
                background = pygame.image.load(path).convert_alpha()
                self.scale_background(background)
        
        self.get_collision_tiles()
    

    def update_entities(self, player):

        boss = None
        for entity in self.entities:
            if hasattr(entity, "final_phase") and entity.final_phase:
                boss = entity
                break
        
        if boss:
            player.end_boss = True
            self.handle_boss(boss, player)
        else: player.end_boss = False

        for entity in self.entities:
            if hasattr(entity, "attack_range") and player.state != 'dead':
                entity.check_attack_range(player)

            if hasattr(entity, "spell") and entity.spell:
                data = entity.spell

                projectile = Projectile(entity.x, entity.y, entity.direction, data)
                self.entities.append(projectile)
                entity.spell = {}
                
            if hasattr(entity, "update"):
                if entity.update(self): self.entities.remove(entity)

    
    def handle_boss(self, boss, player):
        typed = player.input_phrase
        phrase = boss.final_phrase

        if not phrase.startswith(typed):
            boss.health = int(boss.max_health * 0.1)
            boss.final_phase = False
            boss.player_input = ""
            player.input_phrase = ""
            return

        if typed == phrase:
            boss.final_phrase_complete = True
            boss.set_state("dying")
            return

        boss.player_input = typed

    def check_entity_collisions(self, object):
        for entity in self.entities:
            if hasattr(entity, "rect") and (not hasattr(entity, 'caster')) and object.rect.colliderect(entity.rect):
                return entity
        return None

    
    def get_collision_tiles(self):
        self.collision_tiles = []
        self.map_y_offset = self.screen.get_height() - self.tile_map.map_height
        
        for tile in self.tile_map.tiles:
            tile_rect = pygame.Rect(tile.rect.x, tile.rect.y + self.map_y_offset, self.tile_map.tile_size, self.tile_map.tile_size)
            self.collision_tiles.append(tile_rect)
    

    def check_collision(self, rect):
        for tile_rect in self.collision_tiles:
            if rect.colliderect(tile_rect):
                return tile_rect
        return None
    
    def is_grounded(self, rect):
        foot_rect = pygame.Rect(rect.x + 4, rect.bottom + 1, rect.width - 8, 2)
        for tile_rect in self.collision_tiles:
            if foot_rect.colliderect(tile_rect):
                return True
        return False


    def scale_background(self, background):
        screen_height = self.screen.get_height()
        background_height = background.get_height()
        background_width = background.get_width()
        if background_height != screen_height: # Scale background to fit the height of the screen
                scale_factor = screen_height / background_height
                new_width = int(background_width * scale_factor) # Increase the width proportionally to the height to maintain dimensions
                self.backgrounds.append(pygame.transform.scale(background, (new_width, screen_height)))


    def draw(self, camera):
        self.screen.fill("#006994")

        for i in range(len(self.backgrounds)):
            background = self.backgrounds[i]
            width = background.get_width()
            parallax = 2 * (i + 1) / len(self.backgrounds)
            drift = (i + 1) * 5
            total_offset = -(camera.offset_x * parallax) - (pygame.time.get_ticks() * drift * 0.01)
            start_x = int(total_offset % width) - width
            for x in range(start_x, self.screen.get_width(), width):
                self.screen.blit(background, (x, 0))


        map_y = self.screen.get_height() - self.tile_map.map_height
        self.screen.blit(self.tile_map.map_surface, (-camera.offset_x, map_y - camera.offset_y))
        for entity in self.entities:
                entity.draw(self.screen, camera) 
        map_y = self.screen.get_height() - self.decorative_map.map_height
        self.screen.blit(self.decorative_map.map_surface, (-camera.offset_x, map_y - camera.offset_y))
        