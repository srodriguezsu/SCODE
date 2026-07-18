from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps task_id -> list of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
        logger.info(f"WebSocket client connected for task {task_id}. Total clients: {len(self.active_connections[task_id])}")

    def disconnect(self, task_id: str, websocket: WebSocket):
        if task_id in self.active_connections:
            try:
                self.active_connections[task_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
                logger.info(f"All clients disconnected for task {task_id}. Cleaned up connection list.")
            else:
                logger.info(f"Client disconnected for task {task_id}. Remaining clients: {len(self.active_connections[task_id])}")

    async def broadcast_to_task(self, task_id: str, message: dict):
        if task_id in self.active_connections:
            logger.info(f"Broadcasting update to task {task_id}: {message.get('status', 'no-status')}")
            # Iterate on a copy to avoid modification-during-iteration bugs
            for connection in list(self.active_connections[task_id]):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send websocket message to a client on task {task_id}: {e}")
                    # We will handle cleanup during disconnect/error handling in websocket loop

manager = ConnectionManager()
