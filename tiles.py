import pygame
import json



class Tilemap:

    def __init__(self, file_path, spritesheet, index=0):
        self.tile_size = 64 # size of each tile
        self.start_x, self.start_y = 0,0 # Position to draw map
        self.spritesheet = spritesheet # Spritesheet for tileset 
        self.file_path = file_path # File path to JSON containing the tile map
        self.index = index # For creating different tile map objects for different layers of the level
        self.tiles = [] # List of tile objects 
        self.read_json()
        self.load_tiles()
        self.draw()
            
    def read_json(self):
        with open(self.file_path, 'r') as f: # Open tile map json
            meta_data = json.load(f)['layers'][self.index] # Tile map data for specific layer
            data, width, height = meta_data['data'], meta_data['width'], meta_data['height'] 
        self.map = []
        for row in range(height): # Loop through rows and append row to map
            start = row * width
            end = (row + 1) * width
            self.map.append(data[start:end])
    

    def load_tiles(self):
        self.tiles = [] # Array to store tiles
        for y in range(len(self.map)): # Loop through map
            row = self.map[y]
            for x in range(len(row)):
                tile_id = row[x] # tile id of tile in tile set
                image = self.spritesheet.get_sprite_id(tile_id)
                if image is not None:
                    tile = Tile(image, x * self.tile_size, y * self.tile_size)
                    self.tiles.append(tile)
        self.map_width = len(self.map[0]) * self.tile_size # Dimensions of map when displayed
        self.map_height = len(self.map) * self.tile_size
    

    def draw(self):
        self.map_surface = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        self.map_surface.fill((0, 0, 0, 0))
        for tile in self.tiles: (tile.draw(self.map_surface))

      

class Tile(pygame.sprite.Sprite): # Inherits sprite for easier handling of collision detection that will come
   
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, canvas):
        canvas.blit(self.image, (self.rect.x, self.rect.y))