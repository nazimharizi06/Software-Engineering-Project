import pygame
import sys
import maps
from GameStateManager import GameStateManager

SCREENWIDTH, SCREENHEIGHT = 1280, 720
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.clock = pygame.time.Clock()
        
        self.gameStateManager = GameStateManager('start')
        self.start = maps.Start(self.screen, self.gameStateManager)
        self.level = maps.Level(self.screen, self.gameStateManager)
        
        self.states = {'start': self.start, 'level': self.level}

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            self.states[self.gameStateManager.get_state()].run()
            
            pygame.display.update()
            self.clock.tick(FPS)