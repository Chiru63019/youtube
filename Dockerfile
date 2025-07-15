FROM python:3.11-slim

WORKDIR /app

COPY . .

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    ffmpeg \
    aria2 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install yt_dlp -U

CMD gunicorn app:app & python3 main.py
