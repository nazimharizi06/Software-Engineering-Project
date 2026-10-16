from character import NPC
from route_config import load_npc_routes

def collect_positions(npc, moves):
    positions = [npc.tile_id]
    
    for _ in range(moves):
        npc.advance()
        positions.append(npc.tile_id)
        
    return positions

def main():
    config = load_npc_routes()
    
    tile_stages = {
        "1": "start",
        "2": "start",
        "3": "start",
        "K1": "level",
        "K2": "level",
        "K3": "level",
    }
    
    professor = NPC(
        "Professor",
        config["Professor"]["routes"][0],
        tile_stages,
    )
    
    ta = NPC(
        "TA1",
        config["TA1"]["routes"][0],
        tile_stages,
    )
    
    professor_positions = collect_positions(professor, 6)
    ta_positions = collect_positions(ta, 6)
    
    assert professor_positions == [
        "1", "2", "3", "K1", "K2", "1", "2"
    ]
    
    assert ta_positions == [
        "K3", "K2", "K1", "K2", "K3", "K2", "K1"
    ]
    
    assert professor.stage_id == "start"
    assert ta.stage_id == "level"
    
    print("Both NPC patrol checks passed.")
    
if __name__ == "__main__":
    main()