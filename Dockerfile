FROM python:3.13-slim

ENV UV_CACHE_DIR=/root/.cache/uv
ARG INSTALL_DEV=false

RUN apt-get update && apt-get install -y gcc libpq-dev curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN if [ "$INSTALL_DEV" = "true" ]; then \
      uv pip install --system ".[dev]"; \
    else \
      uv pip install --system .; \
    fi

COPY . .

RUN chmod +x /app/entrypoint.sh && \
    mypy --install-types --non-interactive || true

ENTRYPOINT ["/app/entrypoint.sh"]
