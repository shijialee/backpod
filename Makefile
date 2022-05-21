.PHONY: dev.create_feed
dev.create_feed:
	curl -v -H "Content-Type: application/json" -d '{"url": "https://google.com"}' localhost:8888/feeds

.PHONY: dev.get_feed
dev.get_feed:
	curl -v localhost:8888/feeds/FEED_ID
