# VoxLens — AI Meeting Intelligence Platform

VoxLens is a production-grade, enterprise meeting intelligence platform. It ingests meeting audio/video recordings, transcribes them using the Groq AI supercomputer, generates structured meeting intelligence, and supports retrieval-based chat (RAG) over the full content.

---

## 🎙️ Cloud Architecture (How It Works)

During this presentation, you are seeing a highly customized, resilient cloud architecture designed for scale and enterprise reliability.

### 1. The Frontend (Vercel)
The beautiful, responsive UI you are looking at is built with **React 19 + TypeScript** and is hosted globally via **Vercel**. It uses a custom dark-mode design system with stunning micro-animations to provide a premium user experience. It features a robust File Upload component for ingesting raw meeting recordings.

### 2. The Backend (Render)
The heavy lifting happens entirely in the cloud on **Render**:
- **FastAPI (Python):** Handles incoming requests asynchronously using native `BackgroundTasks`, eliminating the need for complex, memory-heavy message brokers like Redis or Celery.
- **Media Processing:** Uses `FFmpeg` to securely extract and normalize audio from user-uploaded video and audio files.
- **AI Transcription:** Transmits the extracted audio to **Groq**, an LPU supercomputer that transcribes long meetings in a matter of seconds.
- **Summarization:** The transcribed text is sent to **DeepSeek** (a state-of-the-art reasoning model) to generate intelligent summaries, extract action items, and find decisions.

### 3. Chat & RAG (Retrieval-Augmented Generation)
When a user asks a question in the chat:
1. The backend mathematically embeds the user's question locally.
2. It searches **ChromaDB** (a Vector Database) to find the exact moments in the video transcript that match the question.
3. It sends only those specific transcript quotes to the DeepSeek AI, guaranteeing a mathematically grounded answer with zero hallucinations.

---

## 🚀 Running the App

To run this architecture locally, follow these steps:

### 1. Start the Local Backend
The backend requires Python 3.12+ and FFmpeg installed on your system.
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Connect the Frontend
In a separate terminal, start the Vite development server:
```powershell
cd frontend
npm run dev
```
*(By default, the Vite proxy will automatically route `/api` requests to your local backend on port `8000`.)*

---

## 💰 Cost and Privacy
VoxLens is designed to be highly cost-efficient and scalable:
- **Groq LPU Processing:** Offers blazingly fast transcription APIs at a fraction of the cost of traditional GPU providers.
- **Affordable Intelligence:** DeepSeek is extremely inexpensive compared to competitors, while offering top-tier reasoning capabilities. 
- **Lightweight Cloud Footprint:** By removing heavy local AI models (like Whisper) and Celery workers, the entire backend runs comfortably on a single free-tier Render instance.
