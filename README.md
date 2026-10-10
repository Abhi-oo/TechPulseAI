# TechPulse AI 🚀

An autonomous technology intelligence network powered by targeted AI agents. TechPulse AI discovers breaking technology developments, investigates factual claims, verifies corroboration across primary and news sources, computes deterministic confidence scores, generates structured intelligence triads (WHAT / WHY / IMPACT), and ranks stories for live distribution.

---

## 📸 Demo & Screenshots

<p align="center">
  <img src="assets/techpulse-dashboard-dark.png" alt="TechPulse AI Autonomous Technology Intelligence Dashboard" width="100%" />
</p>

| Light Mode Dashboard | Dark Mode Dashboard |
| :---: | :---: |
| <img src="assets/techpulse-dashboard.png" alt="TechPulse AI Light Mode" width="100%" /> | <img src="assets/techpulse-dashboard-dark.png" alt="TechPulse AI Dark Mode" width="100%" /> |
| *Clean slate & high contrast* | *Futuristic charcoal & cyan accents* |

> **Demo Video:** [Watch the TechPulse AI Walkthrough Video](https://github.com/Abhi-oo/TechPulseAI/releases) *(or replace with your YouTube/Loom link)*

---

## ⚡ Core Features

- **Autonomous News Ingestion & Discovery:** Multi-threaded RSS feed fetching across Tier 1, Tier 2, and Primary sources (OpenAI, Hugging Face, Anthropic, TechCrunch, Verge, Ars Technica) with temporal clustering and deduplication.
- **Agentic Claim Extraction & Fact Verification:** Identifies discrete factual assertions and investigates them against primary and reporting sources, classifying claims as `CONFIRMED`, `DISPUTED`, or `UNCONFIRMED`.
- **Deterministic Confidence Scoring (0–100):** Strictly algorithmic scoring based on source reliability weights, corroboration count, and consensus ratio — never hallucinated by LLMs.
- **Short-News Intelligence Triad:** Generates structured, concise cards with:
  - **WHAT HAPPENED:** Concise factual breakdown (< 30 words).
  - **WHY IT MATTERS:** Context, industry significance, and strategic relevance.
  - **ECOSYSTEM IMPACT:** Ripple effects across developers, enterprises, and open source.
- **Multi-Factor Gravity Ranking:** Deterministic formula balancing Recency (30%), Importance (30%), Ecosystem Impact (20%), and Confidence (20%), with automated demotion for disputed or low-confidence claims.
- **Futuristic AI Frontend (Next.js 16 + React 19 + Tailwind CSS v4):**
  - **Zero-FOUC Dual-Theme:** Seamless Light & Dark mode toggle with instant pre-hydration initialization and OS preference sync.
  - **Classic Entrance Animation:** Smooth 750ms upward settling bump on initial page load.
  - **Independent Dashboard Partitions:** Fixed header, stationary left sidebar partition, and independently scrolling intelligence feed with zero scroll jitter.
  - **Live Channels Sidebar:** Interactive micro-animations with 4px bump lift on hover and focus.
  - **Dossier Inspection Modal:** Deep-dive modal showing verified claims, grounding quotes, and chronological story timeline updates.

---

## 🏗️ Architecture & Technology Stack

```text
RSS Feeds ──► Ingestion Service ──► Discovery Agent ──► Research Agent ──► Verification Engine
                                                                                   │
                                                                         Confidence Calculation
                                                                                   │
Frontend ◄── Read-Only API ◄── Supabase PostgreSQL ◄── Ranking Service ◄── Short-News Agent
(Next.js)      (FastAPI)
```

### Technology Stack
- **Frontend:** Next.js 16.3.8 (App Router), React 19, TypeScript 5, Tailwind CSS v4 (zero external UI dependencies).
- **Backend API:** FastAPI, Uvicorn, Pydantic v2, HTTPX, Feedparser, BeautifulSoup4.
- **AI Core:** Google Gemini (`gemini-1.5-flash` / `gemini-pro`) with deterministic heuristic fallbacks.
- **Database & Storage:** Supabase PostgreSQL with `pgcrypto` UUIDs and relational foreign keys (`sources`, `submissions`, `stories`, `story_sources`, `claims`, `story_updates`).

---

## 📂 Project Structure

```text
TechPulseAI/
├── .env.example                  # Template configuration with safe placeholders
├── .gitignore                    # Git ignore file excluding secrets and build artifacts
├── README.md                     # Comprehensive project documentation
├── assets/                       # UI screenshots, architecture graphics & demo assets
│   ├── techpulse-dashboard.png
│   └── techpulse-dashboard-dark.png
├── backend/
│   ├── agents/                   # Autonomous AI agents (discovery, research, short_news)
│   ├── migrations/               # PostgreSQL DDL migrations (001_initial_schema.sql)
│   ├── routers/                  # FastAPI routers (stories, discovery, research, short_news)
│   ├── schemas/                  # Pydantic data schemas
│   ├── services/                 # Core algorithms (confidence, ranking, verification, rss)
│   ├── tests/                    # Comprehensive unit and integration test suite
│   ├── config.py                 # Pydantic settings loading from .env
│   ├── database.py               # Supabase and psycopg2 client factories
│   ├── main.py                   # FastAPI application entrypoint
│   ├── requirements.txt          # Python dependencies
│   └── run_migration.py          # Migration execution and verification script
└── frontend/
    ├── src/
    │   ├── app/                  # Next.js App Router (layout, page, globals.css)
    │   ├── components/           # UI components (Navbar, Sidebar, StoryCard, Modal, etc.)
    │   ├── context/              # Zero-dependency ThemeContext (light/dark mode)
    │   ├── lib/                  # Fetch API client
    │   └── types/                # TypeScript interface definitions
    ├── package.json              # Frontend npm dependencies
    └── tsconfig.json             # TypeScript configuration
```

---

## 🛠️ Getting Started

### Prerequisites
- **Python:** 3.11 or higher
- **Node.js:** 18.18 or higher (LTS recommended) and npm
- **Database:** A free [Supabase](https://supabase.com) account (or standard PostgreSQL 15+ database)
- **AI API Key:** A [Google AI Studio Gemini API Key](https://aistudio.google.com/)

---

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:
```ini
# Supabase PostgreSQL Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
DATABASE_URL=postgresql://postgres:your-db-password@db.your-project-id.supabase.co:5432/postgres

# AI / LLM Configuration
GEMINI_API_KEY=your-gemini-api-key

# Backend Service Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ENVIRONMENT=development
PIPELINE_SECRET_KEY=your-internal-secret-token

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

> **Security Note:** Never commit `.env` or expose private API keys. The root `.gitignore` is configured to prevent accidental commits of `.env` files.

---

### 2. Database Migration

Run the automated migration runner to apply the schema and seed default news sources into your database:
```bash
python backend/run_migration.py
```
This script validates table creation for `sources`, `submissions`, `stories`, `story_sources`, `claims`, `story_updates`, and `agent_runs`.

---

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell / Command Prompt):
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend test suite
python -m unittest discover -s tests -v

# Start FastAPI development server
uvicorn main:app --reload --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health Status: [http://localhost:8000/health](http://localhost:8000/health)

---

### 4. Frontend Setup

```bash
# Navigate to frontend directory in a new terminal
cd frontend

# Install dependencies
npm install

# Build for production verification
npm run build

# Start Next.js development server
npm run dev
```
- Open the application dashboard: [http://localhost:3000](http://localhost:3000)

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/stories` | List canonical stories with channel filtering, search query, and sorting (`rank`, `recent`, `confidence`). |
| `GET` | `/api/v1/stories/{id}` | Retrieve comprehensive story dossier including verified claims and chronological timeline. |
| `GET` | `/api/v1/stats` | Retrieve platform-wide telemetry metrics (total stories, verified claims, average confidence). |
| `POST` | `/api/v1/pipeline/scan` | Trigger real-time RSS discovery, claim extraction, and ranking pipeline. |

---

## 🎬 Demo Video Guidance

For sharing your project walkthrough:
- **Under 25 MB:** Can be committed to an `assets/` folder in the repository or uploaded directly to the GitHub Release.
- **Over 25 MB:** We recommend uploading your MP4 to a **GitHub Release Asset**, **YouTube (Unlisted)**, or **Loom**, and linking it in the [Demo Video section](#-demo--screenshots) above. GitHub blocks direct Git pushes for individual files over 100 MB and warns at 50 MB unless Git LFS is configured.

---

## ⚠️ Known Limitations & Future Roadmap

- **External Feed Rate Limits:** Live RSS ingestion depends on third-party publisher feeds. If an external publisher is temporarily down, the pipeline skips that source and continues.
- **WebSocket Streaming:** Currently, the feed updates upon page load or when the "Run Intelligence Scan" button is clicked. Future iterations can add native WebSockets for instant live pushes.
- **User Personalization:** The "For You" channel currently showcases all high-gravity verified stories. Future versions could include user-authenticated bookmarking and custom tag tracking.

---

## 📄 License

MIT License. Built for advanced AI technology intelligence exploration.
