CREATE TABLE IF NOT EXISTS "feed" (
  "id" INTEGER PRIMARY KEY,
  "url" TEXT,
  "uuid" TEXT,
  "status" TEXT,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX feed_url ON feed(url);

# test data
# insert into feed(url) values('https://www.npr.org/rss/podcast.php?id=510289');