import pygame
from spritesheet import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, data):
        super().__init__()
        self.direction = direction
        self.x = x + (48*self.direction)
        self.y = y
        self.timer = 0
        self.element = data['element']
        self.speed = data['speed']
        self.damage = data['damage']
        self.lifetime = data['lifetime']
        self.size = data['size']
        self.caster = data['caster']
        self.spritesheets = {
            'start': Spritesheet(f"Images/Spritesheets/spells/{data['name']}/start/start"),
            'travel': Spritesheet(f"Images/Spritesheets/spells/{data['name']}/travel/travel"),
            'impact': Spritesheet(f"Images/Spritesheets/spells/{data['name']}/impact/impact")
        }
        self.set_state('start')

        self.spritesheet.x = self.x
        self.spritesheet.y = self.y
        w, h = self.size
        self.rect = pygame.Rect(self.x, self.y, w, h)
        if self.direction == -1:
            for sheet in self.spritesheets.values():
                for i in range(len(sheet.images)):
                    sheet.images[i] = pygame.transform.flip(sheet.images[i], True, False)
    
    def set_state(self, state):
        self.state = state
        self.spritesheet = self.spritesheets[self.state]
        self.spritesheet.index = 0
        self.spritesheet.x = self.x
        self.spritesheet.y = self.y


    def start(self):
        if self.spritesheet.index == len(self.spritesheet.images) - 1:
            self.set_state('travel')


    def travel(self, level):
        self.x += self.speed * self.direction
        self.rect.x = self.x
        self.spritesheet.x = self.x
        self.spritesheet.y = self.y

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.set_state('impact')

        tile = level.check_collision(self.rect)
        if tile:
            self.x += self.speed * self.direction
            self.rect.x = self.x
            self.spritesheet.x = self.x
            self.spritesheet.y = self.y
            self.set_state("impact")
            return True

        entity = level.check_entity_collisions(self)
        if entity and entity != self.caster:
            if hasattr(entity, "take_damage"):
                entity.take_damage(self.damage, self.element)  
            self.x += self.speed * self.direction
            self.rect.x = self.x
            self.spritesheet.x = self.x
            self.spritesheet.y = self.y
            self.set_state("impact")
            return True
        return False


    def impact(self):
        if self.spritesheet.index == len(self.spritesheet.images) - 1:
            return True
        return False

    def update(self, level):
        match self.state:
            case 'start':  self.start()
            case 'travel': self.travel(level)
            case 'impact': return self.impact()

    def draw(self, screen, camera):
        self.spritesheet.draw(screen, camera)