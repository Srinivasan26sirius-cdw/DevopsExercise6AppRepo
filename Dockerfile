# ---------- Stage 1: Builder ----------
FROM python:3.11 AS builder

WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies into user directory
RUN pip install --user --no-cache-dir -r requirements.txt


# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim

WORKDIR /app

# Install minimal runtime tools for debugging + health checks
# curl helps test Loki connectivity inside pod
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local

# Add local bin to PATH so uvicorn works
ENV PATH=/root/.local/bin:$PATH

# Optional environment variable for logger
ENV ENV=prod

# Copy application source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]