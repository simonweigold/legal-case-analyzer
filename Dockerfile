# Multi-stage build: frontend (Vite + Bun) -> backend (Python FastAPI)
# Final image contains built static assets served by FastAPI and Python dependencies only.

# --- Frontend build stage ---
FROM oven/bun:1.1.21 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile
COPY frontend/ ./
RUN bun run build

# --- Backend build stage ---
FROM python:3.11-slim AS backend-base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
# System deps (if needed later). Keeping minimal.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application source (backend + frontend dist)
COPY backend/ ./backend/
# Copy only the built dist from the frontend stage
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Create non-root user for security
RUN useradd -m analyzer && chown -R analyzer:analyzer /app
USER analyzer

# Expose backend port
EXPOSE 8000

# Environment variables (override at runtime as needed)
ENV OPENAI_API_KEY="" \
    DATABASE_URL="sqlite+aiosqlite:///./legal_analyzer.db" \
    PYTHONPATH="/app/backend"

# Entrypoint script sets working dir and launches uvicorn
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh

WORKDIR /app/backend

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
