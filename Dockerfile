FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc libpq-dev curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv pip install --system ".[dev]"

COPY . .

RUN chmod +x /app/entrypoint.sh

RUN mypy --install-types --non-interactive || true

ENTRYPOINT ["/app/entrypoint.sh"]
