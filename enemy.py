import pygame
import math
import random
from spritesheet import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, health):
        super().__init__()
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, width, height)

        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 1
        self.grounded = False
        self.direction = 1   
        self.speed = 0

        self.max_health = health      

        self.health = self.max_health
        self.dead = False
        self.final_phase = False
        self.hit_timer = 0

        self.state = "idle"
        self.spritesheets = {}   
        self.spritesheet = None


    def set_state(self, state):
        if state != self.state:
            self.state = state
            self.spritesheet = self.spritesheets[state]


    def run(self, direction):
        if direction != self.direction:
            self.direction = direction
            for sheet in self.spritesheets.values():
                for i in range(len(sheet.images)):
                    sheet.images[i] = pygame.transform.flip(sheet.images[i], True, False)

        self.velocity_x = self.speed * self.direction

        if self.grounded:
            self.set_state("run")
        else:
            self.set_state("falling")


    def take_damage(self, damage, element=None):
        if self.dead:
            return 
        match element:
            case None: pass
            case 'air':
                if self.element == 'earth': damage *= 2
                elif self.element == 'fire': damage /= 2
            case 'water':
                if self.element == 'fire': 
                    damage *= 2
                elif self.element == 'earth': 
                    damage /= 2
            case 'fire':
                if self.element == 'water': damage *= 2
                elif self.element == 'air': 
                    damage /= 2
            case 'earth':
                if self.element == 'air': damage *= 2
                elif self.element == 'water': damage /= 2


        self.health -= damage
        self.hit_timer = 10
        self.set_state("hit")
        self.velocity_x = 0

    
    def check_attack_range(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = math.sqrt(dx*dx + dy*dy)

        if distance <= self.attack_range:
            self.attack_mode = True
            self.dx = dx
            self.dy = dy
        else:
            self.attack_mode = False



    def behaviour(self, level):
        pass


    def update(self, level):

        if self.final_phase: return

        if self.state == "dead":
            return True

        if self.state == "dying":
            if self.spritesheet.index == len(self.spritesheet.images) - 2:
                self.set_state("dead")
            return False

        if self.hit_timer > 0:
            self.hit_timer -= 1

            if self.hit_timer == 0:
                if self.health <= 0:
                    self.dead = True
                    self.set_state("dying")
                else:
                    self.set_state("idle")

            return False


        self.x += self.velocity_x
        self.rect.x = self.x

        tile = level.check_collision(self.rect)
        if tile:
            if self.velocity_x > 0:
                self.x = tile.left - self.rect.width
            elif self.velocity_x < 0:
                self.x = tile.right
            self.rect.x = self.x
            self.velocity_x = 0

        if not self.grounded:
            self.velocity_y += self.gravity

        self.y += self.velocity_y
        self.rect.y = self.y

        tile = level.check_collision(self.rect)
        if tile:
            if self.velocity_y > 0:  # falling
                self.y = tile.top - self.rect.height
                self.grounded = True
            elif self.velocity_y < 0:  # rising
                self.y = tile.bottom
            self.rect.y = self.y
            self.velocity_y = 0
        else:
            self.grounded = level.is_grounded(self.rect)

        if not self.grounded and self.velocity_y > 0:
            self.set_state("falling")

        if self.grounded:
            self.behaviour(level)

        for sheet in self.spritesheets.values():
            sheet.x = self.x
            sheet.y = self.y

        return False

    def draw(self, screen, camera):
        if self.spritesheet:
            self.spritesheet.x = self.x
            self.spritesheet.y = self.y
            self.spritesheet.draw(screen, camera)
    
    
class Fodder(Enemy):
    def __init__(self, x, y, element):
        super().__init__(x, y, 48, 48, 20)

        self.element = element

        self.attack_range = 500
        self.damage = 10

        self.idle_speed = 1
        self.chase_speed = 5
        self.speed = self.idle_speed

        self.idle_timer = 0
        self.idle_interval = 120

        self.attack_cooldown = 45
        self.attack_timer = self.attack_cooldown

        self.spritesheets = {
            'idle':    Spritesheet(f"Images/Spritesheets/fodder/{self.element}/idle/idle"),
            'run':     Spritesheet(f"Images/Spritesheets/fodder/{self.element}/run/run"),
            'hit':     Spritesheet(f"Images/Spritesheets/fodder/{self.element}/hit/hit"),
            'dying':   Spritesheet(f"Images/Spritesheets/fodder/{self.element}/dying/dying"),
            'attack':  Spritesheet(f"Images/Spritesheets/fodder/{self.element}/attack/attack"),
            'dead':    Spritesheet(f"Images/Spritesheets/fodder/{self.element}/dead/dead"),
            'rising':  Spritesheet(f"Images/Spritesheets/fodder/{self.element}/rising/rising"),
            'falling': Spritesheet(f"Images/Spritesheets/fodder/{self.element}/falling/falling")
        }

        self.set_state("idle")



    def idle_wander(self):
        self.idle_timer += 1
        direction = self.direction

        if self.idle_timer >= self.idle_interval:
            self.idle_timer = 0
            direction *= -1

        self.speed = self.idle_speed
        self.run(direction)

    def chase(self):
        self.speed = self.chase_speed
        self.attack_timer = self.attack_cooldown

        if self.dx > 0:
            self.run(1)
        else:
            self.run(-1)

    def attack(self, level):
        entity = level.check_entity_collisions(self)

        if hasattr(entity, "is_player"):
            if entity.state == "dead":
                self.attack_mode = False
                return False

            self.velocity_x = 0
            self.set_state("attack")

            if self.attack_timer >= self.attack_cooldown:
                entity.take_damage(self.damage, self.element)
                self.attack_timer = 0
            self.attack_timer += 1
            return True

        return False

    def behaviour(self, level):
        if self.attack_mode:
            if not self.attack(level):
                self.chase()
        else:
            self.idle_wander()


class Assassin(Enemy):

    def __init__(self, x, y, element):
        super().__init__(x, y, 64, 128, 50)

        self.element = element

        self.attack_range = 500
        self.damage = 10

        self.run_speed = 30
        self.dash_speed = 50
        self.speed = 0

        self.retreat_distance = 100
        self.retreat_point = None
        self.retreat_direction = 0
        self.locked_position = None  

        self.dashing = False
        self.dash_target = None
        self.attacking = False
        self.attack_delay = 25
        self.attack_delay_timer = 0

        self.attack_cooldown = 60
        self.attack_timer = self.attack_cooldown

        self.spritesheets = {
            'idle':    Spritesheet(f"Images/Spritesheets/assassin/{self.element}/idle/idle"),
            'run':     Spritesheet(f"Images/Spritesheets/assassin/{self.element}/run/run"),
            'hit':     Spritesheet(f"Images/Spritesheets/assassin/{self.element}/hit/hit"),
            'dying':   Spritesheet(f"Images/Spritesheets/assassin/{self.element}/dying/dying"),
            'attack':  Spritesheet(f"Images/Spritesheets/assassin/{self.element}/attack/attack"),
            'dead':    Spritesheet(f"Images/Spritesheets/assassin/{self.element}/dead/dead"),
            'rising':  Spritesheet(f"Images/Spritesheets/assassin/{self.element}/rising/rising"),
            'falling': Spritesheet(f"Images/Spritesheets/assassin/{self.element}/falling/falling")
        }

        self.set_state("idle")

        for sheet in self.spritesheets.values():
            for i in range(len(sheet.images)):
                sheet.images[i] = pygame.transform.scale(sheet.images[i], (128, 128))
    
    def idle(self):
        self.velocity_x = 0
        self.set_state("idle")

    def retreat(self):

        distance = self.retreat_point - self.rect.centerx

        if abs(distance) <= self.run_speed:
            self.x = self.retreat_point
            self.rect.centerx = self.retreat_point
            self.velocity_x = 0
            return True

        self.speed = self.run_speed
        self.run(self.retreat_direction)
        return False


    def attack(self, level):
        if self.dashing:
            if self.dash_target > self.x: direction = 1
            else: direction = -1
            self.speed = self.dash_speed
            self.run(direction)

            entity = level.check_entity_collisions(self)
            if hasattr(entity, "is_player"):
                entity.take_damage(self.damage, self.element)
                self.dashing = False
                self.attacking = True
                self.velocity_x = 0
                self.attack_delay_timer = 0

            if abs(self.x - self.dash_target) <= self.dash_speed:
                self.dashing = False
                self.attacking = True
                self.velocity_x = 0
                self.attack_delay_timer = 0
            return False

        if self.attacking:
            self.velocity_x = 0
            self.set_state("attack")
            self.attack_delay_timer += 1

            if self.attack_delay_timer >= self.attack_delay:
                self.attacking = False
                self.dash_target = None
                self.attack_timer = 0
                return True
            return False
        
        self.dashing = True
        self.dash_target = self.locked_position
        self.set_state("attack")
        
    def reset_attack_state(self):
        self.retreat_point = None
        self.locked_position = None
        self.dash_target = None
        self.dashing = False
        self.attacking = False

    def behaviour(self, level):

        if self.dashing or self.attacking:
            if self.attack(level):
                if self.retreat_point is None:
                    self.retreat_point = self.rect.centerx - self.retreat_direction * self.retreat_distance
            return

        if self.attack_timer < self.attack_cooldown:
            self.attack_timer += 1

        if not self.attack_mode:
            self.retreat_point = None
            self.locked_position = None
            self.idle()
            return

        if self.locked_position is None:
            self.locked_position = self.rect.centerx + self.dx
            self.retreat_direction = -1 if self.dx > 0 else 1
            self.attack(level)
            return

        if self.check_edge_ahead(level):
            self.retreat_direction *= -1
            self.retreat_point = self.rect.centerx - self.retreat_direction * self.retreat_distance

        if not self.retreat():
            return

        if self.attack_timer < self.attack_cooldown:
            self.idle()
            return

        self.retreat_point = None
        self.attack(level)
    
    def check_edge_ahead(self, level):
        test_rect = pygame.Rect(self.rect.centerx + (self.retreat_direction * 32) - self.rect.width // 2, self.rect.bottom, self.rect.width, 5)
        return not level.is_grounded(test_rect)
    

    def update(self, level, player=None):
        if player is not None:
            self.check_attack_range(player)

        if self.state == "dead":
            return True

        if self.state == "dying":
            if self.spritesheet.index == len(self.spritesheet.images) - 2:
                self.set_state("dead")
            return False

        if self.hit_timer > 0:
            self.hit_timer -= 1

            if self.hit_timer == 0:
                if self.health <= 0:
                    self.dead = True
                    self.set_state("dying")
                else:
                    self.set_state("idle")

            return False

        if not self.attack_mode:
            self.reset_attack_state()
            self.idle()
            return


        self.x += self.velocity_x
        self.rect.x = self.x

        if not self.grounded:
            self.velocity_y += self.gravity

        self.y += self.velocity_y
        self.rect.y = self.y

        tile = level.check_collision(self.rect)
        if tile:
            if self.velocity_y > 0:  # falling
                self.y = tile.top - self.rect.height
                self.grounded = True
            elif self.velocity_y < 0:  # rising
                self.y = tile.bottom
            self.rect.y = self.y
            self.velocity_y = 0
        else:
            self.grounded = level.is_grounded(self.rect)

        if not self.grounded and self.velocity_y > 0:
            self.set_state("falling")

        if self.grounded:
            self.behaviour(level)


        for sheet in self.spritesheets.values():
            sheet.x = self.x
            sheet.y = self.y

        return False


class Mage(Enemy):
    def __init__(self, x, y, element):
        super().__init__(x, y, 64, 70, 20)

        self.offset_x = -67
        self.offset_y = -145
        self.element = element
        self.attack_range = 1000
        self.damage = 10
        self.attack_delay = 25
        self.attack_delay_timer = 0
        self.attacking = False
        self.attack_cooldown = 30
        self.attack_timer = self.attack_cooldown
        self.flipped = False
        self.spells = {'fire':{'name': 'ignatious', 'element': 'fire', 'speed': 20, 'damage': 20, 'lifetime': 100, 'size': (64,64), 'caster': self}, 
                       'water': {'name': 'hydroblast', 'element': 'water', 'speed': 20, 'damage': 15, 'lifetime': 100, 'size': (64,64), 'caster': self},
                       'air': {'name': 'aeroslash', 'element': 'air', 'speed': 20, 'damage': 5, 'lifetime': 100, 'size': (64,64), 'caster': self},
                       'earth': {'name': 'terrathrow', 'element': 'earth', 'speed': 20, 'damage': 25, 'lifetime': 100, 'size': (64,64), 'caster': self}}

        self.run_speed = 15
        self.speed = 0
        self.retreat_distance = 500
        self.retreat_point = None
        self.retreat_direction = 0
        self.locked_position = None  

        self.spritesheets = {
            'idle':    Spritesheet(f"Images/Spritesheets/mage/idle/idle"),
            'run':     Spritesheet(f"Images/Spritesheets/mage/run/run"),
            'hit':     Spritesheet(f"Images/Spritesheets/mage/hit/hit"),
            'dying':   Spritesheet(f"Images/Spritesheets/mage/dying/dying"),
            'attack':  Spritesheet(f"Images/Spritesheets/mage/attack/attack"),
            'dead':    Spritesheet(f"Images/Spritesheets/mage/dead/dead"),
            'rising':  Spritesheet(f"Images/Spritesheets/mage/idle/idle"),
            'falling': Spritesheet(f"Images/Spritesheets/mage/idle/idle")
        }

        self.set_state("idle")
        for sheet in self.spritesheets.values():
            for i in range(len(sheet.images)):
                sheet.images[i] = pygame.transform.scale(sheet.images[i], (192, 240))


    def idle(self):
        self.velocity_x = 0
        self.set_state("idle")


    def retreat(self):
        distance = self.retreat_point - self.rect.centerx
        if abs(distance) <= self.run_speed:
            self.x = self.retreat_point
            self.rect.centerx = self.retreat_point
            self.velocity_x = 0
            return True
        self.speed = self.run_speed
        self.run(self.retreat_direction)
        return False


    def attack(self, level):
        if self.attacking:
            self.velocity_x = 0
            if not self.flipped:
                self.run(self.direction * -1)
                self.flipped = True
            self.set_state("attack")
            self.attack_delay_timer += 1

            if self.attack_delay_timer >= self.attack_delay:
                self.spell = self.spells[self.element]
                self.attacking = False
                self.attack_timer = 0
                self.flipped = False
                return True
            return False

        self.attacking = True
        self.attack_delay_timer = 0
        self.set_state("attack")
        return False


    def reset_attack_state(self):
        self.retreat_point = None
        self.locked_position = None
        self.attacking = False
        self.attack_delay_timer = 0


    def behaviour(self, level):
        if self.attacking:
            if self.attack(level):
                if self.retreat_point is None:
                    self.retreat_point = self.rect.centerx - self.retreat_direction * self.retreat_distance
            return

        if self.attack_timer < self.attack_cooldown:
            self.attack_timer += 1

        if not self.attack_mode:
            self.reset_attack_state()
            self.idle()
            return

        if self.locked_position is None:
            self.locked_position = self.rect.centerx + self.dx
            self.retreat_direction = -1 if self.dx > 0 else 1
            self.attack(level)
            return

        if self.check_edge_ahead(level):
            self.retreat_direction *= -1
            self.retreat_point = self.rect.centerx - self.retreat_direction * self.retreat_distance

        if not self.retreat():
            return

        if self.attack_timer < self.attack_cooldown:
            self.idle()
            return

        self.retreat_point = None
        self.attack(level)


    def check_edge_ahead(self, level):
        test_rect = pygame.Rect(
            self.rect.centerx + (self.retreat_direction * 32) - self.rect.width // 2,
            self.rect.bottom,
            self.rect.width,
            5
        )
        return not level.is_grounded(test_rect)


    def draw(self, screen, camera):
        if self.spritesheet:
            self.spritesheet.x = self.x + self.offset_x
            self.spritesheet.y = self.y + self.offset_y
            self.spritesheet.draw(screen, camera)


    def update(self, level, player=None):
        if player is not None:
            self.check_attack_range(player)

        if self.state in ("dead", "dying"):
            if self.state == "dying" and self.spritesheet.index == len(self.spritesheet.images) - 2:
                self.set_state("dead")
            return False

        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer == 0:
                if self.health <= 0:
                    self.dead = True
                    self.set_state("dying")
                else:
                    self.set_state("idle")
            return False

        if not self.attack_mode:
            self.reset_attack_state()
            self.idle()
            return

        self.x += self.velocity_x
        self.rect.x = self.x

        if not self.grounded:
            self.velocity_y += self.gravity

        self.y += self.velocity_y
        self.rect.y = self.y

        tile = level.check_collision(self.rect)
        if tile:
            if self.velocity_y > 0:  # falling
                self.y = tile.top - self.rect.height
                self.grounded = True
            elif self.velocity_y < 0:  # rising
                self.y = tile.bottom
            self.rect.y = self.y
            self.velocity_y = 0
        else:
            self.grounded = level.is_grounded(self.rect)

        if not self.grounded and self.velocity_y > 0:
            self.set_state("falling")

        if self.grounded:
            self.behaviour(level)

        for sheet in self.spritesheets.values():
            sheet.x = self.x
            sheet.y = self.y

        return False


class Tank(Enemy):

    def __init__(self, x, y):
        super().__init__(x, y, 96, 96, 150)

        self.element = None

        self.offset_x = -67
        self.offset_y = -92

        self.attack_range = 1000        
        self.strike_range = 80
        self.approach_distance = 60
        self.damage = 50

        self.walk_speed = 3
        self.speed = 0

        self.attack_cooldown = 25
        self.attack_timer = self.attack_cooldown
        self.attacking = False

        self.spritesheets = {
            'idle':    Spritesheet(f"Images/Spritesheets/tank/idle/idle"),
            'run':     Spritesheet(f"Images/Spritesheets/tank/run/run"),
            'hit':     Spritesheet(f"Images/Spritesheets/tank/hit/hit"),
            'dying':   Spritesheet(f"Images/Spritesheets/tank/dying/dying"),
            'attack':  Spritesheet(f"Images/Spritesheets/tank/attack/attack"),
            'dead':    Spritesheet(f"Images/Spritesheets/tank/dead/dead"),
            'rising':  Spritesheet(f"Images/Spritesheets/tank/idle/idle"),
            'falling': Spritesheet(f"Images/Spritesheets/tank/idle/idle")
        }

        self.set_state("idle")

        for sheet in self.spritesheets.values():
            for i in range(len(sheet.images)):
                sheet.images[i] = pygame.transform.scale(sheet.images[i], (256, 256))

    def idle(self):
        self.velocity_x = 0
        self.set_state("idle")

    def move_towards_player(self):
        if self.dx > 0:
            self.speed = self.walk_speed
            self.run(1)
        else:
            self.speed = self.walk_speed
            self.run(-1)

    def attack(self, level):
        self.velocity_x = 0
        self.attacking = True
        self.set_state("attack")
        
        entity = level.check_entity_collisions(self)
        if entity.state == 'dead': self.idle()  
        else: entity.take_damage(self.damage)

    def behaviour(self, level):
        if not self.attack_mode:
            self.idle()
            self.attacking = False
            return

        if self.attacking:
            if self.spritesheet.index == len(self.spritesheet.images) - 1:
                self.attacking = False
                self.attack_timer = 0
                self.idle()
            return
        
        strike_distance = math.sqrt(self.dx*self.dx + self.dy*self.dy)
        if strike_distance <= self.approach_distance:
            if self.attack_timer >= self.attack_cooldown:
                self.attack(level)
            else:
                self.idle()
                self.attack_timer += 1
        else:
            self.move_towards_player()
            self.attack_timer += 1

    def draw(self, screen, camera):
        if self.spritesheet:
            self.spritesheet.x = self.x + self.offset_x
            self.spritesheet.y = self.y + self.offset_y
            self.spritesheet.draw(screen, camera)
        

class Boss(Enemy):

    def __init__(self, x, y, element):
        super().__init__(x, y, 150, 100, 1)

        self.offset_x = -67
        self.offset_y = -115

        self.element = element


        self.attack_range = 10000
        self.approach_distance = 100   
        self.melee_range = 500


        self.damage = 33

        self.walk_speed = 6
        self.run_speed = 30
        self.dash_speed = 50
        self.speed = 0

        self.attack_cooldown = 30
        self.attack_timer = self.attack_cooldown

        self.dashing = False
        self.dash_target = None
        self.attacking = False
        self.attack_delay = 30
        self.attack_delay_timer = 0

        self.behaviour_timer = 0
        self.behaviour_pause = 0

        self.phrases = {
            'water': "HE LEARNED MORE THAN ANY ONE SOUL WAS MEANT TO HOLD",
            'earth': "WHAT HE GATHERED BEGAN TO BEND THE WORLD AROUND HIM",
            'air':   "SOON NOTHING MOVED UNLESS IT MOVED BY HIS WILL",
            'fire':  "ONLY HIS FALL CAN STEADY WHAT HE HAS THROWN INTO CHAOS",
        }



        self.final_phase = False
        self.final_phrase = self.phrases[self.element]
        self.player_input = ""
        self.final_phrase_complete = False


        self.spells = {
            'fire': {'name': 'ignatious', 'element': 'fire', 'speed': 20, 'damage': 20, 'lifetime': 100, 'size': (64,64), 'caster': self},
            'water': {'name': 'hydroblast', 'element': 'water', 'speed': 20, 'damage': 15, 'lifetime': 100, 'size': (64,64), 'caster': self},
            'air': {'name': 'aeroslash', 'element': 'air', 'speed': 20, 'damage': 10, 'lifetime': 100, 'size': (64,64), 'caster': self},
            'earth': {'name': 'terrathrow', 'element': 'earth', 'speed': 20, 'damage': 25, 'lifetime': 100, 'size': (64,64), 'caster': self}
        }

        self.attack_type = None

        self.spritesheets = {
            'idle': Spritesheet(f"Images/Spritesheets/boss/{element}/idle/idle"),
            'run': Spritesheet(f"Images/Spritesheets/boss/{element}/run/run"),
            'hit': Spritesheet(f"Images/Spritesheets/boss/{element}/hit/hit"),
            'dying': Spritesheet(f"Images/Spritesheets/boss/{element}/dying/dying"),
            'attack1': Spritesheet(f"Images/Spritesheets/boss/{element}/attack1/attack1"),
            'attack2': Spritesheet(f"Images/Spritesheets/boss/{element}/attack2/attack2"),
            'dead': Spritesheet(f"Images/Spritesheets/boss/{element}/dead/dead"),
            'rising': Spritesheet(f"Images/Spritesheets/boss/{element}/idle/idle"),
            'falling': Spritesheet(f"Images/Spritesheets/boss/{element}/idle/idle")
        }

        self.set_state("idle")

        for sheet in self.spritesheets.values():
            for i in range(len(sheet.images)):
                sheet.images[i] = pygame.transform.scale(sheet.images[i], (256, 256))
                sheet.images[i] = pygame.transform.flip(sheet.images[i], True, False)


    def idle(self):
        self.velocity_x = 0
        self.set_state("idle")

    def move_towards_player(self):
        if self.dx > 0:
            self.speed = self.walk_speed
            self.run(1)
        else:
            self.speed = self.walk_speed
            self.run(-1)


    def tank_attack(self, level):
        self.velocity_x = 0
        self.attacking = True
        self.set_state("attack1")

        entity = level.check_entity_collisions(self)
        if hasattr(entity, "is_player"):
            if entity.state == 'dead':
                self.idle()
            else:
                entity.take_damage(self.damage, self.element)


    def assassin_attack(self, level):

        if self.dashing:
            if self.dash_target > self.x: direction = 1
            else: direction = -1

            self.speed = self.dash_speed
            self.run(direction)

            entity = level.check_entity_collisions(self)
            if hasattr(entity, "is_player"):
                entity.take_damage(self.damage, self.element)
                self.dashing = False
                self.attacking = True
                self.velocity_x = 0
                self.attack_delay_timer = 0

            if abs(self.x - self.dash_target) <= self.dash_speed:
                self.dashing = False
                self.attacking = True
                self.velocity_x = 0
                self.attack_delay_timer = 0
            return False

        if self.attacking:
            self.velocity_x = 0
            self.set_state("attack1")
            self.attack_delay_timer += 1

            if self.attack_delay_timer >= self.attack_delay:
                self.attacking = False
                self.dash_target = None
                self.attack_timer = 0
                return True
            return False

        self.dashing = True
        self.dash_target = self.rect.centerx + self.dx
        self.set_state("attack1")


    def mage_attack(self, level):

        if self.attacking:
            self.velocity_x = 0
            self.set_state("attack2")
            self.attack_delay_timer += 1

            if self.attack_delay_timer >= self.attack_delay:
                self.spell = self.spells[self.element]
                self.attacking = False
                self.attack_timer = 0
                return True
            return False

        self.attacking = True
        self.attack_delay_timer = 0
        self.set_state("attack2")
        return False


    def take_damage(self, damage, element=None):
        if self.final_phase:
            return  

        match element:
            case None: pass
            case 'air':
                if self.element == 'earth': damage *= 2
                elif self.element == 'fire': damage /= 2
            case 'water':
                if self.element == 'fire': 
                    damage *= 2
                elif self.element == 'earth': 
                    damage /= 2
            case 'fire':
                if self.element == 'water': damage *= 2
                elif self.element == 'air': 
                    damage /= 2
            case 'earth':
                if self.element == 'air': damage *= 2
                elif self.element == 'water': damage /= 2

        self.health -= damage
        if self.health <= 0:
            self.final_phase = True
            self.health = 0
            self.velocity_x = 0
            self.velocity_y = 0
            self.set_state("idle")
            self.player_input = ""
            return

        self.hit_timer = 10
        self.set_state("hit")
        self.velocity_x = 0



    def behaviour(self, level):

        if self.final_phase: 
            self.set_state('idle')
            return

        self.behaviour_timer += 1

        # Every 200 frames → pause for 10 frames
        if self.behaviour_timer >= 500:
            self.behaviour_pause = 100
            self.behaviour_timer = 0

        # If currently pausing → idle and skip all behaviour
        if self.behaviour_pause > 0:
            self.behaviour_pause -= 1
            self.idle()
            return
        
        player = None
        for entity in level.entities:
            if hasattr(entity, "is_player"):
                player = entity
                break

        if player and player.state == "dead":
            self.idle()
            self.velocity_x = 0
            self.attacking = False
            self.dashing = False
            self.attack_type = None
            return

        if not self.attack_mode:
            self.idle()
            return


        if self.attack_type == "dash":
            if self.assassin_attack(level):
                self.attack_type = None
            return

        if self.attack_type == "ranged":
            if self.mage_attack(level):
                self.attack_type = None
            return


        if self.attacking:
            if self.spritesheet.index == len(self.spritesheet.images) - 1:
                self.attacking = False
                self.attack_timer = 0
                self.idle()
            return

        if self.attack_timer < self.attack_cooldown:
            self.attack_timer += 1

        distance = math.sqrt(self.dx*self.dx + self.dy*self.dy)


        if distance <= self.approach_distance:
            if self.attack_timer >= self.attack_cooldown:
                self.tank_attack(level)
            else:
                self.idle()
                self.attack_timer += 1
            return


        if distance <= self.melee_range:
            if self.attack_timer >= self.attack_cooldown:
                self.attack_type = "dash"
            else:
                self.move_towards_player()
                self.attack_timer += 1
            return


        if self.attack_timer >= self.attack_cooldown:
            self.attack_type = "ranged"
        else:
            self.move_towards_player()
            self.attack_timer += 1


    def draw_final_phrase(self, screen, camera):
        if not self.final_phase:
            return

        fill_color = '#E8D4C4'
        border_color = '#C58F3D'
        correct_color = '#783CA0'
        wrong_color = (255, 0, 0)
        remaining_color = '#C58F3D'
        font = pygame.font.Font('Images/PixelPurl.ttf', 48)
        rendered_letters = []
        index = 0
        for letter in self.final_phrase:
            if index < len(self.player_input):
                if self.player_input[index] == letter:
                    color = correct_color
                else: color = wrong_color
            else: color = remaining_color

            surf = font.render(letter, True, color)
            rendered_letters.append(surf)
            index += 1

        padding = 20
        total_width = 0
        for surf in rendered_letters: total_width += surf.get_width()
        total_width += padding * 2
        height = rendered_letters[0].get_height() + padding * 2

        x = 400
        y = 60

        rect = pygame.Rect(x, y, total_width, height)
        pygame.draw.rect(screen, fill_color, rect, border_radius=6)
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=6)

        draw_x = x + padding
        for surf in rendered_letters:
            screen.blit(surf, (draw_x, y + padding))
            draw_x += surf.get_width()

        
    def draw_health_bar(self, screen, x=1000, y=20, width=400, height=20):
        pygame.draw.rect(screen, (40, 40, 40), (x, y, width, height), border_radius=4)
        ratio = self.health/ self.max_health
        ratio = max(0, min(ratio, 1)) # Clamp between 0 and 1
        fill_width = int(width * ratio)
        pygame.draw.rect(screen, (50, 50, 200), (x, y, fill_width, height), border_radius=4)
        pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 2, border_radius=4)


    def draw(self, screen, camera):
        if self.spritesheet:
            self.spritesheet.x = self.x + self.offset_x
            self.spritesheet.y = self.y + self.offset_y
            self.draw_final_phrase(screen, camera)
            self.draw_health_bar(screen)
            self.spritesheet.draw(screen, camera)


class FinalBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, 'water')
        self.offset_x = 0
        self.offset_y = -80
        self.rect.width = 369
        self.attack_range = 10000
        self.approach_distance = 100   
        self.melee_range = 500


        self.damage = 33

        self.walk_speed = 6
        self.speed = 0

        self.attack_cooldown = 30
        self.attack_timer = self.attack_cooldown

        self.teleporting = False
        self.tele_target = None
        self.attacking = False
        self.attack_delay = 30
        self.attack_delay_timer = 0

        self.behaviour_timer = 0
        self.behaviour_pause = 0
        self.phrases = {0: 'THIS IS THE FIRST LINE OF MANY'}
        self.line = 0

        self.final_phase = False
        self.final_phrase = self.phrases[self.line]
        self.player_input = ""
        self.final_phrase_complete = False


        self.spells = {
            'fire': {'name': 'ignatious', 'element': 'fire', 'speed': 20, 'damage': 20, 'lifetime': 100, 'size': (64,64), 'caster': self},
            'water': {'name': 'hydroblast', 'element': 'water', 'speed': 20, 'damage': 15, 'lifetime': 100, 'size': (64,64), 'caster': self},
            'air': {'name': 'aeroslash', 'element': 'air', 'speed': 20, 'damage': 10, 'lifetime': 100, 'size': (64,64), 'caster': self},
            'earth': {'name': 'terrathrow', 'element': 'earth', 'speed': 20, 'damage': 25, 'lifetime': 100, 'size': (64,64), 'caster': self}
        }

        self.attack_type = None

        self.spritesheets = {
            'idle': Spritesheet(f"Images/Spritesheets/boss/final/idle/idle"),
            'run': Spritesheet(f"Images/Spritesheets/boss/final/run/run"),
            'hit': Spritesheet(f"Images/Spritesheets/boss/final/hit/hit"),
            'dying': Spritesheet(f"Images/Spritesheets/boss/final/dying/dying"),
            'attack1': Spritesheet(f"Images/Spritesheets/boss/final/attack1/attack1"),
            'attack2': Spritesheet(f"Images/Spritesheets/boss/final/attack2/attack2"),
            'dead': Spritesheet(f"Images/Spritesheets/boss/final/dead/dead"),
            'rising': Spritesheet(f"Images/Spritesheets/boss/final/idle/idle"),
            'falling': Spritesheet(f"Images/Spritesheets/boss/final/idle/idle"),
            'tele1': Spritesheet(f"Images/Spritesheets/boss/final/tele1/tele1"),
            'tele2': Spritesheet(f"Images/Spritesheets/boss/final/tele2/tele2")
        }

        self.set_state("idle")

        for sheet in self.spritesheets.values():
            for i in range(len(sheet.images)):
                sheet.images[i] = pygame.transform.scale(sheet.images[i], (369, 186))


    def mage_attack(self, level):

        if self.attacking:
            self.velocity_x = 0
            self.set_state("attack2")
            self.attack_delay_timer += 1

            if self.attack_delay_timer >= self.attack_delay:
                self.spell = random.choice(list(self.spells.values()))
                self.attacking = False
                self.attack_timer = 0
                return True
            return False

        self.attacking = True
        self.attack_delay_timer = 0
        self.set_state("attack2")
        return False
    
    def teleport(self, level):
        if self.state != 'tele1' or self.state != 'tele2':
            self.set_state('tele1')
            return
        if self.state == 'tele1' and self.spritesheet.index == len(self.spritesheet.images) - 1:
            self.set_state('tele2')
            return
        if self.state == 'tele2' and self.spritesheet.index == len(self.spritesheet.images) - 1:
            self.teleporting = False
        while level.check_collision(pygame.rect(self.x + self.rect.width + self.tele_target, self.y, 50, 50)):
            self.tele_target -= 64
        self.x += self.tele_target + self.rect.width


    def assassin_attack(self, level):

        if self.teleporting:
            if self.tele_target > self.x: self.tele_target *= 1
            else: self.teletarget *= -1

            self.teleport(level)

            entity = level.check_entity_collisions(self)
            if hasattr(entity, "is_player"):
                entity.take_damage(self.damage, self.element)
                self.teleporting = False
                self.attacking = True
                self.velocity_x = 0
                self.attack_delay_timer = 0

            if abs(self.x - self.dash_target) <= self.dash_speed:
                self.teleporting = False
                self.attacking = True
                self.velocity_x = 0
                self.attack_delay_timer = 0
            return False

        if self.attacking:
            self.velocity_x = 0
            self.set_state("attack1")
            self.attack_delay_timer += 1

            if self.attack_delay_timer >= self.attack_delay:
                self.attacking = False
                self.dash_target = None
                self.attack_timer = 0
                return True
            return False

        self.teleporting = True
        self.tele_target = self.rect.centerx + self.dx
        self.set_state("attack1")


    
    def behaviour(self, level):

        if self.final_phase: 
            self.set_state('idle')
            return

        self.behaviour_timer += 1

        if self.behaviour_timer >= 500:
            self.behaviour_pause = 100
            self.behaviour_timer = 0

        if self.behaviour_pause > 0:
            self.behaviour_pause -= 1
            self.idle()
            return
        
        player = None
        for entity in level.entities:
            if hasattr(entity, "is_player"):
                player = entity
                break

        if player and player.state == "dead":
            self.idle()
            self.velocity_x = 0
            self.attacking = False
            self.teleporting = False
            self.attack_type = None
            return

        if not self.attack_mode:
            self.idle()
            return


        if self.attack_type == "teleport":
            if self.assassin_attack(level):
                self.attack_type = None
            return

        if self.attack_type == "ranged":
            if self.mage_attack(level):
                self.attack_type = None
            return


        if self.attacking:
            if self.spritesheet.index == len(self.spritesheet.images) - 1:
                self.attacking = False
                self.attack_timer = 0
                self.idle()
            return

        if self.attack_timer < self.attack_cooldown:
            self.attack_timer += 1

        distance = math.sqrt(self.dx*self.dx + self.dy*self.dy)


        if distance <= self.approach_distance:
            if self.attack_timer >= self.attack_cooldown:
                self.tank_attack(level)
            else:
                self.idle()
                self.attack_timer += 1
            return


        if distance <= self.melee_range:
            if self.attack_timer >= self.attack_cooldown:
                self.attack_type = "teleport"
            else:
                self.move_towards_player()
                self.attack_timer += 1
            return


        if self.attack_timer >= self.attack_cooldown:
            self.attack_type = "ranged"
        else:
            self.move_towards_player()
            self.attack_timer += 1


