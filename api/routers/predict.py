import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException
from database import save_prediction, get_history
import os

router = APIRouter(prefix="/analyze", tags=["analyze"])
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml-service:8001")

@router.post("/")
async def analyze(file: UploadFile = File(...)):
    image_bytes = await file.read()
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{ML_SERVICE_URL}/predict",
            files={"file": (file.filename, image_bytes, file.content_type)}
        )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="ML service error")
    result = response.json()
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message"))
    save_prediction(result["character"], result["confidence"])
    return result

@router.get("/history")
async def history(limit: int = 10):
    return get_history(limit)