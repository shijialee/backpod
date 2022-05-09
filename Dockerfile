FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-warn-script-location --user -r requirements.txt

ENV PYTHONUNBUFFERED="true" \
    PATH=$PATH:/root/.local/bin \
    FEED_BUCKET_NAME=us-backpod-feed

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
