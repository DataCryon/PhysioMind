# DocMind — AI Document Assistant

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
| Vector DB | **Supabase Vector (pgvector)** |
| Embeddings | Google Gemini API (`gemini-embedding-2`) |
| LLM | Groq API (Llama 3.3 70B) |
| Storage | Supabase (Storage + Postgres) |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- **Supabase account** (Free)
- **Groq API key** (Free)
- **Google AI Studio API key** (Free)

### Supabase Setup (Free & Persistent)

1. Create a new Supabase project.
2. Create a Storage bucket named `pdfs` and set it to **Public**.
3. Run the following SQL in your Supabase SQL Editor:

```sql
-- Enable the pgvector extension
create extension if not exists vector;

-- Table for document metadata
CREATE TABLE pdf_documents (
    id UUID PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    supabase_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for document chunks and their embeddings
CREATE TABLE doc_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT,
    metadata JSONB,
    embedding VECTOR(384) -- Using 384 dimensions for compatibility
);

-- Function for similarity search
CREATE OR REPLACE FUNCTION match_chunks (
  query_embedding VECTOR(384),
  match_threshold FLOAT,
  match_count INT,
  filter_file_id TEXT DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    doc_chunks.id,
    doc_chunks.content,
    doc_chunks.metadata,
    1 - (doc_chunks.embedding <=> query_embedding) AS similarity
  FROM doc_chunks
  WHERE (filter_file_id IS NULL OR (doc_chunks.metadata->>'file_id') = filter_file_id)
    AND 1 - (doc_chunks.embedding <=> query_embedding) > match_threshold
  ORDER BY doc_chunks.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- RLS Policies
ALTER TABLE pdf_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON pdf_documents FOR ALL USING (true) WITH CHECK (true);
ALTER TABLE doc_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON doc_chunks FOR ALL USING (true) WITH CHECK (true);
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Add your Groq, Google, and Supabase keys here
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Deployment (100% Free Tier)

### Backend (Render)
1. Push your code to GitHub.
2. Create a new **Blueprint Instance** on Render using the root `render.yaml`.
3. Set the required environment variables (`GROQ_API_KEY`, `GOOGLE_API_KEY`, etc.) in the Render dashboard.

### Frontend (Vercel)
1. Import your repo into Vercel.
2. Set the `frontend` folder as the Root Directory.
3. Add the environment variable:
   - `VITE_API_URL`: Your Render service URL + `/api` (e.g., `https://docmind-api.onrender.com/api`)

## License

MIT
