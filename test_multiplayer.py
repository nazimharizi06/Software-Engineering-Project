import asyncio
from pathlib import Path
import sys
import unittest

from Multiplayer.client import MultiplayerClient


TIMEOUT = 5
PROJECT_ROOT = Path(__file__).resolve().parent

# Use the real server handler, but choose an available port.
SERVER_SCRIPT = """
import asyncio
from websockets.asyncio.server import serve
from Multiplayer.server import handle_player

async def main():
    async with serve(handle_player, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        print(port, flush=True)
        await asyncio.Future()

asyncio.run(main())
"""


class MultiplayerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.clients = []

        self.server = await asyncio.create_subprocess_exec(
            sys.executable,
            "-B",
            "-u",
            "-c",
            SERVER_SCRIPT,
            cwd=str(PROJECT_ROOT),
            stdout=asyncio.subprocess.PIPE,
            # Keep server exceptions visible in the terminal.
            stderr=None,
        )

        line = await asyncio.wait_for(
            self.server.stdout.readline(),
            timeout=TIMEOUT,
        )

        try:
            port = int(line.decode().strip())
        except ValueError:
            self.fail(
                "Test server did not report a port. "
                "Check the server traceback above."
            )

        self.url = f"ws://127.0.0.1:{port}"

    async def asyncTearDown(self):
        for client in self.clients:
            if client.websocket is not None:
                try:
                    await asyncio.wait_for(
                        client.websocket.close(),
                        timeout=2,
                    )
                except Exception:
                    pass

        if self.server.returncode is None:
            self.server.kill()

        await self.server.wait()

    async def wait_until(self, condition):
        async def poll():
            while True:
                for client in self.clients:
                    client.process_messages()

                if condition():
                    return

                await asyncio.sleep(0.01)

        await asyncio.wait_for(poll(), timeout=TIMEOUT)

    async def wait_event(self, client, event_type):
        async def poll():
            while True:
                events = client.process_messages()

                for event in events:
                    if event["type"] == "error":
                        if event_type == "error":
                            return event

                        self.fail(
                            f"Unexpected server error: "
                            f"{event['message']}"
                        )

                    if event["type"] == event_type:
                        return event

                await asyncio.sleep(0.01)

        return await asyncio.wait_for(
            poll(),
            timeout=TIMEOUT,
        )

    async def new_client(self):
        client = MultiplayerClient()
        client.server_url = self.url

        self.clients.append(client)
        await client.connect()

        return client

    async def create_lobby(self, count):
        host = await self.new_client()
        await host.create_party("Host")
        await self.wait_event(host, "party_created")

        members = [host]
        code = host.party_code

        for number in range(2, count + 1):
            client = await self.new_client()
            await client.join_party(code, f"Player {number}")
            await self.wait_event(client, "party_joined")
            members.append(client)

        await self.wait_until(
            lambda: all(
                len(client.players) == count
                for client in members
            )
        )

        return members

    async def assert_game_starts(self, members):
        hosts = [client for client in members if client.is_host]
        self.assertEqual(len(hosts), 1)

        await hosts[0].start_game()

        for client in members:
            event = await self.wait_event(client, "game_started")
            self.assertEqual(event["code"], client.party_code)

    async def test_multiple_players_join_and_start(self):
        members = await self.create_lobby(3)

        self.assertEqual(
            len({client.player_id for client in members}),
            3,
        )

        self.assertEqual(
            len({client.party_code for client in members}),
            1,
        )

        for client in members:
            self.assertCountEqual(
                client.players,
                ["Host", "Player 2", "Player 3"],
            )

        await self.assert_game_starts(members)

    async def test_six_players_join_seventh_is_rejected(self):
        members = await self.create_lobby(6)

        extra = await self.new_client()
        await extra.join_party(
            members[0].party_code,
            "Player 7",
        )

        error = await self.wait_event(extra, "error")

        self.assertEqual(error["message"], "Party is full")
        self.assertIsNone(extra.party_code)

        for client in members:
            self.assertEqual(len(client.players), 6)

        await self.assert_game_starts(members)

    async def test_player_leaves_without_breaking_lobby(self):
        host, departing, remaining = await self.create_lobby(3)

        await departing.leave_party()
        await self.wait_event(departing, "party_left")

        await self.wait_until(
            lambda: len(host.players) == 2
            and len(remaining.players) == 2
        )

        self.assertIsNone(departing.party_code)
        self.assertIsNone(self.server.returncode)

        await self.assert_game_starts([host, remaining])

    async def test_player_window_closes_without_breaking_lobby(self):
        host, departing, remaining = await self.create_lobby(3)

        # Simulates the client connection disappearing without
        # sending the leave_party message.
        await departing.websocket.close()

        await self.wait_until(
            lambda: len(host.players) == 2
            and len(remaining.players) == 2
        )

        self.assertIsNone(self.server.returncode)

        await self.assert_game_starts([host, remaining])

    async def test_host_disconnect_assigns_new_host(self):
        host, second, third = await self.create_lobby(3)
        original_code = host.party_code

        await host.websocket.close()

        await self.wait_until(
            lambda: len(second.players) == 2
            and len(third.players) == 2
            and sum(
                client.is_host
                for client in (second, third)
            ) == 1
        )

        self.assertEqual(second.party_code, original_code)
        self.assertEqual(third.party_code, original_code)
        self.assertIsNone(self.server.returncode)

        await self.assert_game_starts([second, third])

    async def test_server_crash_disconnects_clients(self):
        members = await self.create_lobby(3)
        await self.assert_game_starts(members)

        # Kill ONLY the server subprocess created by this test.
        self.server.kill()
        await self.server.wait()

        await self.wait_until(
            lambda: all(
                not client.connected
                for client in members
            )
        )

        for client in members:
            self.assertFalse(client.connected)

        # In the current implementation this silently returns
        # without sending anything because connected is False.
        await asyncio.wait_for(
            members[0].start_game(),
            timeout=TIMEOUT,
        )

        # A send-based action tries to reconnect. With the
        # server gone, it should raise a connection error.
        with self.assertRaises(OSError):
            await asyncio.wait_for(
                members[0].create_party("Reconnect attempt"),
                timeout=TIMEOUT,
            )

    @unittest.skip(
        "No scene/location synchronization protocol exists "
        "in this branch; requires game integration testing."
    )
    async def test_players_in_different_scenes(self):
        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)