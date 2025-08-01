CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tags TEXT NOT NULL,
    image_path TEXT NOT NULL,
    title TEXT NOT NULL,
    claimed INTEGER DEFAULT 0,
    claimed_by TEXT
);