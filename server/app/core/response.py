from datetime import datetime, timezone
from uuid import uuid4


def api_ok(data=None, message: str = "ok", code: int = 0) -> dict:
    return {
        "code": code,
        "message": message,
        "data": data,
        "requestId": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def api_error(message: str, code: int, data=None) -> dict:
    return {
        "code": code,
        "message": message,
        "data": data,
        "requestId": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
