from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.vision.screen_analyzer import screen_analyzer

router = APIRouter(prefix="/api/vision", tags=["Vision"])

class VisionAnalyzeRequest(BaseModel):
    question: Optional[str] = "What is currently displayed on my screen?"

@router.post("/analyze")
def analyze_screen_endpoint(request: VisionAnalyzeRequest):
    """Captures screenshot and analyzes screen content."""
    return screen_analyzer.analyze_screen(user_question=request.question)
