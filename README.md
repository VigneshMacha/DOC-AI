# ⚡ Chanti AI

<p align="center">
  <strong>Enterprise RAG Document Intelligence Platform</strong>
</p>

<p align="center">
  Upload documents • Ask questions • Retrieve relevant context • Get grounded AI answers with citations
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Mistral_AI-LLM%20%26%20Embeddings-FD6F00?style=for-the-badge&logo=mistralai&logoColor=white" alt="Mistral AI" />
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL%20%2B%20pgvector-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/Deployment-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License" />
</p>

---

## 🎯 What is Chanti AI?

**Chanti AI** is a production-oriented **Retrieval-Augmented Generation (RAG)** platform that allows users to interact with their PDF documents using natural language.

Instead of asking an LLM to answer from its general knowledge, Chanti AI first retrieves relevant information from the user's documents and then provides that context to the language model.

This makes responses:

* 📚 **Document-grounded**
* 🔎 **Retrievable**
* 📄 **Page-aware**
* 🔐 **User-scoped**
* 🧠 **Context-aware**
* 🚫 **Less prone to hallucination**

### The core idea

```text
Your Documents
      ↓
PDF Extraction / OCR
      ↓
Text Chunking
      ↓
Mistral Embeddings
      ↓
Supabase pgvector
      ↓
Semantic Retrieval
      ↓
Relevant Context
      ↓
Mistral Small
      ↓
Grounded Answer + Citations
```

---

# ✨ Key Highlights

### 📄 Intelligent Document Processing

* PDF text extraction
* Automatic OCR fallback for scanned PDFs
* Page-level metadata preservation
* Recursive text chunking
* Configurable chunk size and overlap

### 🧠 Semantic Retrieval

* Mistral `mistral-embed`
* 1024-dimensional embeddings
* PostgreSQL `pgvector`
* Cosine similarity search
* HNSW indexing
* Metadata filtering

### 🤖 Grounded Generation

* Mistral Small LLM
* Retrieved-context prompting
* Conversation-aware responses
* Anti-hallucination instructions
* Page-level citations

### 🔐 Multi-User Architecture

* User authentication
* Session-based access
* User-scoped document retrieval
* Metadata-based tenant filtering
* Protected application routes

### 🎨 Modern Interface

* Responsive dark-mode workspace
* Document management
* Chat interface
* Markdown rendering
* Citation inspector
* Starter prompts
* Responsive sidebar
* Mobile-friendly layout

---

# 🖥️ Application Preview

> Add screenshots of your actual application here.

```text
docs/
├── screenshots/
│   ├── dashboard.png
│   ├── document-upload.png
│   ├── chat.png
│   └── citations.png
```

Recommended README layout:

```markdown
## 📸 Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

### Document Upload

![Upload](docs/screenshots/document-upload.png)

### AI Chat

![Chat](docs/screenshots/chat.png)

### Source Citations

![Citations](docs/screenshots/citations.png)
```

