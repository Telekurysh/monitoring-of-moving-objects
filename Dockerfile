FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry via pip
RUN pip install --upgrade pip
RUN pip install poetry

# Copy project files
COPY pyproject.toml /app/
COPY README.md /app/
COPY src /app/src
COPY templates /app/templates

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.sensor_track_pro.api.main:app", "--host", "0.0.0.0", "--port", "8000"]