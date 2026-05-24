# Falcon 3 Chat

A minimal streaming chat application built on [Falcon3-1B-Instruct](https://huggingface.co/tiiuae/Falcon3-1B-Instruct) by the Technology Innovation Institute (TII).

**Stack:** FastAPI · HuggingFace Transformers · Next.js 16 · Tailwind CSS  
**Inference:** Runs the model locally — MPS on Apple Silicon, CUDA on Nvidia, CPU fallback  
**Streaming:** Server-Sent Events (SSE) with `TextIteratorStreamer` for real-time token output

---

## Run locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- ~2 GB free disk (model weights download on first run)

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

First startup downloads Falcon3-1B-Instruct (~2 GB) to `~/.cache/huggingface/`.  
Subsequent starts load from cache — takes ~10 seconds on M2 Pro.

Backend runs at **http://localhost:8000**.  
Health check: `curl http://localhost:8000/health`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**.

---

## How it works

```
Browser  →  POST /chat  →  FastAPI  →  Falcon3-1B (MPS/CUDA/CPU)
                                            ↓ token-by-token via TextIteratorStreamer
Browser  ←  SSE stream  ←  FastAPI  ←────────────────────────────
```

1. Frontend sends the full conversation history + new user message as JSON.
2. FastAPI applies Falcon's chat template (`tokenizer.apply_chat_template`), tokenizes, and starts generation in a background thread.
3. `TextIteratorStreamer` yields each token as it's decoded — no waiting for the full response.
4. Each token is sent as an SSE frame: `data: {"token": "..."}\n\n`.
5. Frontend reads the SSE stream via `fetch` + `ReadableStream`, appending tokens to the last message in state.

---

## Deploy

### Backend → HuggingFace Spaces

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space) — SDK: **Docker**, Hardware: **T4 small** (free)
2. Push the `backend/` folder contents to the Space repo:
   ```bash
   git clone https://huggingface.co/spaces/<your-username>/<space-name>
   cp backend/* <space-name>/
   cd <space-name> && git add . && git commit -m "init" && git push
   ```
3. Space URL will be `https://<your-username>-<space-name>.hf.space`

### Frontend → Vercel

1. Push this repo to GitHub.
2. Import the repo at [vercel.com/new](https://vercel.com/new) — set root to `frontend/`.
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://<your-hf-space-url>`
4. Deploy.

---

## Project structure

```
tii-falcon/
├── backend/
│   ├── main.py           # FastAPI app — model loading, /chat SSE endpoint
│   ├── requirements.txt
│   └── Dockerfile        # For HuggingFace Spaces (Linux + T4 GPU)
├── frontend/
│   ├── app/
│   │   ├── page.tsx      # Chat UI — streaming, message history, auto-resize input
│   │   └── layout.tsx
│   └── .env.local        # NEXT_PUBLIC_API_URL (local dev)
└── README.md
```
