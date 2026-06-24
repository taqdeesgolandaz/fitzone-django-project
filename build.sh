#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip setuptools wheel
# Install system libraries required to build Pillow on Linux (Debian/Ubuntu)
if command -v apt-get >/dev/null 2>&1; then
	apt-get update && apt-get install -y --no-install-recommends \
		build-essential \
		python3-dev \
		libjpeg-dev \
		libjpeg62-turbo-dev \
		zlib1g-dev \
		libfreetype6-dev \
		liblcms2-dev \
		libopenjp2-7-dev \
		libwebp-dev \
		libharfbuzz-dev \
		libfribidi-dev \
		pkg-config \
		&& rm -rf /var/lib/apt/lists/*
fi

pip install --prefer-binary -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
