# PhysioMind — AI Document Assistant

A production-ready RAG (Retrieval-Augmented Generation) system for intelligent PDF document Q&A with source attribution.

## Features

- 📄 **PDF Management** — Upload, list, and delete PDF documents
- 🧠 **Smart Q&A** — Ask questions and get accurate answers from your documents
- 📌 **Source Attribution** — Every answer cites the exact file and page number
- ⚙️ **Custom Instructions** — Provide system prompts to customize AI behavior
- ⚡ **Fast Inference** — Powered by Groq API for near-instant responses

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (Vite), React Router, Axios |
| Backend | FastAPI, Python |
| RAG Pipeline | LangChain + LangGraph |
| Vector DB | ChromaDB (persistent) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| LLM | Groq API (Llama 3.3 70B) |
| Storage | Supabase (Storage + Postgres) |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account with Storage bucket and `pdf_documents` table
- Groq API key

### Supabase Setup

1. Create a new Supabase project
2. Create a Storage bucket named `pdfs`
3. Run this SQL in the SQL editor:

```sql
CREATE TABLE pdf_documents (
    id UUID PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    supabase_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE pdf_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON pdf_documents FOR ALL USING (true) WITH CHECK (true);
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Project Structure

```
PhysioMind/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── api/                # Route handlers
│       ├── core/               # Config & logging
│       ├── models/             # Data models
│       ├── schemas/            # Pydantic schemas
│       ├── services/           # Supabase & ChromaDB
│       ├── rag/
│       │   ├── ingestion/      # PDF processing
│       │   ├── retrieval/      # Chunk retrieval
│       │   └── generation/     # LLM + LangGraph
│       └── utils/
├── frontend/
│   └── src/
│       ├── components/         # Reusable UI components
│       ├── pages/              # Dashboard & Chat
│       ├── hooks/              # Custom React hooks
│       ├── services/           # API layer
│       └── utils/              # Formatters
└── README.md
```

## Deployment

### Backend (Render)

1. Push the `backend/` directory to a Git repo
2. Create a new Web Service on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`

### Frontend (Vercel)

1. Push the `frontend/` directory to a Git repo
2. Import project on Vercel
3. Set `VITE_API_URL` to your Render backend URL

## License

MIT