A short demo GIF is also highly recommended.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │       USER           │
                         │   Web Application    │
                         └──────────┬───────────┘
                                    │
                         Upload / Chat Request
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │       FastAPI Backend     │
                    │                           │
                    │ Auth • API • RAG Control  │
                    └─────────────┬─────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
        ┌──────────────────┐              ┌──────────────────┐
        │ Document Upload  │              │   User Query     │
        └────────┬─────────┘              └────────┬─────────┘
                 │                                 │
                 ▼                                 ▼
        ┌──────────────────┐              ┌──────────────────┐
        │ PDF Extraction   │              │ Query Embedding  │
        │      PyPDF       │              │   Mistral Embed  │
        └────────┬─────────┘              └────────┬─────────┘
                 │                                 │
           Text available?                         │
                 │                                 │
          ┌──────┴──────┐                          │
          │             │                          │
         YES            NO                         │
          │             │                          │
          │             ▼                          │
          │      ┌──────────────┐                  │
          │      │ OCR Pipeline │                  │
          │      │ PyMuPDF +    │                  │
          │      │ Tesseract    │                  │
          │      └──────┬───────┘                  │
          │             │                          │
          └──────┬──────┘                          │
                 │                                 │
                 ▼                                 │
        ┌──────────────────┐                       │
        │ Text Chunking    │                       │
        │ 1000 / 100       │                       │
        └────────┬─────────┘                       │
                 │                                 │
                 ▼                                 │
        ┌──────────────────┐                       │
        │ Mistral Embed    │                       │
        │ 1024 Dimensions  │                       │
        └────────┬─────────┘                       │
                 │                                 │
                 └─────────────┬───────────────────┘
                               │
                               ▼
                   ┌─────────────────────────┐
                   │ Supabase PostgreSQL     │
                   │                         │
                   │ pgvector                │
                   │ HNSW Index              │
                   │ Metadata                │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │ Semantic Retrieval      │
                   │                         │
                   │ Top-K Relevant Chunks   │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │ Context Construction    │
                   │                         │
                   │ System Prompt           │
                   │ Retrieved Chunks        │
                   │ Chat History            │
                   │ User Question            │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │      Mistral Small      │
                   │          LLM            │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │ Grounded Response       │
                   │ + Page Citations        │
                   └─────────────────────────┘
```

---

# 🔄 RAG Pipeline

## Phase 1 — Ingestion

```text
PDF
 │
 ▼
File Validation
 │
 ▼
Text Extraction
 │
 ├── Normal PDF ──────────────┐
 │                            │
 └── Scanned PDF              │
          ↓                   │
      OCR Pipeline            │
          ↓                   │
          └──────────┬────────┘
                     ▼
               Text Cleaning
                     │
                     ▼
                  Chunking
                     │
                     ▼
              Mistral Embedding
                     │
                     ▼
             Supabase pgvector
```

### Default chunk configuration

```text
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 100
```

Each chunk retains useful metadata:

```json
{
  "user_id": "user-id",
  "document_id": "document-id",
  "filename": "report.pdf",
  "page": 12
}
```

---

# 🔎 Phase 2 — Retrieval

When the user asks a question:

```text
User Question
      ↓
Mistral Embedding
      ↓
Query Vector
      ↓
Supabase RPC
      ↓
HNSW / Cosine Similarity
      ↓
Metadata Filtering
      ↓
Top-K Relevant Chunks
```

The retrieval layer combines:

```text
Semantic Similarity
        +
User Filtering
        +
Document Metadata
```

---

# 🤖 Phase 3 — Generation

Retrieved chunks are injected into the LLM context.

```text
System Instructions
        +
Retrieved Document Chunks
        +
Conversation History
        +
Current Question
        ↓
   Mistral Small
        ↓
Grounded Response
        +
Source Citations
```

The model is instructed to prioritize retrieved document context and avoid unsupported claims.

---

# 🗂️ Project Structure

```text
chanti-ai/
│
├── backend/
│   ├── database.py
│   ├── main.py
│   │
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   └── templates/
│       ├── index.html
│       ├── login.html
│       └── signup.html
│
├── services/
│   ├── ingestion.py
│   ├── models.py
│   └── rag.py
│
├── config.py
├── requirements.txt
├── Dockerfile
├── Procfile
├── .env.example
├── .gitignore
└── README.md
```

### Core modules

| File                    | Responsibility                                  |
| ----------------------- | ----------------------------------------------- |
| `backend/main.py`       | FastAPI application, routes and lifecycle       |
| `backend/database.py`   | Supabase connection and database operations     |
| `services/ingestion.py` | PDF parsing, OCR, chunking and vector ingestion |
| `services/models.py`    | Mistral LLM and embedding initialization        |
| `services/rag.py`       | Retrieval, context construction and generation  |
| `config.py`             | Application configuration                       |
| `backend/templates/`    | Frontend HTML                                   |
| `backend/static/`       | CSS and JavaScript                              |

---

# 🛠️ Tech Stack

| Layer          | Technology                      |
| -------------- | ------------------------------- |
| Backend        | FastAPI                         |
| Language       | Python 3.10+                    |
| PDF Processing | PyPDF / PyMuPDF                 |
| OCR            | Tesseract                       |
| Embeddings     | Mistral `mistral-embed`         |
| LLM            | Mistral Small                   |
| Database       | PostgreSQL                      |
| Vector Search  | Supabase pgvector               |
| Vector Index   | HNSW                            |
| Authentication | Supabase / Application Sessions |
| Frontend       | HTML, CSS, JavaScript           |
| UI             | Tailwind CSS                    |
| Icons          | Lucide                          |
| Markdown       | Marked.js                       |
| Deployment     | Render / Docker                 |

---

# 🚀 Getting Started

## Prerequisites

Install:

* Python 3.10+
* Git
* Supabase account
* Mistral AI account/API key
* Tesseract OCR

Python 3.11 is recommended.

---

# 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/chanti-ai.git
cd chanti-ai
```

