FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED="true" \
    PROJECT_ID=backpod \
    TOPIC_ID=rss-feed \
    ALLOWED_ORIGIN=https://backpod.podcastdrill.com
    FEED_DOMAIN=https://feeds.podcastdrill.com

COPY . .

# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
CMD ["gunicorn", "-c", "python:config.gunicorn", "main:app"]
