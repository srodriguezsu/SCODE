from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps task_id -> list of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Maps task_id -> list of historical messages sent
        self.message_history: Dict[str, List[dict]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        
        # Send confirmation handshake first
        try:
            await websocket.send_json({
                "status": "connected",
                "message": f"Conectado a las actualizaciones de recomendación para la tarea {task_id}."
            })
        except Exception as e:
            logger.error(f"Failed to send connection confirmation to task {task_id}: {e}")
            raise
            
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
        logger.info(f"WebSocket client connected for task {task_id}. Total clients: {len(self.active_connections[task_id])}")
        
        # Replay any history if messages were already generated before connection was established
        if task_id in self.message_history:
            logger.info(f"Replaying {len(self.message_history[task_id])} historical messages to client for task {task_id}")
            for message in self.message_history[task_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send replayed message to client on task {task_id}: {e}")

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
        # Append message to history
        if task_id not in self.message_history:
            self.message_history[task_id] = []
        self.message_history[task_id].append(message)
        
        if task_id in self.active_connections:
            logger.info(f"Broadcasting update to task {task_id}: {message.get('status', 'no-status')}")
            # Iterate on a copy to avoid modification-during-iteration bugs
            for connection in list(self.active_connections[task_id]):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send websocket message to a client on task {task_id}: {e}")

    def clean_task(self, task_id: str):
        if task_id in self.message_history:
            del self.message_history[task_id]
            logger.info(f"Cleaned up message history for task {task_id}")

manager = ConnectionManager()
