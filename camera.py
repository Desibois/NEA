class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.offset_x = 0
        self.offset_y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height

        self.deadzone_top = 150
        self.deadzone_bottom = 250
        self.deadzone_left = 400
        self.deadzone_right = 700

    def update(self, player):
        player_screen_x = player.x - self.offset_x
        player_screen_y = player.y - self.offset_y

        if player_screen_x < self.deadzone_left:
            self.offset_x -= (self.deadzone_left - player_screen_x)
        elif player_screen_x > self.deadzone_right:
            self.offset_x += (player_screen_x - self.deadzone_right)

        if player_screen_y < self.deadzone_top:
            self.offset_y -= (self.deadzone_top - player_screen_y)
        elif player_screen_y > self.deadzone_bottom:
            self.offset_y += (player_screen_y - self.deadzone_bottom)

        self.offset_x = max(0, min(self.offset_x, self.map_width - self.screen_width))
        self.offset_y = min(self.offset_y, self.map_height - self.screen_height)-275