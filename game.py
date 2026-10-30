from email.mime import message
import os
import pygame
import maps
from world import World

SCREENWIDTH, SCREENHEIGHT = 1280, 720
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        
        ###
        pygame.mixer.init()
        pygame.mixer.music.load("audio/music/leberch-suspense-581371.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        ###

        self.screen = pygame.display.set_mode(
            (SCREENWIDTH, SCREENHEIGHT)
        )

        pygame.display.set_caption("Campus Movement Prototype")

        self.clock = pygame.time.Clock()
        self.world = World()

        self.states = {
            "campus": maps.Campus(
                self.screen,
                self.world.boards["campus"],
            ),
            "kunsela": maps.Kunsela(
                self.screen,
                self.world.boards["kunsela"],
            ),
        }

        self.selected = False
        self.selected_tile = None
        self.inspected_tile = None

    @property
    def current_view(self):
        stage_id = self.world.active_player.stage_id
        return self.states[stage_id]

    def handle_click(self, position):
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

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    self.handle_click(event.pos)

            legal_moves = {}

            if self.selected:
                legal_moves = self.world.legal_moves(
                    self.world.active_player
                )

            visible_tiles = set()

            if self.inspected_tile is not None:
                visible_tiles = (
                    self.current_view.board.tiles_that_see(
                        self.inspected_tile
                    )
                )

            self.current_view.draw(
                self.world,
                selected=self.selected,
                legal_moves=legal_moves,
                visible_tiles=visible_tiles,
                inspected_tile=self.inspected_tile,
            )

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.mixer.music.stop()
        pygame.quit()