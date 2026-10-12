from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.config import settings
from backend.tools.system import get_system_stats

router = APIRouter(prefix="/api/system", tags=["System"])


class SettingsUpdateRequest(BaseModel):
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    enable_voice: Optional[bool] = None
    safe_mode: Optional[bool] = None
    voice_continuous: Optional[bool] = None
    voice_wakeword_only: Optional[bool] = None


@router.get("/stats")
def get_stats():
    """Retrieve live system diagnostics (CPU, RAM, Disk, Battery, Network)."""
    return get_system_stats()


@router.get("/config")
def get_config():
    """Get current JARVIS system settings (API keys masked)."""
    masked_key = ""
    if settings.OPENAI_API_KEY:
        masked_key = (
            settings.OPENAI_API_KEY[:7] + "..." + settings.OPENAI_API_KEY[-4:]
            if len(settings.OPENAI_API_KEY) > 12
            else "****"
        )

    return {
        "jarvis_name": settings.JARVIS_NAME,
        "openai_model": settings.OPENAI_MODEL,
        "openai_api_key_configured": bool(settings.OPENAI_API_KEY),
        "openai_api_key_masked": masked_key,
        "port": settings.JARVIS_PORT,
        "enable_voice": settings.ENABLE_VOICE,
        "enable_vision": settings.ENABLE_VISION,
        "safe_mode": settings.SAFE_MODE,
        "voice_continuous": settings.VOICE_CONTINUOUS,
        "voice_wakeword_only": settings.VOICE_WAKEWORD_ONLY,
    }


@router.post("/config")
def update_config(req: SettingsUpdateRequest):
    """Update runtime settings."""
    if req.openai_api_key is not None:
        settings.OPENAI_API_KEY = req.openai_api_key
        from backend.core.brain import brain_instance
        brain_instance.api_key = req.openai_api_key
        if req.openai_api_key.startswith("sk-"):
            from openai import OpenAI
            brain_instance.client = OpenAI(api_key=req.openai_api_key)

    if req.openai_model is not None:
        settings.OPENAI_MODEL = req.openai_model
        from backend.core.brain import brain_instance
        brain_instance.model = req.openai_model

    if req.enable_voice is not None:
        settings.ENABLE_VOICE = req.enable_voice
    if req.safe_mode is not None:
        settings.SAFE_MODE = req.safe_mode
    if req.voice_continuous is not None:
        settings.VOICE_CONTINUOUS = req.voice_continuous
    if req.voice_wakeword_only is not None:
        settings.VOICE_WAKEWORD_ONLY = req.voice_wakeword_only

    return {"status": "success", "message": "FRIDAY settings updated successfully."}
