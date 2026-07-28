# AI Meeting & Video Assistant — Product Requirements Document

## 1. Product Summary

### 1.1 Product Name
**AI Meeting & Video Assistant**

### 1.2 One-Line Description
A production-grade, cost-efficient, local-first AI assistant that ingests YouTube links or audio/video files, transcribes them, generates structured meeting intelligence, and supports retrieval-based chat over the full content.

### 1.3 Vision
Build a polished, portfolio-ready assistant that feels like a real product: fast UI, reliable processing, transparent outputs, and a clear architecture that can scale from a solo demo to a practical internal tool.

### 1.4 Core Value Proposition
Users can upload a recording or paste a YouTube URL and immediately get:
- accurate transcription,
- concise summary,
- action items with owners and deadlines,
- decisions,
- unresolved questions,
- and an interactive chat experience grounded in the meeting content.

---

## 2. Goals and Non-Goals

### 2.1 Goals
- Accept **YouTube URLs** and **local audio/video files**.
- Extract audio, normalize it, and transcribe it efficiently.
- Support **English** and **Hindi/Hinglish** with the best available cost-effective path.
- Generate meeting outputs that are structured, readable, and useful.
- Enable **RAG-based chat** over transcript chunks.
- Provide a **React-based frontend** suitable for a portfolio-grade product.
- Keep operating cost low by preferring open-source, local, and free-tier components where practical.
- Produce a dedicated **README.md** that explains setup, architecture, usage, and deployment clearly.

### 2.2 Non-Goals
- Real-time live meeting capture.
- Speaker diarization as a hard requirement in v1.
- Enterprise-grade auth, billing, or multi-tenant permissions in v1.
- Full collaboration workspace features such as shared folders, annotations, or team-level analytics.
- High-cost cloud-only architecture.

---

## 3. Target Users

### 3.1 Primary Users
- Portfolio reviewers
- Teachers and academic evaluators
- Recruiters and office evaluators
- Students and solo builders
- Small teams needing quick meeting intelligence

### 3.2 User Needs
- Fast, reliable transcription
- Clear summaries that do not feel generic
- Action items and decisions extracted in a structured format
- Searchable meeting knowledge
- A product that looks and behaves like production software

---

## 4. Product Principles

1. **Cost discipline first**  
   Prefer local inference, open-source models, and free tiers where quality remains acceptable.

2. **Accuracy over hype**  
   Avoid bloated AI features that do not improve user value.

3. **Structured output wins**  
   Summaries, action items, and decisions must be predictable and machine-readable.

4. **Fast experience, even if processing is asynchronous**  
   UI should stay responsive while media processing runs in the background.

5. **Local-first by default**  
   Keep sensitive media and transcripts as local as possible.

6. **Production feel**  
   Clean architecture, robust error states, progress indicators, and a polished UI matter.

---

## 5. Recommended Stack

### 5.1 Frontend
- **React 19**
- **Next.js 15+** or **Vite + React 19** for the frontend shell
- **Tailwind CSS**
- **shadcn/ui**
- **TanStack Query** for async state
- **Zustand** or **Redux Toolkit** for local UI state
- **Framer Motion** for subtle interaction polish

### 5.2 Backend / API
- **Python**
- **FastAPI** for media processing and AI orchestration
- **Celery / RQ / Dramatiq** if background workers are required
- **Redis** for job queueing and cache
- **Docker** for reproducible deployment

### 5.3 Media Processing
- **yt-dlp** for YouTube downloading
- **FFmpeg** for audio extraction and normalization
- Mono, **16 kHz WAV** output for transcription compatibility

### 5.4 Speech-to-Text
- **Local Whisper** for English transcription
- **Sarvam AI** for Hindi/Hinglish support where it improves quality
- Optional fallback routing by language detection

### 5.5 LLM
- **DeepSeek API** as the primary LLM
- Use it for:
  - summaries,
  - extraction,
  - query answering,
  - and response synthesis over retrieved chunks

### 5.6 RAG / Retrieval
- **LangChain LCEL**
- **ChromaDB** as vector store
- **Hugging Face sentence-transformer embeddings**

### 5.7 Deployment
- **Vercel** for the frontend
- A separate Python backend deployment for media-heavy work if needed
- If the backend must remain in one repo, treat Vercel as the frontend plus API gateway and offload heavy processing to a worker service

---

## 6. What “Hugging Face” Means in This Project

Hugging Face is the ecosystem you use when you want:
- pre-trained embedding models,
- open-source NLP models,
- model hosting,
- and a common interface for ML tooling.

In this project, Hugging Face is mainly useful for **embeddings**.  
That means the transcript is broken into chunks, each chunk is converted into a numeric vector, and those vectors are stored in ChromaDB. Later, when a user asks a question, the system finds the most relevant chunks and sends them to the LLM for an answer.

