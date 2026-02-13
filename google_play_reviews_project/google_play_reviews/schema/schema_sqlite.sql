PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS apps (
  app_id TEXT PRIMARY KEY,
  platform TEXT NOT NULL DEFAULT 'google_play',
  app_name TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reviews (
  review_uid TEXT PRIMARY KEY,
  app_id TEXT NOT NULL,
  user_name TEXT,
  rating INTEGER,
  review_text TEXT NOT NULL,
  review_date TEXT,
  thumbs_up INTEGER,
  app_version TEXT,
  sort_mode TEXT,
  scrape_time TEXT,
  run_id TEXT,
  ingested_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (app_id) REFERENCES apps(app_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_app_date
ON reviews(app_id, review_date);

CREATE INDEX IF NOT EXISTS idx_reviews_app_rating
ON reviews(app_id, rating);

CREATE INDEX IF NOT EXISTS idx_reviews_app_version
ON reviews(app_id, app_version);
