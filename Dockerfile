FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for static and media
RUN mkdir -p staticfiles media

# Collect static files
RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Expose port
EXPOSE 8000

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run gunicorn
CMD ["gunicorn", "fitzone.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--worker-class", "gthread", "--timeout", "60"]
