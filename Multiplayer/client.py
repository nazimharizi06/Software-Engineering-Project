
import asyncio
import json

import websockets


class MultiplayerClient:
    def __init__(self):
        # WebSocket server running on this computer
        self.server_url = "ws://127.0.0.1:8765"
        self.websocket = None

        # Information about the current party
        self.party_code = None
        self.player_id = None
        self.players = []
        self.is_host = False
        self.connected = False

        # Messages waiting to be processed by the game
        self.messages = asyncio.Queue()

    # Connect to the multiplayer server
    async def connect(self):
        if self.connected:
            return

        self.websocket = await websockets.connect(self.server_url)
        self.connected = True

        # Start listening without blocking the game
        asyncio.create_task(self.listen())

    # Listen for messages from the server
    async def listen(self):
        try:
            async for raw_message in self.websocket:
                message = json.loads(raw_message)
                await self.messages.put(message)

        except websockets.exceptions.ConnectionClosed:
            pass

        finally:
            self.connected = False

    # Send a JSON message to the server
    async def send(self, message):
        if not self.connected:
            await self.connect()

        await self.websocket.send(json.dumps(message))

    # Create a new multiplayer party
    async def create_party(self, name="Player"):
        await self.send({
            "type": "create_party",
            "name": name
        })

    # Join an existing party
    async def join_party(self, code, name="Player"):
        await self.send({
            "type": "join_party",
            "code": code,
            "name": name
        })

    # Leave the current party
    async def leave_party(self):
        if self.connected:
            await self.send({"type": "leave_party"})

    # Ask the server to start the game
    async def start_game(self):
        if self.connected:
            await self.send({"type": "start_game"})

    # Process messages received from the server
    def process_messages(self):
        events = []

        while not self.messages.empty():
            message = self.messages.get_nowait()
            event_type = message.get("type")

            if event_type in ("party_created", "party_joined"):
                self.party_code = message["code"]
                self.player_id = message["player_id"]

            elif event_type == "party_update":
                self.party_code = message["code"]
                self.players = message["players"]
                self.is_host = (
                    self.player_id == message["host_id"]
                )

            elif event_type == "party_left":
                self.party_code = None
                self.player_id = None
                self.players = []
                self.is_host = False

            events.append(message)

        return events
