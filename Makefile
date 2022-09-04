.PHONY: prod.sync_frontend
prod.sync_frontend:
	rsync -cvrlOD -e 'ssh' static/ het_dev:/var/www/backpod.podcastdrill.com/public

.PHONY: dev.create_feed
dev.create_feed:
	curl -v -H "Content-Type: application/json" -d '{"url": "https://google.com"}' localhost:8888/feeds

.PHONY: dev.get_feed
dev.get_feed:
	curl -v localhost:8888/feeds/FEED_ID

.PHONY: prod.create_feed
prod.create_feed:
	curl -v -H "Content-Type: application/json" -d '{"url": "https://www.npr.org/rss/podcast.php?id=510289"}' https://backpod-web-5nkbg7zlqa-uw.a.run.app/feeds

.PHONY: prod.get_feed
prod.get_feed:
	curl -v https://backpod-web-5nkbg7zlqa-uw.a.run.app/feeds/FEED_ID
