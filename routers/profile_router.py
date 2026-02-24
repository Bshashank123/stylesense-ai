import os
import json
import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db, User
from auth import get_current_user
from services.groq_service import analyze_selfie
import aiofiles

router = APIRouter(prefix="/api/profile", tags=["profile"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload-selfie")
async def upload_selfie(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")

    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # Save file with unique name
    ext = os.path.splitext(file.filename)[-1].lower() or ".jpg"
    filename = f"selfie_{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    # Analyze with Gemini
    try:
        profile = await analyze_selfie(filepath)
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # Store in DB
    current_user.style_profile_json = json.dumps(profile)
    current_user.selfie_path = filepath
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Selfie analyzed successfully",
        "profile": profile,
        "selfie_url": f"/{filepath}"
    }


@router.get("/me")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    profile = None
    if current_user.style_profile_json:
        profile = json.loads(current_user.style_profile_json)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "profile": profile,
        "selfie_url": f"/{current_user.selfie_path}" if current_user.selfie_path else None,
        "has_profile": profile is not None
    }
