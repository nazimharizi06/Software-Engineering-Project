import pygame
import maps
from world import World

SCREENWIDTH, SCREENHEIGHT = 1280, 720
FPS = 60

class Game:
    def __init__(self):
        pygame.init()

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

    @property
    def current_view(self):
        stage_id = self.world.active_player.stage_id
        return self.states[stage_id]

    def handle_click(self, position):
        player = self.world.active_player
        view = self.current_view

        if view.character_hit(self.world, player, position):
            self.selected = not self.selected
            return

        if not self.selected:
            return

        target_id = view.tile_at(position)

        if target_id is None:
            self.selected = False
            return

        moved = self.world.move_player(
            self.world.active_player_index,
            target_id,
        )

        if moved:
            self.selected = False

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

            self.current_view.draw(
                self.world,
                selected=self.selected,
                legal_moves=legal_moves,
            )

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


# import pygame
# import sys
# import maps
# from GameStateManager import GameStateManager
# from character import Character, NPC
# from route_config import load_npc_routes

# SCREENWIDTH, SCREENHEIGHT = 1280, 720
# FPS = 60

# class Game:
#     def __init__(self):
#         pygame.init()
#         self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
#         self.clock = pygame.time.Clock()
        
#         self.gameStateManager = GameStateManager('campus')
#         self.campus = maps.Campus(self.screen, self.gameStateManager)
#         self.kunsela = maps.Kunsela(self.screen, self.gameStateManager)
        
#         self.states = {'campus': self.campus, 'kunsela': self.kunsela}

#         #TEMP
#         #TODO: Replace with tile defs later
#         self.tile_stages = {
#             str(number): "campus"
#             for number in range(1, 31)
#         }
        
#         self.tile_stages.update({
#             "K1": "level",
#             "K2": "level",
#             "K3": "level",
#         })
        
#         self.players = [
#             Character(
#                 name = "Player 1",
#                 stage_id = "campus",
#                 tile_id = "1"
#             )
#         ]
        
#         route_config = load_npc_routes()
        
#         self.npcs = [
#             NPC(
#                 name = name,
#                 route=settings["routes"][0],
#                 tile_stages=self.tile_stages,
#             )
#             for name, settings in route_config.items()
#         ]
        
#         self.turn_number = 0

#     def finish_player_turn(self):
#         self.turn += 1
        
#         for npc in self.npcs:
#             npc.advance()

#     def run(self):
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()
                    
#             self.states[self.gameStateManager.get_state()].run()
            
#             pygame.display.update()
#             self.clock.tick(FPS)