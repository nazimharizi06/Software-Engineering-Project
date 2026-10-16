from board import create_boards, resolve_move, EXITS
from character import Character, NPC
from route_config import load_npc_routes


class World:
    def __init__(self):
        self.boards = create_boards()

        self.tile_stages = {
            tile_id: stage_id
            for stage_id, board in self.boards.items()
            for tile_id in board.tiles
        }

        self.players = [
            Character("Player 1", "campus", "13"),
        ]

        config = load_npc_routes()

        self.npcs = [
            NPC(
                name,
                settings["routes"][0],
                self.tile_stages,
            )
            for name, settings in config.items()
        ]

        self.active_player_index = 0
        self.turn_number = 0

        for npc in self.npcs:
            self.validate_route(npc)

    @property
    def active_player(self):
        return self.players[self.active_player_index]

    @property
    def characters(self):
        return self.players + self.npcs

    @property
    def occupied_stages(self):
        return {
            character.stage_id
            for character in self.characters
        }

    def legal_moves(self, character):
        """
        Map clicked tile IDs to resulting (stage, tile) positions.

        Example: clicking campus tile 6 from tile 5 results
        in ("kunsela", "K16").
        """
        board = self.boards[character.stage_id]
        moves = {}

        for target_id in board.tiles:
            destination = resolve_move(
                self.boards,
                character.stage_id,
                character.tile_id,
                target_id,
            )

            if destination is not None:
                moves[target_id] = destination

        return moves

    def move_player(self, player_index, target_id):
        if player_index != self.active_player_index:
            return False

        player = self.players[player_index]
        destination = self.legal_moves(player).get(target_id)

        if destination is None:
            return False

        player.stage_id, player.tile_id = destination

        self.finish_player_turn()
        return True

    def finish_player_turn(self):
        for npc in self.npcs:
            self.advance_npc(npc)

        self.turn_number += 1

        self.active_player_index = (
            self.active_player_index + 1
        ) % len(self.players)

    def advance_npc(self, npc):
        if len(npc.tiles) == 1:
            return

        next_index, next_direction = npc.next_step()
        target_id = npc.tiles[next_index]

        destination = (
            self.tile_stages[target_id],
            target_id,
        )

        if destination not in self.legal_moves(npc).values():
            raise ValueError(
                f"{npc.name}: illegal route step "
                f"{npc.tile_id} -> {target_id}"
            )

        npc.stage_id, npc.tile_id = destination
        npc.route_index = next_index
        npc.direction = next_direction

    def validate_route(self, npc):
        """Check every route connection before gameplay begins."""
        for tile_id in npc.tiles:
            stage_id = self.tile_stages[tile_id]
            tile = self.boards[stage_id].tiles[tile_id]

            if tile.building or (stage_id, tile_id) in EXITS:
                raise ValueError(
                    f"{npc.name}: use arrival positions in routes, "
                    f"not entrance/exit trigger tile {tile_id}"
                )

        pairs = list(zip(npc.tiles, npc.tiles[1:]))

        if len(npc.tiles) > 1:
            if npc.loop_mode == "L":
                pairs.append((npc.tiles[-1], npc.tiles[0]))
            else:
                pairs += [
                    (target, source)
                    for source, target in pairs
                ]

        for source_id, target_id in pairs:
            probe = Character(
                npc.name,
                self.tile_stages[source_id],
                source_id,
            )

            destination = (
                self.tile_stages[target_id],
                target_id,
            )

            if destination not in self.legal_moves(probe).values():
                raise ValueError(
                    f"{npc.name}: invalid route connection "
                    f"{source_id} -> {target_id}"
                )