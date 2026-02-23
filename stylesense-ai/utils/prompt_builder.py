"""
StyleSense AI — Prompt Engineering Layer
All Gemini prompts live here. Centralised, versioned, deterministic.
"""

import json


# ─── Prompt 1: Selfie → Style Profile ─────────────────────────────────────────

SELFIE_ANALYSIS_PROMPT = """
You are a professional fashion stylist AI with expertise in body analysis and personal styling.

Analyze the person in the provided image carefully and return ONLY a valid JSON object.

Extract the following attributes:
- gender_presentation: one of [male, female, androgynous]
- body_type: one of [lean, average, athletic, curvy, plus-size]
- skin_tone: one of [fair, medium, olive, dark]
- hair_color: descriptive color (e.g. black, brown, blonde, red, grey)
- hair_length: one of [short, medium, long, bald]
- overall_style_vibe: one of [casual, formal, sporty, streetwear, minimalist, mixed]
- estimated_height: one of [petite, average, tall]

Return ONLY this JSON structure with no additional text, markdown, or explanation:
{
  "gender_presentation": "",
  "body_type": "",
  "skin_tone": "",
  "hair_color": "",
  "hair_length": "",
  "overall_style_vibe": "",
  "estimated_height": ""
}
"""


# ─── Prompt 2: Clothing Photo → Wardrobe Metadata ─────────────────────────────

CLOTHING_ANALYSIS_PROMPT = """
You are a professional fashion catalog AI with expertise in garment classification.

Analyze the clothing item in the provided image and return ONLY a valid JSON object.

Identify these attributes precisely:
- item_type: one of [shirt, tshirt, polo, blouse, top, jeans, trousers, shorts, skirt, dress, jacket, hoodie, sweater, blazer, coat, shoes, sneakers, boots, sandals, heels, accessory, other]
- primary_color: main dominant color (e.g. navy blue, white, black, forest green)
- secondary_color: secondary color if present, otherwise "none"
- style: one of [casual, formal, sporty, streetwear, minimalist, bohemian, preppy, vintage]
- pattern: one of [solid, striped, checked, printed, floral, denim, geometric, animal-print, abstract, none]
- season_suitability: one of [summer, winter, all-season, spring-fall]
- occasion: one of [everyday, work, party, gym, outdoor, formal-event, beach]

Return ONLY this JSON structure with no additional text, markdown, or explanation:
{
  "item_type": "",
  "primary_color": "",
  "secondary_color": "",
  "style": "",
  "pattern": "",
  "season_suitability": "",
  "occasion": ""
}
"""


# ─── Prompt 3: Outfit Generation ──────────────────────────────────────────────

def build_outfit_prompt(profile: dict, wardrobe: list, vibe: str, selected_item: dict = None) -> str:
    """
    Build a personalized outfit generation prompt.
    Uses user profile + wardrobe list + vibe to produce a complete outfit JSON.
    """

    profile_str = json.dumps(profile, indent=2)
    wardrobe_str = json.dumps(wardrobe, indent=2)

    prompt = f"""
You are an expert AI fashion stylist with 15 years of experience in personal styling and color theory.

Your task is to create a complete, harmonious outfit using ONLY items from the provided wardrobe.

═══════════════════════════════
OCCASION VIBE: {vibe.upper()}
═══════════════════════════════

USER STYLE PROFILE:
{profile_str}

AVAILABLE WARDROBE ITEMS (use ONLY these):
{wardrobe_str}

═══════════════════════════════
OUTFIT CREATION RULES:
═══════════════════════════════
1. ONLY use items from the wardrobe list above — never suggest items not in the list
2. Select exactly 1 top item (shirt/tshirt/blouse/top/sweater/hoodie)
3. Select exactly 1 bottom item (jeans/trousers/shorts/skirt/dress)
4. Select exactly 1 footwear item (shoes/sneakers/boots/sandals/heels)
5. Optionally select 1 layering/outerwear item if available and appropriate
6. Ensure color harmony between all selected items
7. Match the selection to the user's body type for the best fit and look
8. The overall outfit MUST match the vibe: {vibe}
9. Reference items by their wardrobe ID numbers
"""

    if selected_item:
        prompt += f"""
═══════════════════════════════
MANDATORY ITEM (MUST INCLUDE):
═══════════════════════════════
This item MUST be part of the outfit:
{json.dumps(selected_item, indent=2)}

Build the rest of the outfit around this item.
"""

    prompt += """
═══════════════════════════════
RETURN ONLY THIS JSON — NO EXTRA TEXT:
═══════════════════════════════
{
  "top": "item description with color and style",
  "bottom": "item description with color and style",
  "footwear": "item description with color and style",
  "layering_item": "item description or null if none",
  "top_id": wardrobe_item_id_or_null,
  "bottom_id": wardrobe_item_id_or_null,
  "footwear_id": wardrobe_item_id_or_null,
  "layering_id": wardrobe_item_id_or_null,
  "explanation": "2-3 sentence explanation of why this outfit works for the vibe and the person",
  "style_tips": "2-3 actionable styling tips to elevate the look",
  "color_palette": "brief description of the color story"
}
"""
    return prompt


