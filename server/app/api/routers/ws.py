from __future__ import annotations

import jwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.api.deps.auth import CurrentActor
from app.core.exceptions import AuthenticationError, BusinessError
from app.core.settings import settings
from app.crud import order as order_crud
from app.db.session import SessionLocal
from app.schemas.orders import OrderMessageCreateRequest
from app.services import order_service
from app.services.ws_manager import ws_manager

router = APIRouter()


def _verify_token(token: str) -> CurrentActor:
    """Validate a JWT access token from WebSocket query param."""
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthenticationError("access token invalid") from exc

    if token_data.get("typ") != "access" or not token_data.get("uid"):
        raise AuthenticationError("token type mismatch")
    return CurrentActor(
        user_id=int(token_data["uid"]),
        nickname=token_data.get("nickname", ""),
    )


@router.websocket("/ws/orders/{order_id}/chat")
async def order_chat_ws(
    ws: WebSocket,
    order_id: int,
    token: str = Query(...),
) -> None:
    # 1. Authenticate
    try:
        actor = _verify_token(token)
    except AuthenticationError:
        await ws.close(code=4001)
        return

    user_id = actor.user_id

    # 2. Verify order exists and user is participant
    db = SessionLocal()
    try:
        order = order_crud.get_order(db, order_id)
        if order is None:
            await ws.close(code=4004, reason="order not found")
            return
        if user_id not in {order.buyer_id, order.seller_id}:
            await ws.close(code=4003, reason="forbidden")
            return
    finally:
        db.close()

    # 3. Accept connection and register
    await ws_manager.connect(order_id, user_id, ws)

    try:
        while True:
            raw = await ws.receive_json()
            msg_type = raw.get("type", "")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})

            elif msg_type == "message":
                content = raw.get("content", "").strip()
                if not content:
                    await ws.send_json({"type": "error", "message": "content is empty"})
                    continue

                # Save message to database
                payload = OrderMessageCreateRequest(content=content)
                db = SessionLocal()
                try:
                    result = order_service.create_message(db, order_id, payload, actor)
                    # Broadcast to ALL participants in the room
                    await ws_manager.broadcast(order_id, {
                        "type": "new_message",
                        "data": result,
                    })
                except BusinessError as exc:
                    db.rollback()
                    await ws.send_json({"type": "error", "message": exc.message})
                except Exception:
                    db.rollback()
                    await ws.send_json({"type": "error", "message": "internal error"})
                finally:
                    db.close()

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        ws_manager.disconnect(order_id, user_id)
