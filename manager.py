import pygame
from menus import *

class GameManager:
    def __init__(self, screen, initial_state, bg_image):
        self.bg_image = bg_image
        self.running = True # Flag
        self.screen = screen
        self.state = initial_state
        self._menus = {} # stores generated menus for quicker access
        self.current_menu = None
        self.music_enabled = True
        pygame.mixer.init()
        self.mixer = pygame.mixer # SFX
        self.music_volume = 0.7
        self._brightness = 1.0
        self._factor = 1.0
        self.play_music()

    def handle_action(self, action: str, value=None):
        try:
            if value is not None: # Slider
                getattr(self, action)(value) # Turns action into method and executes
            else: # Button
                getattr(self, action)()
        except AttributeError: pass # If method for attribute does not exist
    
    def main_menu(self): # Main menu
        self.state = 'main'
        if 'main' in self._menus: # No need to render if it already exists
            self.set_menu('main')
            return self.current_menu
        Bcontinue_game = Button(self.screen, 'Continue game', "Images/Main_menu/Buttons/CONTINUEGAME.png", (125, 193), "continue_game", self)
        Bnew_game = Button(self.screen, 'New Game', "Images/Main_menu/Buttons/NEWGAME.png", (120, 288), "new_game", self)
        Bprevious_game = Button(self.screen, 'Previous Game', "Images/Main_menu/Buttons/PREVIOUSGAME.png", (420, 193), "previous_game", self)
        Bsettings = Button(self.screen, 'Settings', "Images/Main_menu/Buttons/SETTINGS.png", (430, 288), "settings", self)
        menu = Menu(self.screen, "Main Menu", "Images/Main_menu/Background.png", True, [Bcontinue_game, Bnew_game, Bprevious_game, Bsettings])
        self.register_menu('main', menu)
        self.set_menu('main')
        return menu
    
    def settings(self):
        self.state = 'settings'
        if 'settings' in self._menus:
            self.set_menu('settings')
            return self.current_menu
        Bback = Button(self.screen, 'Back', "Images/Settings/Buttons/BACK.png",  (135, 68), "main_menu", self)
        Bmusic = Button(self.screen, 'Music', "Images/Settings/Buttons/MUSIC.png",  (290, 153), "toggle_music", self)
        Svolume= Slider(self.screen, 'Volume', (135, 183), 'change_volume', self, self.music_volume)
        Stext_size = Slider(self.screen, 'Text_Size', (135, 273), 'adjust_size', self, 0.5)
        Sbrightness = Slider(self.screen, 'Brightness', (135, 363), 'adjust_brightness', self, 0.5)
        menu = Menu(self.screen, "Settings", "Images/Settings/Background.png", True, [Bback, Bmusic, Svolume, Sbrightness, Stext_size])
        self.register_menu('settings', menu)
        self.set_menu('settings')
        return menu

    def toggle_music(self):
        if self.music_enabled: # Music off
            self.mixer.music.pause()
            self.music_enabled = False
        else: # Music on
            self.mixer.music.unpause()
            self.music_enabled = True

    def play_music(self):
        self.mixer.music.load("SFX/background.wav")
        self.mixer.music.set_volume(self.music_volume)
        self.mixer.music.play(-1) # Loops music 
        self.music_enabled = True
    
    def change_volume(self, slider_value):
        self.music_volume = max(0.0, min(1.0, slider_value))
        self.mixer.music.set_volume(self.music_volume)
    
    def adjust_brightness(self, _brightness):
        self._brightness = _brightness
        gamma = 2 * _brightness  
        pygame.display.set_gamma(gamma) # Gamma determines _brightness
    
    def adjust_size(self, factor):
        self._factor =  factor + 0.5

    def render_menu(self):   
        if not self.current_menu:
            return
        pygame.display.set_caption(self.current_menu.title) # Change title of display
        bg_image = self.current_menu.bg_image.convert_alpha() # Opaque area of menu background
        bg_width = max(1, int(bg_image.get_width() * self._factor)) 
        bg_height = max(1, int(bg_image.get_height() * self._factor))
        bg_scaled = pygame.transform.smoothscale(bg_image, (bg_width, bg_height)) # Scale background to new width, height
        bg_x = (self.screen.get_width() - bg_width) // 2 
        bg_y = (self.screen.get_height() - bg_height) // 2
        self.screen.blit(self.bg_image, (0, 0)) # Display background wallpaper
        self.screen.blit(bg_scaled, (bg_x, bg_y)) # Display centred menu background

        for button in self.current_menu.buttons: # Loop and scale buttons.sliders
            src_w, src_h = button._source_size # Orignial size
            src_x, src_y = button._source_position # original position
            new_size = int(src_w * self._factor), int(src_h * self._factor)
            new_pos = (src_x * self._factor) + bg_x , (src_y * self._factor) + bg_y
            button.image = pygame.transform.smoothscale(pygame.image.load(button.image_path).convert_alpha(), new_size) # Scale image
            button.rect = button.image.get_rect(topleft=new_pos) # New effective area
            button.position = button.rect.topleft # New position
            if isinstance(button, Slider): # Scale slider
                dw, dh = button._dial_source_size
                button.dial_image = pygame.transform.smoothscale(button._dial_source_image, (max(1,int(dw*self._factor)), max(1,int(dh*self._factor))))
                button.dial_rect = button.dial_image.get_rect()
                button.min_x = button.rect.x
                button.max_x = button.rect.x + button.rect.width - button.dial_rect.width 
                button.centreline() # Recreate centre line
                button.update_dial() # Repositon dial
            button.draw()
        
    def register_menu(self, name, menu): # Add menu to dictionary
        self._menus[name] = menu

    def set_menu(self, name): # Set menu in dictionary to current menu
        for menu_name, menu in self._menus.items():
            if menu_name == name: menu.opened = True
            else: menu.opened = False
        self.current_menu = self._menus[name]

    def continue_game(self):
        self.state = 'continue'
        
    def new_game(self):
        self.state = 'new'  

    def previous_game(self):
        self.state = 'previous'
        if 'previous' in self._menus:
            self.set_menu('previous')
            return self.current_menu
        Bback = Button(self.screen, 'Back', "Images/Previous/Buttons/BACK.png",  (135, 85), "main_menu", self)
        Bgame1 =  Button(self.screen, 'Game1', "Images/Previous/Buttons/GAME1.png",  (120, 165), "load_save", self)
        Bgame2 =  Button(self.screen, 'Game2', "Images/Previous/Buttons/GAME2.png",  (115, 225), "load_save", self)
        Bgame3 =  Button(self.screen, 'Game3', "Images/Previous/Buttons/GAME3.png",  (116, 285), "load_save", self)
        Bgame4 =  Button(self.screen, 'Game4', "Images/Previous/Buttons/GAME4.png",  (113, 345), "load_save", self)
        Bgame5 =  Button(self.screen, 'Game5', "Images/Previous/Buttons/GAME5.png",  (500, 50), "load_save", self)
        Bgame6 =  Button(self.screen, 'Game6', "Images/Previous/Buttons/GAME6.png",  (505, 110), "load_save", self)
        Bgame7 =  Button(self.screen, 'Game7', "Images/Previous/Buttons/GAME7.png",  (500, 160), "load_save", self)
        Bgame8 =  Button(self.screen, 'Game8', "Images/Previous/Buttons/GAME8.png",  (500, 225), "load_save", self)
        Bgame9 =  Button(self.screen, 'Game9', "Images/Previous/Buttons/GAME9.png",  (500, 300), "load_save", self)
        buttons = [Bback, Bgame1, Bgame2, Bgame3, Bgame4, Bgame5, Bgame6, Bgame7, Bgame8, Bgame9]
        menu = Menu(self.screen, "Previous", "Images/Previous/Background.png", True, buttons)
        self.register_menu("previous", menu)
        self.set_menu("previous")
        return menu

    def load_save(self):
        pass
    
    def pause(self):
        self.state = "pause"
        if 'pause' in self._menus:
            self.set_menu('pause')
            return self.current_menu
        Bback = Button(self.screen, 'Back', "Images/Pause/Buttons/BACK.png",  (100, 70), "unpause", self) # Back button performs unpause method
        Bmain = Button(self.screen, 'Main', "Images/Pause/Buttons/MAIN.png",  (80, 165), "main_menu", self)
        Bsettings = Button(self.screen, 'Settings', "Images/Pause/Buttons/SETTINGS.png",  (75, 275), "settings", self)
        menu = Menu(self.screen, "Paused", "Images/Pause/Background.png", True, [Bback, Bmain, Bsettings])
        self.register_menu('pause', menu)
        self.set_menu('pause')
        return menu

    def dead(self):
        self.state = "dead"
        if 'dead' in self._menus:
            self.set_menu('dead')
            return self.current_menu
        Bmain = Button(self.screen, 'Main', "Images/Dead/Buttons/MAIN.png",  (80, 165), "main_menu", self)
        Bquit = Button(self.screen, 'Quit', "Images/Dead/Buttons/QUIT.png",  (75, 275), "exit", self)
        Brespawn = Button(self.screen, 'Respawn', "Images/Dead/Buttons/RESPAWN.png",  (75, 385), "respawn", self)
        menu = Menu(self.screen, "Dead", "Images/Dead/Background.png", True, [Bmain, Bquit, Brespawn])
        self.register_menu('dead', menu)
        self.set_menu('dead')
        return menu
    
    def exit(self):
        self.running = False

    def next_level(self):
        pass

    def end_level(self):
        self.state = "endlevel"
        if 'endlevel' in self._menus:
            self.set_menu('endlevel')
            return self.current_menu
        Bnext = Button(self.screen, 'Next', "Images/End_level/Buttons/NEXT.png",  (120, 140), "next", self)
        Bsettings = Button(self.screen, 'Settings', "Images/End_level/Buttons/SETTINGS.png",  (110, 200), "settings", self)
        Bmain = Button(self.screen, 'Main', "Images/End_level/Buttons/MAIN.png",  (115, 270), "main_menu", self)
        Bquit = Button(self.screen, 'Quit', "Images/End_level/Buttons/QUIT.png",  (110, 350), "exit", self)
        menu = Menu(self.screen, "Dead", "Images/End_level/Background.png", True, [Bmain, Bquit, Bnext, Bsettings])
        self.register_menu('endlevel', menu)
        self.set_menu('endlevel')
        return menu
    
    def end_game(self):
        self.state = "endgame"
        if 'endgame' in self._menus:
            self.set_menu('endgame')
            return self.current_menu
        Bnew = Button(self.screen, 'New', "Images/End_game/Buttons/NEW.png",  (120, 200), "new", self)
        Bmain = Button(self.screen, 'Main', "Images/End_game/Buttons/MAIN.png",  (115, 260), "main_menu", self)
        Bquit = Button(self.screen, 'Quit', "Images/End_game/Buttons/QUIT.png",  (110, 350), "exit", self)
        menu = Menu(self.screen, "Dead", "Images/End_game/Background.png", True, [Bnew, Bmain, Bquit])
        self.register_menu('endgame', menu)
        self.set_menu('endgame')
        return menu

    def respawn(self):
        pass

    def unpause(self):
        pass
