#!/bin/bash

echo "Starting build..."
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
echo "Build completed!"
