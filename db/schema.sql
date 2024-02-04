CREATE TABLE IF NOT EXISTS theaters (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    name TEXT,
    img_url TEXT
);

CREATE TABLE IF NOT EXISTS screenings (
    movie_id INTEGER,
    theater_id INTEGER,
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (theater_id) REFERENCES theaters(id),
    PRIMARY KEY (movie_id, theater_id)
);

INSERT OR IGNORE INTO theaters (id, name) VALUES (24, 'UGC Ciné Cité Villeneuve d''Ascq');
INSERT OR IGNORE INTO theaters (id, name) VALUES (25, 'UGC Ciné Cité Lille');
INSERT OR IGNORE INTO theaters (id, name) VALUES (45, 'Le Métropole');
INSERT OR IGNORE INTO theaters (id, name) VALUES (46, 'Le Majestic');
