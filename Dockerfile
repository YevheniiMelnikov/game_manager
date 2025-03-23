FROM python:3.13-slim

ENV APP_HOME=/app
ENV PYTHONPATH=$APP_HOME
ENV TZ=Europe/Kyiv

ENV POETRY_VERSION=1.5.1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       python3-dev \
       libpq-dev \
       curl \
       git \
       postgresql-client \
       redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv uvicorn \
    && curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR $APP_HOME

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY . .

RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["uvicorn", "game_management.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
