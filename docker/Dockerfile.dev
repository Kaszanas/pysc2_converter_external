# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=0

# Install system dependencies if necessary (e.g. for pygame)
# PyGame often needs some system libraries
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install all dependencies including the dev group
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-groups --no-install-project

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tests/ ./tests/

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-groups

# Add the virtual environment to PATH so commands like 'pytest' work natively
ENV PATH="/app/.venv/bin:$PATH"

# Keep the container running or drop to shell
CMD ["/bin/bash"]
