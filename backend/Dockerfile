# Used for HuggingFace Spaces deployment (Linux + Nvidia T4)
# Not used for local Mac development — run directly with uvicorn
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MODEL_ID=tiiuae/Falcon3-1B-Instruct
ENV PORT=7860

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
