import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws/research/{session_id}")
async def research_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint streaming granular real-time research progress events."""
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            # Keep-alive receive loop
            data = await websocket.receive_text()
            logger.debug(f"Received message from client in session {session_id}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
        logger.info(f"Client disconnected from WebSocket session {session_id}")
    except Exception as e:
        logger.warning(f"WebSocket connection error on session {session_id}: {e}")
        ws_manager.disconnect(session_id, websocket)
