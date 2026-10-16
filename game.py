from email.mime import message
import os
import pygame
import asyncio
import sys
import maps
from GameStateManager import GameStateManager
from UI.main_menu import MainMenu
from UI.multiplayer_menu import MultiplayerMenu
from UI.lobby import Lobby
from Multiplayer.client import MultiplayerClient
from UI.join_party import JoinParty

SCREENWIDTH, SCREENHEIGHT = 1280, 720
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        self.gameStateManager = GameStateManager('main_menu')
        self.multiplayerClient = MultiplayerClient()
        self.start = maps.Start(self.screen, self.gameStateManager)
        self.level = maps.Level(self.screen, self.gameStateManager) 
        
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.multiplayerMenu = MultiplayerMenu(self.screen, self.gameStateManager)
        self.lobby = Lobby(self.screen, self.gameStateManager)
        self.joinParty = JoinParty(self.screen, self.gameStateManager)
        
        self.states = {'start': self.start, 'level': self.level, 'main_menu': self.mainMenu, 'multiplayer_menu': self.multiplayerMenu, 'lobby': self.lobby, 'join_party': self.joinParty}
        
        # Give both screens access to the same connection
        self.lobby.client = self.multiplayerClient
        self.multiplayerMenu.client = self.multiplayerClient

        # Share the multiplayer connection with the Join Party screen
        self.joinParty.client = self.multiplayerClient

    async def run(self):
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

            # Apply messages received from the server
            for message in self.multiplayerClient.process_messages():
                event_type = message.get("type")

                if event_type == "party_update":
                    #update lobby information 
                        self.lobby.update_lobby(
                            message["code"],
                            message["players"],
                            self.multiplayerClient.is_host
                        )
                elif event_type == "party_joined":
                    #open the lobby when the player successfully joins a party
                    if self.gameStateManager.get_state() == "join_party":
                        self.joinParty.waiting = False
                        self.joinParty.message = "Joined the party"
                        self.gameStateManager.set_state("lobby")

                elif event_type == "party_left":
                    self.lobby.update_lobby("------", [], True)
                    self.joinParty.waiting = False
                    self.joinParty.message = "Left the party"
                    #return to the multiplayer menu when the player leaves a party
                    self.gameStateManager.set_state("multiplayer_menu")

                elif event_type == "error":
                    #print the error from the server
                    print("Multiplayer error:", message["message"])

                    #show the error on the Join Party screen
                    if self.gameStateManager.get_state() == "join_party":
                        self.joinParty.message = message["message"]
                        self.joinParty.waiting = False
                       
                elif event_type == "game_started":
                    self.gameStateManager.set_state("level")

            pygame.display.update()
            self.clock.tick(FPS)
            await asyncio.sleep(0)  # Allow other tasks to run