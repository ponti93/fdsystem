# =========================
# Stage 1: Build React frontend
# =========================
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# Install ALL dependencies (need devDeps like react-scripts for build)
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY frontend/ . 

# Build React app (output in /app/frontend/build)
RUN npm run build

# =========================
# Stage 2: Python backend
# =========================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for ML libs, Postgres, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Copy built frontend into backend static directory
COPY --from=frontend-build /app/frontend/build ./static

# Create necessary directories
RUN mkdir -p models data

# Env vars
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
