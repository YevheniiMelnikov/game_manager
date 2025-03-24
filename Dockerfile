FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc libpq-dev curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv pip install --system .

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["uvicorn", "game_management.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
