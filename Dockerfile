FROM python:3.13-slim

ENV APP_HOME=/app
ENV PYTHONPATH=$APP_HOME
ENV TZ=Europe/Kyiv

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       python3-dev \
       curl \
       git \
       postgresql-client \
       redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR $APP_HOME

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system uvicorn

COPY . .

RUN mkdir -p /app/logs

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uvicorn", "game_management.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
