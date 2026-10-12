import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.database import init_db
from backend.api import chat, voice, tools, memory, agent, system
import backend.tools

# Configure Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("JARVIS.Main")

# Create FastAPI App
app = FastAPI(
    title="FRIDAY AI Assistant API",
    description="Autonomous Desktop AI Assistant Backend",
    version="5.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(tools.router)
app.include_router(memory.router)
app.include_router(agent.router)
app.include_router(system.router)
from backend.api import vision
app.include_router(vision.router)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing FRIDAY database tables...")
    init_db()
    voice.set_voice_broadcaster(manager.broadcast_voice_state)
    logger.info("FRIDAY backend initialized and ready.")


@app.on_event("shutdown")
def on_shutdown():
    """Clean up audio resources on server shutdown."""
    try:
        from backend.voice.text_to_speech import tts_engine
        tts_engine.stop()
    except Exception:
        pass
    try:
        from backend.voice.microphone import get_microphone
        get_microphone().stop()
    except Exception:
        pass
    logger.info("FRIDAY audio resources released.")


@app.get("/")
def root():
    return {
        "app": settings.JARVIS_NAME,
        "version": "5.0.0",
        "status": "ONLINE",
        "message": "FRIDAY operational. Systems nominal.",
    }


# ─── WebSocket Manager ───────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)

    async def broadcast_voice_state(self, state: str, detail: str = ""):
        """Broadcast a voice state change event to all connected WebSocket clients."""
        payload = {"type": "voice_state", "state": state}
        if detail:
            payload["detail"] = detail
        await self.broadcast(payload)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast({"type": "STATUS_UPDATE", "payload": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