---

# 2️⃣ Create Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 4️⃣ Configure Environment

Create `.env`:

```env
# Mistral
MISTRAL_API_KEY=your_mistral_api_key
EMBEDDING_MODEL=mistral-embed
LLM_MODEL=mistral-small-2603

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Application
COOKIE_SECURE=false

# RAG
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
```

### Production

Set:

```env
COOKIE_SECURE=true
```

when serving the application over HTTPS.

---

# 🗄️ Database Setup

Enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Create the vector table:

```sql
CREATE TABLE document_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ
        DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

Create the HNSW index:

```sql
CREATE INDEX document_vectors_embedding_idx
ON document_vectors
USING hnsw (embedding vector_cosine_ops);
```

Create metadata index:

```sql
CREATE INDEX idx_doc_vectors_metadata
ON document_vectors
USING gin (metadata);
```

Create the retrieval RPC:

```sql
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding VECTOR(1024),
    match_count INT DEFAULT 4,
    filter JSONB DEFAULT '{}'::jsonb
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
        dv.id,
        dv.content,
        dv.metadata,
        1 - (dv.embedding <=> query_embedding) AS similarity
    FROM document_vectors dv
    WHERE dv.metadata @> filter
    ORDER BY dv.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

Reload the PostgREST schema:

```sql
NOTIFY pgrst, 'reload schema';
```

> **Important:** For a real production multi-tenant deployment, configure restrictive RLS policies around the authenticated user's identity. Application-side `user_id` filtering should be treated as an additional safeguard, not the only tenant-isolation mechanism.

---

# ▶️ Run Locally

```bash
uvicorn backend.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000
```


# ☁️ Deploying to Render

Create a new **Web Service** and connect your GitHub repository.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2
```

### Required Environment Variables

```text
MISTRAL_API_KEY
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
EMBEDDING_MODEL
LLM_MODEL
COOKIE_SECURE
CHUNK_SIZE
CHUNK_OVERLAP
```

Set:

```text
COOKIE_SECURE=true
```

for production HTTPS.

---

# 🔌 API Overview

The exact endpoints may vary with the current implementation, but the backend is organized around operations such as:

```text
Authentication
├── Register
├── Login
└── Logout

Documents
├── Upload
├── List
├── Delete
└── Process

Chat
├── Create Conversation
├── Send Message
├── Retrieve Context
└── Delete Conversation
```

A future production version can expose a documented OpenAPI interface automatically through FastAPI.

---

# 🔐 Security Architecture

Chanti AI is designed around user-scoped access.

```text
Authenticated User
        ↓
Session Validation
        ↓
User ID
        ↓
Document Metadata Filter
        ↓
Vector Retrieval
        ↓
