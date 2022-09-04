# backpod service for GCP cloud run

This is an attempt to implemete a backpod service using GCP cloud run. A live version is at https://backpod.podcastdrill.com

Cloud Storage, PubSub, Firestore and Cloud Run are used.

Generated feed is stored in Cloud Storage and Cached by CloudFlare.

There are two servcies involved:

1. web service
  * external API that takes podcast feed url to scrape and publishs a message to be picked up by scraper service.
  * to test service:
    * `curl -v -H "Content-Type: application/json" -d '{"url": "https://www.npr.org/rss/podcast.php?id=510289"}' https://backpod-web-5nkbg7zlqa-uw.a.run.app/feeds`
1. scraper service
  * internal service subscribe to pubsub message and does the scraping work.

# frontend

* cloudflare DNS, hosted on Hetzner.
