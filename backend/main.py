import json
import os
from threading import Thread

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

MODEL_ID = os.getenv("MODEL_ID", "tiiuae/Falcon3-1B-Instruct")

# MPS = Apple Silicon GPU, CUDA = Nvidia, CPU = fallback
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tokenizer: AutoTokenizer = None
model: AutoModelForCausalLM = None


@app.on_event("startup")
async def load_model():
    global tokenizer, model
    print(f"Loading {MODEL_ID} on {DEVICE}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
    ).to(DEVICE)
    model.eval()
    print("Model ready.")


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.post("/chat")
async def chat(req: ChatRequest):
    messages = req.history + [{"role": "user", "content": req.message}]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    generation_kwargs = {
        **inputs,
        "streamer": streamer,
        "max_new_tokens": 512,
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
    }

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    def stream():
        for token in streamer:
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok", "device": DEVICE, "model": MODEL_ID}
