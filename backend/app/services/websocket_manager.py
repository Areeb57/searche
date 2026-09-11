import json
import logging
from collections import defaultdict
from typing import Any, Dict, List, Set
from fastapi import WebSocket
from app.schemas.websocket import WebSocketEvent

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages active WebSocket connections grouped by research session ID."""

    def __init__(self):
        # Maps session_id -> Set of active WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # In-memory history buffer of events per session (last 50 events)
        self.event_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket client connected to session: {session_id} (Total: {len(self.active_connections[session_id])})")

        # Replay event history to newly joined client
        history = self.event_history.get(session_id, [])
        for event in history:
            try:
                await websocket.send_json(event)
            except Exception as e:
                logger.debug(f"Failed replaying event history: {e}")
                break

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket client disconnected from session: {session_id}")

    async def broadcast(self, event: WebSocketEvent) -> None:
        """Broadcast event to all clients listening on this research session."""
        session_id = event.session_id
        event_dict = event.model_dump()

        # Buffer in history
        history = self.event_history[session_id]
        history.append(event_dict)
        if len(history) > 100:
            history.pop(0)

        connections = self.active_connections.get(session_id, set()).copy()
        dead_connections = []

        for ws in connections:
            try:
                await ws.send_json(event_dict)
            except Exception as e:
                logger.warning(f"Error sending WebSocket event to client on {session_id}: {e}")
                dead_connections.append(ws)

        for dead in dead_connections:
            self.disconnect(session_id, dead)


ws_manager = WebSocketManager()