This makes the assistant more grounded and less likely to hallucinate.

---

## 7. User Experience

### 7.1 Primary Flow
1. User opens the app.
2. User pastes a YouTube URL or uploads an audio/video file.
3. System validates the source.
4. System downloads or ingests media.
5. System extracts audio and normalizes it.
6. System transcribes the audio.
7. System generates:
   - title,
   - summary,
   - action items,
   - decisions,
   - open questions.
8. System embeds transcript chunks into ChromaDB.
9. User asks questions in a chat panel.
10. Assistant answers using RAG over the meeting content.

### 7.2 User Interface Requirements
The UI must include:
- source input panel,
- upload support,
- processing progress state,
- transcript display,
- generated meeting report,
- chat interface,
- error and retry states,
- export/download options.

### 7.3 UI Quality Bar
The product should feel:
- fast,
- modern,
- minimal,
- and “real”.

No generic demo layouts.  
No cluttered admin-dashboard appearance.  
No weak visual hierarchy.

---

## 8. Functional Requirements

## 8.1 Source Ingestion
The system must support:
- YouTube URL input
- local audio upload
- local video upload

### Acceptance Criteria
- Invalid URLs are rejected gracefully.
- Unsupported file formats show a clear error.
- Long media is handled without UI freeze.
- Progress state is visible to the user.

---

## 8.2 Audio Extraction and Optimization
The system must:
- download audio from YouTube using `yt-dlp`,
- extract audio from video files,
- convert audio to **WAV, mono, 16 kHz**,
- split long recordings into manageable chunks,
- normalize volume where useful.

### Acceptance Criteria
- Output audio is transcription-ready.
- Chunking is deterministic.
- Chunk metadata is preserved.

---

## 8.3 Transcription and Language Handling
The system must:
- transcribe English audio using local Whisper,
- support Hindi/Hinglish using Sarvam AI,
- route by language heuristics or user selection,
- preserve timestamps.

### Acceptance Criteria
- Transcript is segmented with timestamps.
- Language-specific path is transparent to the user.
- Fallback behavior exists if one transcription path fails.

---

## 8.4 Summarization
The system must generate:
- a concise overview,
- bullet-point summary,
- important takeaways,
- and a meeting title.

### Acceptance Criteria
- Summary is readable and not overly verbose.
- Output follows a stable structure.
- Key decisions and actions are highlighted clearly.

---

## 8.5 Structured Extraction
The system must extract:
- **Action Items**
  - owner
  - deadline
  - task description
- **Key Decisions**
- **Open Questions / Follow-ups**

### Acceptance Criteria
- Output is structured and easy to scan.
- Missing owners/deadlines are marked explicitly as unknown.
- Extraction is robust across informal meeting language.

---

## 8.6 RAG Chat
The system must:
- chunk the transcript,
- embed chunks,
- store vectors in ChromaDB,
- retrieve relevant chunks for user queries,
- answer questions grounded in the meeting content.

### Acceptance Criteria
- Chat responses cite or reflect transcript evidence.
- Relevant chunks are retrieved before answer generation.
- The assistant does not answer purely from memory when context exists.

---

## 8.7 Export / Delivery
The system should allow:
- copyable transcript,
- downloadable summary report,
- markdown export,
- and README-friendly output structure.

---

## 9. Architecture

### 9.1 Recommended High-Level Architecture
**Frontend**
- React 19 app for user interactions

**API Layer**
- FastAPI for upload handling, processing orchestration, and RAG queries

**Background Processing**
- Worker process for media extraction, transcription, embedding, and summarization

**Storage**
- Local filesystem or object storage for raw uploads and processed media
- ChromaDB for embeddings
- JSON/SQLite/Postgres for job metadata depending on scale

### 9.2 Architecture Rationale
A fully serverless setup is not ideal for long media processing.  
Heavy media tasks, FFmpeg work, Whisper inference, and vector indexing are better handled outside short-lived request lifecycles.

For cost efficiency:
- keep frontend lightweight,
- keep most AI work on the cheapest practical path,
- and use background jobs for long-running tasks.

---

## 10. Cost Strategy

### 10.1 Cost Goals
- Keep the product usable on a very low budget.
- Avoid unnecessary paid infrastructure.
- Use free/open-source components wherever possible.

### 10.2 Cost-Control Choices
- Local Whisper for English instead of always calling a paid API.
- Sarvam AI only where it improves non-English quality.
- DeepSeek API for LLM tasks instead of a more expensive alternative.
- ChromaDB locally for vector storage.
- Hugging Face embeddings instead of a proprietary embedding stack.
- One backend worker instead of multiple separate AI services.

