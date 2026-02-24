"""
StyleSense AI — Groq Service
Replaces Google Gemini with 100% free APIs:
  - Groq API  (text + vision)  → groq.com         (free tier, no card needed)
  - Hugging Face (image gen)   → huggingface.co   (free token, no card needed)
"""

import os
import json
import base64
import re
import httpx
from pathlib import Path
from dotenv import load_dotenv

from utils.prompt_builder import (
    SELFIE_ANALYSIS_PROMPT,
    CLOTHING_ANALYSIS_PROMPT,
    build_outfit_prompt,
    build_image_prompt,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Vision model — supports image input
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Text-only model — fast, generous free limits
TEXT_MODEL = "llama-3.3-70b-versatile"


# ─── Helper: Parse JSON from response ─────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """Robustly extract JSON from LLM text response."""
    text = text.strip()
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from response: {text[:200]}")


def _image_to_base64(image_path: str) -> tuple[str, str]:
    """Convert image file to base64 string and return (base64_str, mime_type)."""
    path = Path(image_path)
    suffix = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_map.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        image_bytes = f.read()

    return base64.b64encode(image_bytes).decode("utf-8"), mime_type


def _get_headers() -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in .env file — get your free key at console.groq.com")
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }


# ─── Service 1: Analyze Selfie ────────────────────────────────────────────────

async def analyze_selfie(image_path: str) -> dict:
    b64, mime_type = _image_to_base64(image_path)

    payload = {
        "model": VISION_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                {"type": "text", "text": SELFIE_ANALYSIS_PROMPT}
            ]
        }],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{GROQ_BASE_URL}/chat/completions", headers=_get_headers(), json=payload)
        r.raise_for_status()

    return _extract_json(r.json()["choices"][0]["message"]["content"])


# ─── Service 2: Analyze Clothing Item ────────────────────────────────────────

async def analyze_clothing(image_path: str) -> dict:
    b64, mime_type = _image_to_base64(image_path)

    payload = {
        "model": VISION_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                {"type": "text", "text": CLOTHING_ANALYSIS_PROMPT}
            ]
        }],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{GROQ_BASE_URL}/chat/completions", headers=_get_headers(), json=payload)
        r.raise_for_status()

    return _extract_json(r.json()["choices"][0]["message"]["content"])


# ─── Service 3: Generate Outfit ───────────────────────────────────────────────

async def generate_outfit(profile: dict, wardrobe: list, vibe: str, selected_item: dict = None) -> dict:
    prompt = build_outfit_prompt(profile, wardrobe, vibe, selected_item)

    payload = {
        "model": TEXT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{GROQ_BASE_URL}/chat/completions", headers=_get_headers(), json=payload)
        r.raise_for_status()

    return _extract_json(r.json()["choices"][0]["message"]["content"])


# ─── Service 4: Generate Outfit Image (Hugging Face — free) ──────────────────

async def generate_outfit_image(outfit: dict, vibe: str, profile: dict, selfie_path: str = None) -> str:
    """
    Generates image using Hugging Face Inference API (FLUX.1-schnell).
    Free — sign up at huggingface.co and create a token at /settings/tokens
    Add HF_TOKEN=hf_xxx to your .env file.
    """
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not set in .env — get your free token at huggingface.co/settings/tokens")

    prompt = build_image_prompt(outfit, vibe, profile)
    clean_prompt = " ".join(prompt.split())  # collapse newlines into single line

    payload = {
        "inputs": clean_prompt,
        "parameters": {
            "width": 512,
            "height": 768,
            "num_inference_steps": 4,
        }
    }

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
            headers=headers,
            json=payload,
        )
        r.raise_for_status()
        image_bytes = r.content

    return base64.b64encode(image_bytes).decode("utf-8")
