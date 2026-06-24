FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-dev libjpeg-dev libjpeg62-turbo-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libopenjp2-7-dev libwebp-dev \
    libharfbuzz-dev libfribidi-dev pkg-config git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first to leverage layer caching
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel && \
    pip install --prefer-binary -r requirements.txt

# Copy project files
COPY . /app/

# Create unprivileged user
RUN useradd --create-home --shell /bin/bash appuser || true
RUN chown -R appuser:appuser /app
USER appuser

ENV DJANGO_SETTINGS_MODULE=fitzone.settings

# Entrypoint will collect static files, run migrations, then start gunicorn
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE ${PORT}

ENTRYPOINT ["/app/entrypoint.sh"]
