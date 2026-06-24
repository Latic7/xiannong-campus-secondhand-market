from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections grouped by order_id.

    Each order has a room where all participants (buyer + seller)
    can receive real-time message broadcasts.
    """

    def __init__(self) -> None:
        # order_id -> {user_id: WebSocket}
        self._connections: dict[int, dict[int, WebSocket]] = defaultdict(dict)

    async def connect(self, order_id: int, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[order_id][user_id] = ws

    def disconnect(self, order_id: int, user_id: int) -> None:
        if order_id in self._connections:
            self._connections[order_id].pop(user_id, None)
            if not self._connections[order_id]:
                del self._connections[order_id]

    async def broadcast(self, order_id: int, message: dict) -> None:
        """Send a JSON message to all users in an order's room."""
        for uid, ws in self._connections.get(order_id, {}).items():
            try:
                await ws.send_json(message)
            except Exception:
                pass

    @property
    def active_rooms(self) -> int:
        return len(self._connections)


ws_manager = ConnectionManager()
