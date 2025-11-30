import asyncio
import json
import random
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

class RealTimeManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.is_simulating = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        if not self.is_simulating:
            self.is_simulating = True
            asyncio.create_task(self.start_simulation())

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if not self.active_connections:
            self.is_simulating = False

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Handle broken connections gracefully
                pass

    async def start_simulation(self):
        """
        Simulates backend activity ("Nerve Center" pulses) when no real activity is happening.
        This ensures the "Soul" page is always alive.
        """
        event_types = [
            "RULE_MINED",
            "CAUSAL_LINK_FOUND",
            "PROFIT_CALCULATED",
            "CONTEXT_SWITCH",
            "OPTIMIZATION_CYCLE"
        ]
        
        entities = ["Product_A", "Product_B", "Category_X", "Store_1", "Region_North", "Customer_Segment_Y"]

        while self.is_simulating:
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            event = {
                "type": random.choice(event_types),
                "data": {
                    "entity_source": random.choice(entities),
                    "entity_target": random.choice(entities),
                    "value": random.uniform(0.1, 0.9),
                    "confidence": random.uniform(0.5, 1.0)
                }
            }
            await self.broadcast(event)

manager = RealTimeManager()
