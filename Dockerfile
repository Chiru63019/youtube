FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt update && \
    apt install -y gcc libffi-dev ffmpeg aria2 build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade yt_dlp

CMD gunicorn app:app & python3 main.py
