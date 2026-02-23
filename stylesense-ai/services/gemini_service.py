"""
StyleSense AI — Gemini Service
All Google Gemini API interactions are isolated in this module.
Uses: gemini-1.5-flash for vision/text, imagen-3.0-generate-001 for images.
"""

import os
import json
import base64
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

from utils.prompt_builder import (
    SELFIE_ANALYSIS_PROMPT,
    CLOTHING_ANALYSIS_PROMPT,
    build_outfit_prompt,
    build_image_prompt,
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ─── Initialise Gemini Client ──────────────────────────────────────────────────
_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env file")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


# ─── Helper: Parse JSON from Gemini response ──────────────────────────────────

def _extract_json(text: str) -> dict:
    """
    Robustly extract JSON from Gemini text response.
    Handles markdown code blocks, extra whitespace, etc.
    """
    # Strip markdown code blocks if present
    text = text.strip()
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object within text
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from Gemini response: {text[:200]}")


def _read_image_bytes(image_path: str):
    """Read image file and return (bytes, mime_type)."""
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
        return f.read(), mime_type


# ─── Service 1: Analyze Selfie ────────────────────────────────────────────────

async def analyze_selfie(image_path: str) -> dict:
    """
    Analyze a selfie image and extract the user's style profile.
    Returns a structured JSON dict.
    """
    client = get_client()
    image_bytes, mime_type = _read_image_bytes(image_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        inline_data=types.Blob(mime_type=mime_type, data=image_bytes)
                    ),
                    types.Part(text=SELFIE_ANALYSIS_PROMPT),
                ]
            )
        ]
    )

    return _extract_json(response.text)


# ─── Service 2: Analyze Clothing Item ────────────────────────────────────────

async def analyze_clothing(image_path: str) -> dict:
    """
    Analyze a clothing photo and extract wardrobe item metadata.
    Returns a structured JSON dict.
    """
    client = get_client()
    image_bytes, mime_type = _read_image_bytes(image_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        inline_data=types.Blob(mime_type=mime_type, data=image_bytes)
                    ),
                    types.Part(text=CLOTHING_ANALYSIS_PROMPT),
                ]
            )
        ]
    )

    return _extract_json(response.text)


# ─── Service 3: Generate Outfit ───────────────────────────────────────────────

async def generate_outfit(
    profile: dict,
    wardrobe: list,
    vibe: str,
    selected_item: dict = None
) -> dict:
    """
    Generate a complete outfit recommendation from the user's wardrobe.
    Returns outfit JSON with top, bottom, footwear, explanation, tips.
    """
    client = get_client()
    prompt = build_outfit_prompt(profile, wardrobe, vibe, selected_item)

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1024,
        )
    )

    return _extract_json(response.text)


# ─── Service 4: Generate Try-On Image (Imagen 3) ──────────────────────────────

async def generate_outfit_image(
    outfit: dict,
    vibe: str,
    profile: dict,
    selfie_path: str = None
) -> str:
    """
    Generate a photorealistic virtual try-on image using Imagen 3.
    Returns base64-encoded PNG image string.
    """
    client = get_client()
    prompt = build_image_prompt(outfit, vibe, profile)

    response = client.models.generate_images(
        model="imagen-3.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="2:3",
            safety_filter_level="block_few",
            person_generation="allow_adult",
        )
    )

    generated_image = response.generated_images[0]
    image_bytes = generated_image.image.image_bytes
    return base64.b64encode(image_bytes).decode("utf-8")