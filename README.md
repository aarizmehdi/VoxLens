# VoxLens — AI Meeting & Video Assistant

VoxLens is a production-grade, local-first AI assistant that ingests YouTube links or audio/video files, transcribes them, generates structured meeting intelligence, and supports retrieval-based chat over the full content.

## Features

- **Media Ingestion**: Accept YouTube URLs or local audio/video file uploads.
- **Fast, Local-First Transcription**: Powered by `faster-whisper` for English, with `sarvamai` available for Hindi/Hinglish optimization.
- **Smart Summaries & Extraction**: Automatically generates concise summaries, action items (with owners and deadlines), decisions, and open questions using the DeepSeek API.
- **RAG Chat**: Ask questions about the meeting. The assistant finds relevant chunks from the transcript and provides grounded answers with citations.
- **Premium UI**: A polished, responsive React frontend built with a custom dark-mode design system.

## Architecture

VoxLens uses an asynchronous processing architecture to keep the UI snappy while handling heavy media workloads:

- **Frontend**: React 19 + Vite + TypeScript. Connects to the backend via REST API.
- **Backend**: FastAPI (Python 3.12). Handles API requests and RAG queries.
- **Worker**: Celery + Redis. Manages the heavy background pipeline (download → extract → transcribe → summarize → embed).
- **Storage**: SQLite for metadata, ChromaDB for embeddings, and local filesystem for audio chunks.
- **LLM/Embeddings**: DeepSeek via OpenAI compatible API, Hugging Face `sentence-transformers` for local embeddings.

## Prerequisites

- Docker and Docker Compose (recommended for easy setup)
- OR Python 3.12, Node.js 20, Redis, and FFmpeg (for bare-metal setup)
- A DeepSeek API key

## Quick Start (Docker)

1. **Clone the repository**
2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your `DEEPSEEK_API_KEY`. (Optional: add `SARVAM_API_KEY` for Hindi transcription).

3. **Start the stack**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - Frontend UI: http://localhost (or http://localhost:5173 if running bare-metal dev server)
   - Backend API Docs: http://localhost:8000/docs

## Local Development (Bare-Metal)

If you prefer to run services individually:

**1. Infrastructure**
Make sure Redis is running (`redis-server`).
Make sure FFmpeg is installed (`apt install ffmpeg` or `brew install ffmpeg`).

**2. Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start API
uvicorn app.main:app --reload --port 8000

# Start Celery Worker (in a new terminal)
celery -A app.workers.celery_app worker --loglevel=info
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev
```

## How It Works

1. **Upload**: User submits a URL or file. The FastAPI backend creates a pending `Meeting` record and dispatches a Celery task.
2. **Processing**: The worker downloads media (using `yt-dlp`), extracts 16kHz mono audio (using `ffmpeg`), and chunks it.
3. **Transcription**: Audio chunks are fed to `faster-whisper`.
4. **Analysis**: The full transcript is sent to DeepSeek to generate a structured JSON report (Summary, Actions, Decisions).
5. **Embedding**: The transcript is chunked and embedded into ChromaDB locally.
6. **Chat**: When a user chats, their query is embedded, relevant chunks are retrieved from Chroma, and DeepSeek answers using only that context.

## Cost and Privacy

VoxLens is designed to be highly cost-efficient and privacy-friendly:
- Transcription and Embeddings run entirely locally, incurring zero API costs and keeping raw speech data on your machine.
- LLM tasks use DeepSeek, which is extremely affordable.
- No cloud databases or expensive PaaS subscriptions required.

## Roadmap

- Speaker Diarization support
- Advanced language routing
- Real-time transcription mode
