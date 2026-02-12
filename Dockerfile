# === Builder stage ===
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

# Python and UV optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# First we copy only the dependency files (layer caching)
COPY pyproject.toml uv.lock ./

# Synchronizing dependencies.
# --no-install-project: We don’t put the bot code itself in .venv (we’ll save space)
# --frozen: ensures that we only use the versions in the lock file
RUN uv sync --frozen --no-dev --no-install-project

# === Runtime stage ===
FROM python:3.14-slim-bookworm AS runtime

# These variables are also needed at startup
# We write the path to the venv binaries at the beginning of the system
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Security: creating a system user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs
# Copying the created environment from the builder.
# We immediately set our user as the owner.
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copying the source code
COPY --chown=appuser:appuser . .

# Switching to the user
USER appuser

# Now 'python' will be automatically taken from /app/.venv/bin/python
CMD ["python", "src/main.py"]