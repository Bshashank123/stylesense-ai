# ✦ StyleSense AI

> Your AI-powered personal fashion stylist — built with FastAPI + Groq + Hugging Face

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Database** | SQLite via SQLAlchemy |
| **Authentication** | JWT (python-jose) + bcrypt |
| **LLM — Vision & Text** | Groq API (free tier) |
| **Image Generation** | Hugging Face Inference API (free tier) |
| **Frontend** | Vanilla HTML/CSS/JS |

---

## 🤖 LLMs & Models Used

### 1. `meta-llama/llama-4-scout-17b-16e-instruct` — Vision Model
Used for analyzing selfie photos and clothing images.

| Parameter | Value |
|-----------|-------|
| Provider | Groq |
| Modality | Vision + Text (multimodal) |
| Parameters | 17 Billion |
| Context Window | 131,072 tokens |
| Temperature | `0.3` (selfie analysis), `0.2` (clothing analysis) |
| Max Output Tokens | `1024` |
| Input Format | Base64 image + text prompt |

---

### 2. `llama-3.3-70b-versatile` — Text Model
Used for generating outfit recommendations from wardrobe data.

| Parameter | Value |
|-----------|-------|
| Provider | Groq |
| Modality | Text only |
| Parameters | 70 Billion |
| Context Window | 128,000 tokens |
| Temperature | `0.7` |
| Max Output Tokens | `1024` |
| Input Format | Structured text prompt |

---

### 3. `black-forest-labs/FLUX.1-schnell` — Image Generation Model
Used for generating virtual try-on outfit images.

| Parameter | Value |
|-----------|-------|
| Provider | Hugging Face Inference API |
| Model Type | Text-to-Image Diffusion (FLUX) |
| Output Resolution | 512 × 768 px (portrait) |
| Inference Steps | `4` (schnell = optimised for 1–4 steps) |
| Input Format | Single-line text prompt |

---

## 🚀 Quick Start

### 1. Get Your Free API Keys