# ─── Prompt 4: Virtual Try-On Image Generation ────────────────────────────────

def build_image_prompt(outfit: dict, vibe: str, profile: dict) -> str:
    """
    Build a photorealistic fashion image generation prompt.
    Creates a virtual try-on illusion based on outfit + user profile.
    """

    layering = outfit.get("layering_item") or "no outerwear"
    gender = profile.get("gender_presentation", "person")
    body_type = profile.get("body_type", "average build")
    hair = f"{profile.get('hair_length', 'medium')} {profile.get('hair_color', 'dark')} hair"
    skin = profile.get("skin_tone", "medium") + " skin tone"

    return f"""
Photorealistic full-body fashion editorial photograph of a {gender} model.

Physical appearance:
- {body_type} body type
- {hair}
- {skin}

Complete outfit being worn:
- Top: {outfit.get('top', 'casual top')}
- Bottom: {outfit.get('bottom', 'classic trousers')}
- Shoes: {outfit.get('footwear', 'clean sneakers')}
- Outer layer: {layering}

Styling direction: {vibe} aesthetic

Photography specs:
- Studio fashion photography
- Soft diffused lighting with subtle rim light
- Clean minimal white/light grey background
- Full body shot showing complete outfit
- Sharp focus on clothing details
- Professional fashion magazine quality
- Ultra realistic, 8K resolution
- No text or watermarks
"""


# ─── Vibe Definitions ─────────────────────────────────────────────────────────

AVAILABLE_VIBES = [
    {"id": "casual-cool", "label": "Casual Cool", "emoji": "😎", "desc": "Effortless everyday style"},
    {"id": "office-ready", "label": "Office Ready", "emoji": "💼", "desc": "Professional and polished"},
    {"id": "date-night", "label": "Date Night", "emoji": "🌙", "desc": "Romantic and sophisticated"},
    {"id": "street-style", "label": "Street Style", "emoji": "🏙️", "desc": "Urban and edgy"},
    {"id": "weekend-vibes", "label": "Weekend Vibes", "emoji": "☀️", "desc": "Relaxed and comfortable"},
    {"id": "gym-fit", "label": "Gym Fit", "emoji": "💪", "desc": "Sporty and functional"},
    {"id": "brunch-ready", "label": "Brunch Ready", "emoji": "🥐", "desc": "Chic and social"},
    {"id": "travel-mode", "label": "Travel Mode", "emoji": "✈️", "desc": "Comfortable yet stylish"},
    {"id": "party-time", "label": "Party Time", "emoji": "🎉", "desc": "Bold and statement-making"},
    {"id": "minimalist", "label": "Minimalist", "emoji": "⬜", "desc": "Clean and understated"},
]
