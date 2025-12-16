FROM python:3.11-slim

# Env vars to protect against common python issues in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies (ffmpeg is crucial for your STT)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Copy project definition
COPY pyproject.toml .
# Copy source code
COPY src/ src/
COPY run.py .
COPY README.md .

# Install dependencies (including the project itself in editable mode if needed, or just deps)
# Installing '.' processes pyproject.toml dependencies
RUN pip install .

# Prepare data directories and permissions
RUN mkdir -p /app/data /app/models && \
    chown -R appuser:appuser /app

USER appuser

CMD ["python", "run.py"]

