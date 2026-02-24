import os
import json
import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db, User, WardrobeItem
from auth import get_current_user
from services.groq_service import analyze_clothing
import aiofiles

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/add")
async def add_wardrobe_item(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    ext = os.path.splitext(file.filename)[-1].lower() or ".jpg"
    filename = f"clothing_{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    # Analyze with Gemini
    try:
        metadata = await analyze_clothing(filepath)
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"AI clothing analysis failed: {str(e)}")

    # Store in DB
    item = WardrobeItem(
        user_id=current_user.id,
        image_path=filepath,
        metadata_json=json.dumps(metadata)
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": "Clothing item added successfully",
        "item": {
            "id": item.id,
            "image_url": f"/{filepath}",
            "metadata": metadata,
            "created_at": item.created_at.isoformat()
        }
    }


@router.get("/")
async def get_wardrobe(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id
    ).order_by(WardrobeItem.created_at.desc()).all()

    wardrobe = []
    for item in items:
        metadata = json.loads(item.metadata_json) if item.metadata_json else {}
        wardrobe.append({
            "id": item.id,
            "image_url": f"/{item.image_path}",
            "metadata": metadata,
            "created_at": item.created_at.isoformat()
        })

    return {"wardrobe": wardrobe, "total": len(wardrobe)}


@router.delete("/{item_id}")
async def delete_wardrobe_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Remove image file
    if os.path.exists(item.image_path):
        os.remove(item.image_path)

    db.delete(item)
    db.commit()

    return {"message": "Item removed from wardrobe"}