Relevant User Documents
```

Security considerations include:

* HTTP-only cookies
* SameSite cookie protection
* Secure cookies in production
* User-scoped retrieval
* Server-side API keys
* Input validation
* File validation
* Prompt/input limits
* Database-level access control

### Never expose these variables to the frontend:

```text
MISTRAL_API_KEY
SUPABASE_SERVICE_ROLE_KEY
```

---

# 🧪 Testing Checklist

Before deployment, verify:

```text
Authentication
[ ] User registration works
[ ] Login works
[ ] Logout works
[ ] Unauthorized routes are protected

Documents
[ ] PDF upload works
[ ] Multiple uploads work
[ ] Normal PDFs are parsed
[ ] Scanned PDFs trigger OCR
[ ] Documents appear in the UI
[ ] Documents can be deleted

RAG
[ ] Embeddings are generated
[ ] Vectors are stored
[ ] Retrieval returns relevant chunks
[ ] User filtering works
[ ] Citations show correct pages
[ ] Hallucination fallback works

Chat
[ ] Conversations can be created
[ ] Messages are persisted
[ ] Chat history works
[ ] Conversations can be deleted

Production
[ ] Environment variables are configured
[ ] HTTPS cookies are enabled
[ ] Logs are clean
[ ] Secrets are not committed
[ ] Docker build succeeds
```

---

# ⚡ Performance Considerations

Chanti AI uses several techniques to keep retrieval efficient:

### HNSW

The HNSW index enables approximate nearest-neighbor vector search.

### Metadata Indexing

A GIN index accelerates JSONB metadata filtering.

### Chunking

Moderately sized chunks reduce unnecessary context while preserving semantic information.

### Top-K Retrieval

Only the most relevant chunks are sent to the LLM rather than the entire document.

---

# ⚠️ Current Limitations

RAG systems still have important limitations.

Chanti AI may produce weaker answers when:

* A document contains very little usable text
* OCR quality is poor
* The answer spans many distant pages
* Tables are complex
* Important information is embedded inside images
* Retrieved chunks do not contain enough context
* The user asks questions outside the uploaded documents

These limitations can be addressed through future improvements such as:

* Hybrid search
* Reranking
* Query rewriting
* Table extraction
* Multimodal retrieval
* Better OCR pipelines
* Contextual chunking


---

# 🧠 Why RAG?

Traditional LLM applications:

```text
User Question
      ↓
LLM
      ↓
Answer
```

Chanti AI:

```text
User Question
      ↓
Semantic Retrieval
      ↓
Relevant Document Context
      ↓
LLM
      ↓
Grounded Answer
      ↓
Source Citation
```

This architecture reduces dependence on the model's general knowledge and allows the system to answer questions using private, user-provided information.

---

# 🎓 What This Project Demonstrates

Chanti AI demonstrates practical implementation of:

* Retrieval-Augmented Generation
* Vector databases
* Semantic search
* Embedding models
* LLM integration
* Prompt engineering
* PDF processing
* OCR
* PostgreSQL
* pgvector
* HNSW indexing
* FastAPI backend development
* Authentication
* Multi-tenant application design
* REST APIs
* Responsive frontend development
* Docker
* Cloud deployment

This makes the project suitable as a portfolio project for **Generative AI, Backend Engineering, AI Engineering, and Full-Stack roles**.

---

# 🤝 Contributing

Contributions are welcome.

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Make your changes, test them, and submit a pull request.

Please ensure that:

* Existing functionality continues to work
* Secrets are not committed
* New features are documented
* Database changes are documented
* API changes are tested

---

# 📜 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

# ⭐ Chanti AI

<p align="center">
  <strong>Ask your documents. Get answers you can verify.</strong>
</p>

```text
              CHANTI AI

        📄 Your Documents
               │
               ▼
        🔍 Document Parsing
               │
               ▼
          ✂️ Chunking
               │
               ▼
       🧠 Embeddings
               │
               ▼
       🗄️ Vector Database
               │
               ▼
       🔎 Semantic Search
               │
               ▼
         🤖 Mistral LLM
               │
               ▼
       📚 Grounded Answer
               │
               ▼
        🔗 Citations
```

---

