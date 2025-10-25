import asyncio
from agent.client import AssistantClient

async def test():
    print("[TEST] Creating client...")
    client = AssistantClient(session_id="test-123", resume=False)

    print("[TEST] Initializing...")
    await client.initialize()

    print("[TEST] Setting up SDK client...")
    sdk_client = await client.setup_client()

    print("[TEST] Connecting...")
    await sdk_client.connect()

    print("[TEST] Success!")

asyncio.run(test())