**Groq** (for LLM — vision + text):
- Go to [console.groq.com](https://console.groq.com)
- Sign up (no credit card needed)
- Create an API key

**Hugging Face** (for image generation):
- Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Create a **Read** token (no credit card needed)

### 2. Setup & Run

```bash
cd stylesense-ai
cp .env.example .env

# Edit .env and paste your keys:
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
# HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

pip install -r requirements.txt
chmod +x start.sh && ./start.sh
```

Or manually:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open the App
Visit **http://localhost:8000** and create your account.

---

## 📁 Project Structure

```
stylesense-ai/
│
├── main.py                    # FastAPI app entry point
├── database.py                # SQLAlchemy models + DB setup
├── auth.py                    # JWT authentication utilities
├── requirements.txt
├── start.sh                   # One-command startup script
├── .env.example               # Environment variable template
│
├── routers/
│   ├── auth_router.py         # POST /api/auth/signup, /login
│   ├── profile_router.py      # POST /api/profile/upload-selfie
│   ├── wardrobe_router.py     # CRUD /api/wardrobe/
│   └── outfit_router.py       # POST /api/outfit/generate-from-vibe
│
├── services/
│   └── groq_service.py        # All AI API calls (Groq + HF)
│
├── utils/
│   └── prompt_builder.py      # Prompt Engineering Layer
│
├── static/uploads/            # User-uploaded images (auto-created)
│
└── frontend/
    ├── index.html             # Login / Signup
    ├── dashboard.html         # Home dashboard
    ├── wardrobe.html          # Wardrobe manager
    ├── generate.html          # Outfit generator
    └── result.html            # Outfit result + history
```

---

## 🧠 AI Pipeline

```
[Selfie Upload]
      │ SELFIE_ANALYSIS_PROMPT → llama-4-scout-17b (vision)
      ▼
[Style Profile JSON] ──────────────────────────────────┐
                                                       │
[Clothing Upload]                                      │
      │ CLOTHING_ANALYSIS_PROMPT → llama-4-scout-17b  │
      ▼                                               │
[Wardrobe DB] ─────────────────────────────────────────┤
                                                       │
[Select Vibe]                                          │
      │ build_outfit_prompt() → llama-3.3-70b          │
      ▼                                               │
[Outfit JSON] ◄────────────────────────────────────────┘
      │
      │ build_image_prompt() → FLUX.1-schnell (HF)
      ▼
[Virtual Try-On Image]
```

---

## ⭐ Prompt Engineering Layer

All AI prompts live in `utils/prompt_builder.py`:

| Prompt | Model | Purpose |
|--------|-------|---------|
| `SELFIE_ANALYSIS_PROMPT` | llama-4-scout-17b | Selfie → Style Profile JSON |
| `CLOTHING_ANALYSIS_PROMPT` | llama-4-scout-17b | Photo → Wardrobe Metadata JSON |
| `build_outfit_prompt()` | llama-3.3-70b | Wardrobe + Vibe → Outfit JSON |
| `build_image_prompt()` | FLUX.1-schnell | Outfit → Virtual Try-On Photo |

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/signup` | — | Create account |
| POST | `/api/auth/login` | — | Login + get JWT |
| POST | `/api/profile/upload-selfie` | ✓ | Upload selfie → AI analysis |
| GET | `/api/profile/me` | ✓ | Get style profile |
| POST | `/api/wardrobe/add` | ✓ | Add clothing item → AI tag |
| GET | `/api/wardrobe/` | ✓ | List wardrobe items |
| DELETE | `/api/wardrobe/{id}` | ✓ | Remove item |
| GET | `/api/outfit/vibes` | ✓ | List available vibes |
| POST | `/api/outfit/generate-from-vibe` | ✓ | Generate outfit |
| POST | `/api/outfit/generate-image` | ✓ | Generate try-on image |
| GET | `/api/outfit/history` | ✓ | Outfit history |
| GET | `/api/outfit/{id}` | ✓ | Single outfit |

Interactive docs: **http://localhost:8000/docs**

---

## 🗄️ Database

SQLite (auto-created as `stylesense.db`):

| Table | Key Fields |
|-------|-----------|
| `users` | id, email, password_hash, style_profile_json, selfie_path |
| `wardrobe` | id, user_id, image_path, metadata_json |
| `outfits` | id, user_id, vibe, outfit_json, generated_image |

---

## 🎨 Available Vibes

| Vibe | Occasion |
|------|---------|
| 😎 Casual Cool | Effortless everyday style |
| 💼 Office Ready | Professional and polished |
| 🌙 Date Night | Romantic and sophisticated |
| 🏙️ Street Style | Urban and edgy |
| ☀️ Weekend Vibes | Relaxed and comfortable |
| 💪 Gym Fit | Sporty and functional |
| 🥐 Brunch Ready | Chic and social |
| ✈️ Travel Mode | Comfortable yet stylish |
| 🎉 Party Time | Bold and statement-making |
| ⬜ Minimalist | Clean and understated |

---

## 🔐 Security

- Passwords hashed with **bcrypt**
- All protected routes require **JWT Bearer token**
- Tokens expire after **7 days**
- Each user's wardrobe is private and isolated

---

## 🏆 Architecture Highlights

1. **Prompt Engineering Layer** — All prompts centralised in `utils/prompt_builder.py` with schema enforcement, role-priming, and JSON-only outputs
2. **Service Isolation** — All AI calls in `services/groq_service.py`, never scattered across routes
3. **Multimodal Pipeline** — Vision (selfie + clothing) + LLM (outfit) + Image Gen (try-on)
4. **Robust JSON Parsing** — `_extract_json()` handles markdown fences and messy LLM output
5. **Async throughout** — FastAPI + async I/O for all file and AI operations
6. **100% Free APIs** — No credit card required for any service
