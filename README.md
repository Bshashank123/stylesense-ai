StyleSense AI 👗

StyleSense AI is an AI-powered fashion assistant that helps users generate outfits, analyze clothing images, and get personalized styling suggestions using Generative AI.

Features

Generate outfit ideas based on occasion, weather, and budget

Analyze clothing from uploaded images

Get styling tips and fashion advice via chatbot

Personalized recommendations using AI

Tech Stack

Frontend: React / Next.js

Backend: FastAPI (Python)

AI Model: Google Gemini

Image Processing: Pillow / OpenCV

Database: MongoDB / PostgreSQL

Project Structure
stylesense-ai/
│
├── frontend/
├── backend/
│   ├── routes/
│   ├── services/
│   ├── prompts/
│   └── main.py
│
└── README.md
Getting Started
Clone the repo
git clone https://github.com/Bshashank123/stylesense-ai
cd stylesense-ai
Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Frontend setup
cd frontend
npm install
npm run dev
Environment Variables

Create a .env file in backend:

GEMINI_API_KEY=your_api_key
DATABASE_URL=your_db_url
Future Improvements

Virtual try-on

Closet digitization

Fashion trend prediction
