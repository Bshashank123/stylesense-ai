import os
import json
import uuid
import base64
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, User, WardrobeItem, Outfit
from auth import get_current_user
from services.groq_service import generate_outfit, generate_outfit_image
from utils.prompt_builder import AVAILABLE_VIBES
import aiofiles

router = APIRouter(prefix="/api/outfit", tags=["outfit"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class GenerateFromVibeRequest(BaseModel):
    vibe: str
    selected_item_id: Optional[int] = None


class GenerateImageRequest(BaseModel):
    outfit_id: int


# ─── Helper: Get wardrobe as list ─────────────────────────────────────────────

def _get_wardrobe_list(user_id: int, db: Session) -> list:
    items = db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).all()
    wardrobe = []
    for item in items:
        meta = json.loads(item.metadata_json) if item.metadata_json else {}
        wardrobe.append({"id": item.id, **meta})
    return wardrobe


# ─── Endpoint: Get available vibes ────────────────────────────────────────────

@router.get("/vibes")
async def get_vibes():
    return {"vibes": AVAILABLE_VIBES}


# ─── Endpoint: Generate outfit from vibe ─────────────────────────────────────

@router.post("/generate-from-vibe")
async def generate_outfit_from_vibe(
    payload: GenerateFromVibeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check user has style profile
    if not current_user.style_profile_json:
        raise HTTPException(
            status_code=400,
            detail="Please upload a selfie first to create your style profile"
        )

    profile = json.loads(current_user.style_profile_json)
    wardrobe = _get_wardrobe_list(current_user.id, db)

    if len(wardrobe) < 3:
        raise HTTPException(
            status_code=400,
            detail="Please add at least 3 clothing items to your wardrobe before generating an outfit"
        )

    # Validate vibe
    valid_vibes = [v["id"] for v in AVAILABLE_VIBES]
    if payload.vibe not in valid_vibes:
        raise HTTPException(status_code=400, detail=f"Invalid vibe. Choose from: {valid_vibes}")

    # Get selected item if provided
    selected_item = None
    if payload.selected_item_id:
        item = db.query(WardrobeItem).filter(
            WardrobeItem.id == payload.selected_item_id,
            WardrobeItem.user_id == current_user.id
        ).first()
        if item:
            meta = json.loads(item.metadata_json) if item.metadata_json else {}
            selected_item = {"id": item.id, **meta}

    # Generate outfit with Gemini
    try:
        outfit_data = await generate_outfit(profile, wardrobe, payload.vibe, selected_item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outfit generation failed: {str(e)}")

    # Save to DB
    outfit_record = Outfit(
        user_id=current_user.id,
        vibe=payload.vibe,
        outfit_json=json.dumps(outfit_data)
    )
    db.add(outfit_record)
    db.commit()
    db.refresh(outfit_record)

    return {
        "message": "Outfit generated successfully",
        "outfit_id": outfit_record.id,
        "outfit": outfit_data,
        "vibe": payload.vibe
    }


# ─── Endpoint: Generate try-on image ─────────────────────────────────────────

@router.post("/generate-image")
async def generate_try_on_image(
    payload: GenerateImageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch outfit record
    outfit_record = db.query(Outfit).filter(
        Outfit.id == payload.outfit_id,
        Outfit.user_id == current_user.id
    ).first()

    if not outfit_record:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit_data = json.loads(outfit_record.outfit_json)
    profile = json.loads(current_user.style_profile_json) if current_user.style_profile_json else {}

    # Generate image with Imagen 3
    try:
        image_b64 = await generate_outfit_image(
            outfit=outfit_data,
            vibe=outfit_record.vibe,
            profile=profile,
            selfie_path=current_user.selfie_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

    # Save image to disk
    filename = f"tryon_{current_user.id}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)

    image_bytes = base64.b64decode(image_b64)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(image_bytes)

    # Update outfit record with image path
    outfit_record.generated_image = filepath
    db.commit()

    return {
        "message": "Try-on image generated successfully",
        "image_url": f"/{filepath}",
        "image_b64": image_b64
    }


# ─── Endpoint: Outfit history ─────────────────────────────────────────────────

@router.get("/history")
async def get_outfit_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    outfits = db.query(Outfit).filter(
        Outfit.user_id == current_user.id
    ).order_by(Outfit.created_at.desc()).limit(20).all()

    history = []
    for o in outfits:
        outfit_data = json.loads(o.outfit_json) if o.outfit_json else {}
        history.append({
            "id": o.id,
            "vibe": o.vibe,
            "outfit": outfit_data,
            "image_url": f"/{o.generated_image}" if o.generated_image else None,
            "created_at": o.created_at.isoformat()
        })

    return {"history": history}


# ─── Endpoint: Get single outfit ──────────────────────────────────────────────

@router.get("/{outfit_id}")
async def get_outfit(
    outfit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    return {
        "id": outfit.id,
        "vibe": outfit.vibe,
        "outfit": json.loads(outfit.outfit_json) if outfit.outfit_json else {},
        "image_url": f"/{outfit.generated_image}" if outfit.generated_image else None,
        "created_at": outfit.created_at.isoformat()
    }
