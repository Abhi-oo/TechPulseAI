# TechPulse AI 🚀

An AI-powered technology intelligence network where AI agents discover, investigate, verify, explain, rank, and continuously update technology and AI developments.

## Architecture & Workflow

```text
DISCOVER ➔ CLUSTER ➔ INVESTIGATE ➔ VERIFY ➔ EXPLAIN ➔ RANK ➔ PUBLISH ➔ UPDATE
```

- **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS
- **Backend:** Python 3.11+, FastAPI, Pydantic, SQLAlchemy / Supabase PostgreSQL
- **AI Core:** Targeted LLM Agents (Research & Verification, Short-News, Story Evolution)
- **Deterministic Engine:** Feed Ingestion, Temporal Clustering, Corroboration Scoring, Gravity Ranking

---

## Repository Structure

```text
TechPulseAI/
├── .env.example
├── .gitignore
├── README.md
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── ...
└── frontend/
    ├── src/
    │   ├── app/
    │   └── ...
    ├── package.json
    └── ...
```

---

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+

### 1. Environment Setup
Copy the template environment file:
```bash
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Backend Swagger API Docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend Web Dashboard will be available at: [http://localhost:3000](http://localhost:3000)