### 10.3 Practical Cost Notes
The lowest-cost version of this system is:
- frontend hosted cheaply,
- backend in a single container,
- media processing local or on a small compute instance,
- LLM usage limited to summarization and final answers,
- embeddings computed once per meeting.

The biggest cost drivers will be:
- LLM token usage,
- transcription compute,
- and media processing duration.

---

## 11. Performance Requirements

### 11.1 Functional Performance Targets
- Small files should complete quickly enough for interactive use.
- Large files should show progress and not fail silently.
- Chat responses should feel responsive after retrieval is prepared.

### 11.2 Quality Targets
- The system should be robust to noisy speech.
- The system should handle long meetings without collapsing context.
- Outputs should remain readable even when transcripts are imperfect.

---

## 12. Error Handling

The system must handle:
- invalid YouTube URLs,
- blocked downloads,
- unsupported formats,
- transcription failures,
- language misclassification,
- empty or low-quality audio,
- vector store initialization failures,
- LLM API failures,
- worker timeouts.

Each error state should:
- explain what happened,
- indicate what the user can do next,
- and preserve any partial work if possible.

---

## 13. Security and Privacy

### 13.1 Principles
- Minimize data exposure.
- Keep files local when possible.
- Do not leak transcript content outside the intended processing flow.
- Avoid storing raw media longer than necessary.

### 13.2 Considerations
- User uploads may contain sensitive meeting content.
- YouTube URLs should be processed only for the requested session.
- Clear retention policy should be documented in the README.

---

## 14. Deployment

### 14.1 Primary Target
**Vercel for frontend deployment**

### 14.2 Recommended Production Setup
Because media processing and transcription are not a great fit for short-lived serverless execution, the recommended setup is:

- **Vercel**: frontend UI
- **Python backend**: containerized API and worker
- **Redis / queue**: background processing
- **ChromaDB**: persistent vector store
- **Storage**: local volume or managed storage depending on deployment environment

### 14.3 Why This Matters
Vercel is excellent for the UI, but long-running tasks are better handled by a dedicated backend worker. This design keeps the user experience fast and avoids deployment friction.

---

## 15. Recommended Project Structure

```bash
ai-meeting-assistant/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── workers/
│   │   └── utils/
│   ├── tests/
│   └── Dockerfile
├── README.md
├── docker-compose.yml
└── .env.example
```

---

## 16. Suggested API Surface

### 16.1 Upload and Processing
- `POST /api/process`
- `GET /api/jobs/{job_id}`
- `GET /api/transcripts/{meeting_id}`
- `GET /api/report/{meeting_id}`

### 16.2 Chat
- `POST /api/chat`

### 16.3 Health
- `GET /api/health`

---

## 17. Data Model

### 17.1 Core Entities
**Meeting**
- id
- title
- source_type
- source_url / file_name
- language
- created_at

**TranscriptChunk**
- id
- meeting_id
- chunk_index
- start_time
- end_time
- text
- embedding_id

**SummaryReport**
- meeting_id
- summary
- action_items
- decisions
- open_questions

**ChatMessage**
- meeting_id
- role
- content
- created_at

---

## 18. README.md Requirements

The repository must include a high-quality `README.md` with:
- product overview,
- feature list,
- architecture diagram or explanation,
- tech stack,
- local setup instructions,
- environment variables,
- how transcription works,
- how RAG chat works,
- deployment steps,
- cost notes,
- troubleshooting,
- limitations,
- and roadmap.

The README should feel like a serious open-source product, not a student demo.

---

## 19. Roadmap

### Phase 1 — MVP
- URL/file input
- audio extraction
- transcription
- summary
- action items
- simple chat

### Phase 2 — Production Polish
- better progress indicators
- error recovery
- markdown export
- job history
- cleaner UI
- prompt refinement

### Phase 3 — Advanced Quality
- smarter language routing
- better chunking
- richer citation behavior
- improved retrieval tuning
- optional diarization

### Phase 4 — Portfolio Showcase
- beautiful landing page
- demo data
- example reports
- deployment hardening
- documentation refinement

---

## 20. Success Metrics

The project is successful if:
- users can process a meeting without confusion,
- the report is consistently useful,
- chat answers are grounded in transcript context,
- the UI looks production-grade,
- the README makes the project easy to understand,
- and the whole system stays cost-efficient.

---

## 21. Final Product Definition

This is not just a transcription tool.  
It is a **meeting intelligence system** with:
- ingestion,
- speech-to-text,
- summarization,
- extraction,
- retrieval,
- and conversational analysis.

The product should demonstrate engineering maturity, practical AI design, and strong portfolio value.

---

## 22. Deliverables
- Production-grade PRD
- React-based frontend
- Python backend
- RAG pipeline
- DeepSeek-powered analysis layer
- README.md
- Dockerized deployment setup
