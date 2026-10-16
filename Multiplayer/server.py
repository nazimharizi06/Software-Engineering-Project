
import asyncio
import json
import secrets
import string

from websockets.asyncio.server import serve


# Store parties by their unique six-character codes
parties = {}
MAX_PLAYERS = 6


# Generate a unique party code
def generate_party_code():
    characters = string.ascii_uppercase + string.digits

    while True:
        code = "".join(secrets.choice(characters) for _ in range(6))
        if code not in parties:
            return code


# Send a JSON message to one player
async def send_message(websocket, message):
    await websocket.send(json.dumps(message))


# Find the party containing a particular player
def find_party(websocket):
    for code, party in parties.items():
        if websocket in party["players"]:
            return code, party

    return None, None


# Send the latest roster and host information to everyone
async def broadcast_party(code):
    party = parties.get(code)
    if party is None:
        return

    players = [
        player["name"]
        for player in party["players"].values()
    ]

    message = {
        "type": "party_update",
        "code": code,
        "players": players,
        "host_id": id(party["host"])
    }

    for websocket in list(party["players"]):
        try:
            await send_message(websocket, message)
        except Exception:
            pass


# Remove a player and update the remaining members
async def remove_player(websocket):
    code, party = find_party(websocket)

    if party is None:
        return

    del party["players"][websocket]

    # Delete the party when everyone leaves
    if not party["players"]:
        del parties[code]
        print(f"Party {code} closed")
        return

    # Assign a new host if the previous host leaves
    if party["host"] == websocket:
        party["host"] = next(iter(party["players"]))

    await broadcast_party(code)


# Handle messages from a connected player
async def handle_player(websocket):
    print("Player connected")

    try:
        async for raw_message in websocket:
            try:
                message = json.loads(raw_message)
                if not isinstance(message, dict):
                    raise ValueError()
            except (json.JSONDecodeError, ValueError):
                await send_message(websocket, {
                    "type": "error",
                    "message": "Invalid message"
                })
                continue

            action = message.get("type")

            if action == "create_party":
                await remove_player(websocket)

                name = str(message.get("name", "Host")).strip()[:20]
                name = name or "Host"
                code = generate_party_code()

                parties[code] = {
                    "players": {websocket: {"name": name}},
                    "host": websocket,
                    "started": False
                }

                await send_message(websocket, {
                    "type": "party_created",
                    "code": code,
                    "player_id": id(websocket)
                })

                await broadcast_party(code)
                print(f"Party created: {code}")

            elif action == "join_party":
                code = str(message.get("code", "")).strip().upper()
                name = str(message.get("name", "Player")).strip()[:20]
                name = name or "Player"

                party = parties.get(code)

                if party is None:
                    await send_message(websocket, {
                        "type": "error",
                        "message": "Party not found"
                    })
                    continue

                if party["started"]:
                    await send_message(websocket, {
                        "type": "error",
                        "message": "Game already started"
                    })
                    continue

                if websocket not in party["players"] and len(party["players"]) >= MAX_PLAYERS:
                    await send_message(websocket, {
                        "type": "error",
                        "message": "Party is full"
                    })
                    continue

                # Leave the previous party, if any
                await remove_player(websocket)

                # Check that the target party still exists
                party = parties.get(code)
                if party is None:
                    await send_message(websocket, {
                        "type": "error",
                        "message": "Party no longer exists"
                    })
                    continue

                party["players"][websocket] = {"name": name}

                await send_message(websocket, {
                    "type": "party_joined",
                    "code": code,
                    "player_id": id(websocket)
                })

                await broadcast_party(code)
                print(f"{name} joined {code}")

            elif action == "leave_party":
                await remove_player(websocket)
                await send_message(websocket, {
                    "type": "party_left"
                })

            elif action == "start_game":
                code, party = find_party(websocket)

                if party is None:
                    await send_message(websocket, {
                        "type": "error",
                        "message": "You are not in a party"
                    })
                    continue

                if party["host"] != websocket:
                    await send_message(websocket, {
                        "type": "error",
                        "message": "Only the host can start"
                    })
                    continue

                if party["started"]:
                    continue

                party["started"] = True

                for player_socket in list(party["players"]):
                    try:
                        await send_message(player_socket, {
                            "type": "game_started",
                            "code": code
                        })
                    except Exception:
                        pass

                print(f"Game started: {code}")

            else:
                await send_message(websocket, {
                    "type": "error",
                    "message": "Unknown action"
                })

    finally:
        await remove_player(websocket)
        print("Player disconnected")


# Run the server until stopped
async def main():
    async with serve(handle_player, "127.0.0.1", 8765):
        print("Campus Caper server running")
        print("WebSocket address: ws://127.0.0.1:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
