# Build stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (including dev dependencies)
RUN uv sync --frozen

# Final stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src ./src
COPY tests ./tests
COPY pyproject.toml ./

# Set Python path
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
