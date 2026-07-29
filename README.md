# VoxLens — AI Meeting & Video Assistant

VoxLens is a production-grade, local-first AI assistant that ingests YouTube links or local audio/video files, transcribes them using AI, generates structured meeting intelligence, and supports retrieval-based chat (RAG) over the full content.

---

## 🎙️ Demo Architecture (How It Works)

During this presentation, you are seeing a highly customized, resilient architecture designed to bypass cloud hardware limits and anti-bot protections.

### 1. The Frontend (Vercel)
The beautiful, responsive UI you are looking at is built with **React 19 + TypeScript** and is hosted live on the internet via **Vercel**. It uses a custom dark-mode design system to provide a premium user experience.

### 2. The Secure Tunnel (Cloudflare)
Because free cloud servers like Render only provide 512MB of RAM (which is not enough to load heavy AI models), and because YouTube actively blocks cloud IP addresses from downloading videos, we implemented a brilliant workaround: **A Secure Local Tunnel**.
When the Vercel frontend makes an API request, it travels through an encrypted **Cloudflare Tunnel** directly to the presenter's laptop. 

### 3. The Backend (Local Machine)
The heavy lifting happens entirely locally on the presenter's laptop, which acts as a powerhouse server:
- **FastAPI (Python):** Handles the incoming requests asynchronously using native `BackgroundTasks`, eliminating the need for complex message brokers like Redis or Celery.
- **Media Ingestion:** Uses `yt-dlp` and `FFmpeg` to download and extract audio. Because this happens on a home Wi-Fi network (residential IP), YouTube's bot-detection algorithms allow it to pass seamlessly.
- **AI Transcription:** The audio is chopped into chunks and fed into a local instance of `faster-whisper`.
- **Summarization:** The transcribed text is sent to **DeepSeek** (a state-of-the-art reasoning model) to generate intelligent summaries, extract action items, and find decisions.

### 4. Chat & RAG (Retrieval-Augmented Generation)
When a user asks a question in the chat:
1. The backend uses HuggingFace `sentence-transformers` to mathematically embed the user's question locally.
2. It searches **ChromaDB** (a local Vector Database) to find the exact moments in the video transcript that match the question.
3. It sends only those specific transcript quotes to the DeepSeek AI, guaranteeing a mathematically grounded answer with zero hallucinations.

---

## 🚀 Running the App

To run this architecture yourself, follow these steps:

### 1. Start the Local Backend
The backend requires Python 3.12+ and FFmpeg installed on your system.
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Start the Secure Tunnel
In a new terminal, launch the Cloudflare tunnel to expose your local port 8000 to the internet safely.
```powershell
cd backend
.\cloudflared.exe tunnel --url http://localhost:8000
```
*Copy the `https://....trycloudflare.com` URL that appears in the terminal.*

### 3. Connect the Frontend
Go to your Vercel Dashboard -> VoxLens Settings -> Environment Variables.
Set `VITE_API_URL` to your Cloudflare URL, with `/api` appended at the end:
`https://your-cloudflare-link.trycloudflare.com/api`

Redeploy your Vercel app, and you are live!

---

## 💰 Cost and Privacy
VoxLens is designed to be highly cost-efficient and privacy-friendly:
- **Zero API Costs for Heavy Lifting:** Audio processing, transcription, and vector embeddings run entirely locally on your CPU/GPU.
- **Affordable Intelligence:** DeepSeek is extremely inexpensive compared to competitors, while offering top-tier reasoning capabilities. 
- **Resilient:** By running the backend locally, you are immune to strict cloud API limits and third-party bot blocks.
