# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into virtual environment
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .



# -------- Stage 2: Runtime --------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY --from=builder /app /app

# Activate venv path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "user_app/main.py"]
