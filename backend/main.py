import json
import os
import secrets
import sqlite3
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/chat.db")
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1024"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app = FastAPI(title="Conversational AI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

bearer = HTTPBearer(auto_error=False)
rate_windows: dict[str, deque[float]] = defaultdict(deque)
RATE_LIMITS = {"chat": (10, 60), "api": (60, 60)}
gemini_client = httpx.AsyncClient(timeout=httpx.Timeout(120.0))


class SessionCreate(BaseModel):
    title: str | None = "New Chat"


class MessageCreate(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    directory = os.path.dirname(DATABASE_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages(session_id, id);
            """
        )


@app.on_event("startup")
async def startup() -> None:
    initialize_database()


@app.on_event("shutdown")
async def shutdown() -> None:
    await gemini_client.aclose()


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    if not API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_BEARER_TOKEN is not configured on the backend.",
        )
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer token required")
    if not secrets.compare_digest(credentials.credentials, API_BEARER_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid bearer token")


def client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path == "/api/health" or request.method == "OPTIONS":
        return await call_next(request)
    bucket = "chat" if request.url.path.endswith("/chat") else "api"
    limit, window = RATE_LIMITS[bucket]
    key = f"{bucket}:{client_key(request)}"
    now = time.monotonic()
    timestamps = rate_windows[key]
    while timestamps and timestamps[0] <= now - window:
        timestamps.popleft()
    if len(timestamps) >= limit:
        retry_after = max(1, int(window - (now - timestamps[0])))
        return JSONResponse(
            {"detail": "Rate limit exceeded"},
            status_code=429,
            headers={"Retry-After": str(retry_after)},
        )
    timestamps.append(now)
    return await call_next(request)


def session_exists(connection: sqlite3.Connection, session_id: str) -> bool:
    return connection.execute(
        "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
    ).fetchone() is not None


def session_summary(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sessions", dependencies=[Depends(require_auth)])
async def list_sessions() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
        ).fetchall()
    return [session_summary(row) for row in rows]


@app.post("/api/sessions", dependencies=[Depends(require_auth)])
async def create_session(body: SessionCreate) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    timestamp = now_iso()
    title = body.title or "New Chat"
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (session_id, title, timestamp, timestamp),
        )
    return {"id": session_id, "title": title, "created_at": timestamp, "updated_at": timestamp}


@app.get("/api/sessions/{session_id}", dependencies=[Depends(require_auth)])
async def get_session(session_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        session = connection.execute(
            "SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        messages = connection.execute(
            "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
    return {**session_summary(session), "messages": [dict(message) for message in messages]}


@app.delete("/api/sessions/{session_id}", dependencies=[Depends(require_auth)])
async def delete_session(session_id: str) -> dict[str, str]:
    with get_connection() as connection:
        if not session_exists(connection, session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        connection.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        connection.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return {"status": "deleted"}


@app.patch("/api/sessions/{session_id}", dependencies=[Depends(require_auth)])
async def update_session(session_id: str, body: SessionCreate) -> dict[str, Any]:
    timestamp = now_iso()
    with get_connection() as connection:
        if not session_exists(connection, session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        if body.title:
            connection.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (body.title, timestamp, session_id),
            )
        session = connection.execute(
            "SELECT id, title, updated_at FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    return dict(session)


@app.post("/api/sessions/{session_id}/messages", dependencies=[Depends(require_auth)])
async def add_message(session_id: str, body: MessageCreate) -> dict[str, Any]:
    timestamp = now_iso()
    with get_connection() as connection:
        if not session_exists(connection, session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        connection.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, body.role, body.content, timestamp),
        )
        connection.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?", (timestamp, session_id)
        )
    return {"role": body.role, "content": body.content, "created_at": timestamp}


def build_gemini_contents(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "role": "model" if message["role"] == "assistant" else "user",
            "parts": [{"text": message["content"]}],
        }
        for message in history
        if message["role"] in ("user", "assistant")
    ]


async def stream_gemini(contents: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
    if not GEMINI_API_KEY:
        yield f'data: {json.dumps({"error": "GEMINI_API_KEY is not configured on the backend."})}\n\n'
        return
    payload = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": GEMINI_MAX_OUTPUT_TOKENS},
    }
    url = f"{GEMINI_API_URL}/{GEMINI_MODEL}:streamGenerateContent"
    async with gemini_client.stream(
        "POST", url, params={"alt": "sse", "key": GEMINI_API_KEY},
        headers={"content-type": "application/json"}, json=payload,
    ) as response:
        if response.status_code != 200:
            body = await response.aread()
            yield f'data: {json.dumps({"error": body.decode("utf-8", errors="replace")})}\n\n'
            return
        async for line in response.aiter_lines():
            if not line or not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            candidates = event.get("candidates", [])
            if not candidates:
                continue
            for part in candidates[0].get("content", {}).get("parts", []):
                if part.get("text"):
                    yield f'data: {json.dumps({"text": part["text"]})}\n\n'
        yield 'data: {"stop": true}\n\n'


@app.post("/api/sessions/{session_id}/chat", dependencies=[Depends(require_auth)])
async def chat(session_id: str, body: ChatRequest) -> StreamingResponse:
    timestamp = now_iso()
    with get_connection() as connection:
        if not session_exists(connection, session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        connection.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, "user", body.message, timestamp),
        )
        connection.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?", (timestamp, session_id)
        )
        history = connection.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
    api_messages = build_gemini_contents([dict(message) for message in history])

    async def generate() -> AsyncGenerator[str, None]:
        full_text = ""
        try:
            async for chunk in stream_gemini(api_messages):
                full_text += _extract_text(chunk)
                yield chunk
        finally:
            assistant_timestamp = now_iso()
            with get_connection() as connection:
                connection.execute(
                    "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                    (session_id, "assistant", full_text, assistant_timestamp),
                )
                connection.execute(
                    "UPDATE sessions SET updated_at = ? WHERE id = ?",
                    (assistant_timestamp, session_id),
                )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


def _extract_text(sse_data: str) -> str:
    if not sse_data.startswith("data:"):
        return ""
    try:
        return json.loads(sse_data[5:].strip()).get("text", "")
    except json.JSONDecodeError:
        return ""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
