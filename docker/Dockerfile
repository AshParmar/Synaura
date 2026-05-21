# docker/Dockerfile
# Production Dockerfile for Synaura FastAPI Backend

FROM python:3.11-slim

# ── System dependencies ───────────────────────────────────────────────────────
# libgl1 + libglib2.0-0 are required by OpenCV at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────────
COPY requirements.txt ./
# Install CPU-only torch first to keep image size manageable
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# ── Pre-download Embedding Model ──────────────────────────────────────────────
# Bake the model into the image so Cloud Run doesn't get rate limited on startup
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# ── Application source ────────────────────────────────────────────────────────
COPY . .

# Install local package (setup.py) in editable mode so imports resolve
RUN pip install --no-cache-dir -e .

# ── Runtime configuration ─────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Use 0.0.0.0 so Cloud Run can reach the container
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
