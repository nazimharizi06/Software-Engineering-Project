from dataclasses import dataclass

@dataclass
class Character:
    name: str
    stage_id: str
    tile_id: str

class NPC(Character):
    def __init__(self, name, route, tile_stages):
        tiles = tuple(route["tiles"])
        loop_mode = route["loop"]
        
        if not tiles:
            raise ValueError(f"{name}: route cannot be empty")

        if loop_mode not in ("L", "R"):
            raise ValueError(f"{name}: loop must be L or R")

        for tile in tiles:
            if tile not in tile_stages:
                raise ValueError(f"{name}: unknown tile {tile}")
            
        super().__init__(
            name=name,
            stage_id=tile_stages[tiles[0]],
            tile_id=tiles[0]
        )
        
        self.route_id = route["id"]
        self.tiles = tiles
        self.loop_mode = loop_mode
        self.route_index = 0
        self.direction = 1
        
    def next_step(self):
        if len(self.tiles) == 1:
            return self.route_index, self.direction
        
        if self.loop_mode == "L":
            index = (self.route_index + 1) % len(self.tiles)
            return index, self.direction
        
        direction = self.direction
        index = self.route_index + direction
        
        if index < 0 or index >= len(self.tiles):
            direction *= -1
            index = self.route_index + direction
            
        direction = self.direction
        index = self.route_index + direction
        
        if index < 0 or index >= len(self.tiles):
            direction *= -1
            index = self.route_index + direction
            
        return index, direction