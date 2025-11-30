import asyncio
import websockets
import json

async def test_soul_connection():
    uri = "ws://127.0.0.1:8001/ws/soul"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Listen for 3 messages
            for i in range(3):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received event {i+1}: {data['type']}")
                print(f"  Data: {data['data']}")
            
            print("Verification successful: Received simulated events.")
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_soul_connection())
