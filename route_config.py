import json
from pathlib import Path

def load_npc_routes():
    path = (
        Path(__file__).resolve().parent
        / "config"
        / "npc_routes.json"
    )
    
    with path.open(encoding="utf-8") as file:
        config = json.load(file)
    
    if not isinstance(config, dict):
        raise ValueError("NPC configuration must be an object")
    
    for name, settings in config.items():
        if not isinstance(settings, dict):
            raise ValueError(f"{name}: settings must be an objct")
        
        routes = settings.get("routes")
        
        if not isinstance(routes, list) or not routes:
            raise ValueError(f"{name}: routes must be a nonempty list")
        
        route_ids = set()
        
        for route in routes:
            if not isinstance(route, dict):
                raise ValueError(f"{name}: each route must be an object")
            
            route_id = route.get("id")
            
            if not isinstance(route_id, str) or not route_id:
                raise ValueError(f"{name}: route needs a nonempty id")
            
            if route_id in route_ids:
                raise ValueError(f"{name}: duplicate route id {route_id}")
            
            route_ids.add(route_id)
            
            if route.get("loop") not in ("L", "R"):
                raise ValueError(f"{name}/{route_id}: loop must be L or R")
            
            tiles = route.get("tiles")
            
            if (
                not isinstance(tiles, list)
                or not tiles
                or any(
                    not isinstance(tile, str) or not tile
                    for tile in tiles
                )
            ):
                raise ValueError(
                    f"{name}/{route_id}: tiles must be a nonempty "
                    "list of tile strings"
                )

    return config