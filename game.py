
import asyncio
import sys
import pygame
import maps

from world import World
from GameStateManager import GameStateManager
from UI.main_menu import MainMenu
from UI.multiplayer_menu import MultiplayerMenu
from UI.lobby import Lobby
from UI.join_party import JoinParty
from Multiplayer.client import MultiplayerClient

SCREENWIDTH, SCREENHEIGHT = 1280, 720
FPS = 60


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (SCREENWIDTH, SCREENHEIGHT), pygame.SCALED
        )
        pygame.display.set_caption("Campus Caper")
        self.clock = pygame.time.Clock()

        # Set up menus and multiplayer
        self.gameStateManager = GameStateManager("main_menu")
        self.multiplayerClient = MultiplayerClient()

        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.multiplayerMenu = MultiplayerMenu(self.screen, self.gameStateManager)
        self.lobby = Lobby(self.screen, self.gameStateManager)
        self.joinParty = JoinParty(self.screen, self.gameStateManager)

        self.states = {
            "main_menu": self.mainMenu,
            "multiplayer_menu": self.multiplayerMenu,
            "lobby": self.lobby,
            "join_party": self.joinParty,
        }

        # Share the connection between multiplayer screens
        self.lobby.client = self.multiplayerClient
        self.multiplayerMenu.client = self.multiplayerClient
        self.joinParty.client = self.multiplayerClient

        # Set up Henry's world and map views
        self.world = World()

        self.board_views = {
            "campus": maps.Campus(
                self.screen, self.world.boards["campus"]
            ),
            "kunsela": maps.Kunsela(
                self.screen, self.world.boards["kunsela"]
            ),
        }

        self.selected = False
        self.inspected_tile = None

    @property
    def current_view(self):
        stage_id = self.world.active_player.stage_id
        return self.board_views[stage_id]

    def handle_click(self, position):
        # Keep Henry's character selection and movement logic
        player = self.world.active_player
        view = self.current_view

        if view.character_hit(self.world, player, position):
            self.selected = not self.selected
            self.inspected_tile = None
            return

        target_id = view.tile_at(position)

        if target_id is None:
            self.selected = False
            self.inspected_tile = None
            return

        if self.selected:
            legal_moves = self.world.legal_moves(player)

            if target_id in legal_moves:
                moved = self.world.move_player(
                    self.world.active_player_index,
                    target_id,
                )

                if moved:
                    self.selected = False
                    self.inspected_tile = None

                return

        self.selected = False

        if self.inspected_tile == target_id:
            self.inspected_tile = None
        else:
            self.inspected_tile = target_id

    def draw_board(self):
        # Render Henry's board, movement highlights, and visibility
        legal_moves = {}

        if self.selected:
            legal_moves = self.world.legal_moves(
                self.world.active_player
            )

        visible_tiles = set()

        if self.inspected_tile is not None:
            visible_tiles = self.current_view.board.tiles_that_see(
                self.inspected_tile
            )

        self.current_view.draw(
            self.world,
            selected=self.selected,
            legal_moves=legal_moves,
            visible_tiles=visible_tiles,
            inspected_tile=self.inspected_tile,
        )

    def process_multiplayer_messages(self):
        # Process messages received from the multiplayer server
        for message in self.multiplayerClient.process_messages():
            event_type = message.get("type")

            if event_type == "party_update":
                self.lobby.update_lobby(
                    message["code"],
                    message["players"],
                    self.multiplayerClient.is_host,
                )

            elif event_type == "party_joined":
                if self.gameStateManager.get_state() == "join_party":
                    self.joinParty.waiting = False
                    self.joinParty.message = "Joined the party"
                    self.gameStateManager.set_state("lobby")

            elif event_type == "party_left":
                self.lobby.update_lobby("------", [], False)
                self.joinParty.waiting = False
                self.joinParty.message = "Left the party"
                self.gameStateManager.set_state("multiplayer_menu")

            elif event_type == "error":
                print("Multiplayer error:", message["message"])

                if self.gameStateManager.get_state() == "join_party":
                    self.joinParty.message = message["message"]
                    self.joinParty.waiting = False

            elif event_type == "game_started":
                # Both clients enter Henry's gameplay screen
                self.selected = False
                self.inspected_tile = None
                self.gameStateManager.set_state("level")

    async def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                state = self.gameStateManager.get_state()

                if state == "level":
                    if (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                    ):
                        self.handle_click(event.pos)
                else:
                    active_screen = self.states.get(state)

                    if active_screen and hasattr(active_screen, "handle_event"):
                        if not active_screen.handle_event(event):
                            pygame.quit()
                            return

            self.process_multiplayer_messages()

            state = self.gameStateManager.get_state()

            if state == "level":
                self.draw_board()
            elif state in self.states:
                self.states[state].run()

            pygame.display.update()
            self.clock.tick(FPS)

            # Keep networking responsive while the game runs
            await asyncio.sleep(0)
