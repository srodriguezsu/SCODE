from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
import logging

from api.config import CORS_ORIGINS
from api.websocket_manager import manager
from api.tasks import run_recommendation_flow

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SCODE Cohesion Recommender API",
    description="Calculates cohesive team recommendations using a Decision Tree model and manages async results via WebSockets.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SCODE Recommender API is running."}

@app.post("/projects/{project_id}/recommend")
async def recommend_teams_endpoint(
    project_id: int,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """
    Triggers the team recommendation flow.
    Requires an Authorization header containing the JWT token.
    Resolves immediately and returns a task_id to follow progress via WebSocket.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )
        
    task_id = str(uuid.uuid4())
    logger.info(f"Received recommendation request for project: {project_id}. Task ID assigned: {task_id}")
    
    # Schedule the recommendation flow in the background
    background_tasks.add_task(
        run_recommendation_flow,
        task_id=task_id,
        project_id=project_id,
        auth_header=authorization
    )
    
    return {
        "status": "processing",
        "message": "Petición de recomendación de equipos recibida. Conéctese al WebSocket /ws/{task_id} para seguir el progreso.",
        "task_id": task_id
    }

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint to receive real-time updates for a running recommendation task.
    """
    logger.info(f"WebSocket client attempting to connect for task: {task_id}")
    try:
        await manager.connect(task_id, websocket)
    except Exception as e:
        logger.error(f"Failed to connect WebSocket for task {task_id}: {str(e)}")
        return
        
    try:
        while True:
            # We keep the connection alive by waiting for messages.
            # In a production context, clients might send heartbeat pings.
            data = await websocket.receive_text()
            logger.debug(f"Received from client {task_id}: {data}")
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for task: {task_id}")
        manager.disconnect(task_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {str(e)}")
        manager.disconnect(task_id, websocket)
