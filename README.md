# ✦ StyleSense AI

> Your AI-powered personal fashion stylist — built with FastAPI + Google Gemini + Imagen 3

---

## 🚀 Quick Start

### 1. Get Your Gemini API Key
Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free API key.

### 2. Setup & Run
```bash
# Clone / unzip the project
cd stylesense-ai

# Create your .env file
cp .env.example .env

# Edit .env and paste your key:
# GEMINI_API_KEY=your_actual_key_here

# Install and run (all-in-one)
chmod +x start.sh && ./start.sh
```

Or manually:
```bash
pip install -r requirements.txt
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
│   └── gemini_service.py      # All Gemini API calls (isolated)
│
├── utils/
│   └── prompt_builder.py      # ⭐ Prompt Engineering Layer
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
      │ SELFIE_ANALYSIS_PROMPT → gemini-1.5-flash
      ▼
[Style Profile JSON] ─────────────────────────────┐
                                                   │
[Clothing Upload]                                  │
      │ CLOTHING_ANALYSIS_PROMPT → gemini-1.5-flash│
      ▼                                            │
[Wardrobe DB] ─────────────────────────────────────┤
                                                   │
[Select Vibe]                                      │
      │ build_outfit_prompt() → gemini-1.5-flash   │
      ▼                                            │
[Outfit JSON] ◄────────────────────────────────────┘
      │
      │ build_image_prompt() → imagen-3.0-generate-001
      ▼
[Virtual Try-On Image]
```

---

## ⭐ Prompt Engineering Layer

All AI prompts are in `utils/prompt_builder.py`:

| Prompt | Model | Purpose |
|--------|-------|---------|
| `SELFIE_ANALYSIS_PROMPT` | gemini-1.5-flash | Selfie → Style Profile JSON |
| `CLOTHING_ANALYSIS_PROMPT` | gemini-1.5-flash | Photo → Wardrobe Metadata JSON |
| `build_outfit_prompt()` | gemini-1.5-flash | Wardrobe + Vibe → Outfit JSON |
| `build_image_prompt()` | imagen-3.0-generate-001 | Outfit → Try-On Photo |

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
2. **Service Isolation** — All Gemini calls in `services/gemini_service.py`, never scattered across routes
3. **Multimodal Pipeline** — Vision (selfie + clothing) + LLM (outfit) + Image Gen (try-on)
4. **Robust JSON Parsing** — `_extract_json()` handles markdown fences and messy LLM output
5. **Async throughout** — FastAPI + async I/O for all file and AI operations
