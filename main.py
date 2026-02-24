"""
StyleSense AI — FastAPI Backend
Main application entry point.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from database import init_db
from routers import auth_router, profile_router, wardrobe_router, outfit_router

load_dotenv()

# ─── Create App ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="StyleSense AI",
    description="AI-powered personal fashion stylist",
    version="1.0.0"
)

# ─── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files ──────────────────────────────────────────────────────────────

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ─── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(wardrobe_router.router)
app.include_router(outfit_router.router)

# ─── Frontend Routes ───────────────────────────────────────────────────────────

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/wardrobe")
async def serve_wardrobe():
    return FileResponse("frontend/wardrobe.html")

@app.get("/generate")
async def serve_generate():
    return FileResponse("frontend/generate.html")

@app.get("/result")
async def serve_result():
    return FileResponse("frontend/result.html")

# ─── Health Check ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "StyleSense AI", "version": "1.0.0"}

# ─── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ StyleSense AI started")
    print("📦 Database initialised")
    print("🚀 Ready at http://localhost:8000")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
