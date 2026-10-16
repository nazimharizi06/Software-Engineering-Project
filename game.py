import pygame
import sys
import maps
from GameStateManager import GameStateManager
from UI.main_menu import MainMenu
from UI.multiplayer_menu import MultiplayerMenu

SCREENWIDTH, SCREENHEIGHT = 1280, 720
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.clock = pygame.time.Clock()
        
        self.gameStateManager = GameStateManager('main_menu')
        self.start = maps.Start(self.screen, self.gameStateManager)
        self.level = maps.Level(self.screen, self.gameStateManager) 
        
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.multiplayerMenu = MultiplayerMenu(self.screen, self.gameStateManager)
        
        self.states = {'start': self.start, 'level': self.level, 'main_menu': self.mainMenu, 'multiplayer_menu': self.multiplayerMenu}

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                active_screen = self.states[self.gameStateManager.get_state()]
                if hasattr(active_screen, 'handle_event'):
                    if not active_screen.handle_event(event):
                        pygame.quit()
                        sys.exit()
                    
            self.states[self.gameStateManager.get_state()].run()
            
            pygame.display.update()
            self.clock.tick(FPS)