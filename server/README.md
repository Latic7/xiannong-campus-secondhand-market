# Server (FastAPI Skeleton)

This folder contains a runnable FastAPI skeleton aligned with `docs/api/openapi-draft.yaml`.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Create local config file `.env` (you can copy from `.env.example`) and fill WeChat app credentials.
4. Start server:

```bash
uvicorn app.main:app --reload --port 8000
```

Required `.env` keys:

- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `JWT_SECRET`
- `JWT_EXPIRES_SECONDS`
- `JWT_REFRESH_EXPIRES_SECONDS`

5. Open docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Structure

- `app/main.py`: application entry.
- `app/api/routers/*`: module routers (auth, users, products, orders, reports, admin).
- `app/schemas/*`: request/response schemas.
- `app/core/response.py`: unified API response helper.
