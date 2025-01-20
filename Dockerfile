FROM python:3.9.6-alpine3.14

WORKDIR /app

COPY . .
RUN apk add --no-cache gcc libffi-dev musl-dev ffmpeg aria2 && pip install --no-cache-dir -r requirements.txt
RUN pip install yt_dlp -U

CMD gunicorn app:app & python3 main.py

