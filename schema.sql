-- ============================================================================
-- Music Player Database Schema
-- Supports Top 50 Songs per Genre, Artists, Albums, Playlists & History
-- Compatible with SQLite, PostgreSQL, and MySQL (ANSI SQL standard)
-- ============================================================================

-- 1. GENRES
CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ARTISTS
CREATE TABLE IF NOT EXISTS artists (
    artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    bio TEXT,
    country VARCHAR(50),
    monthly_listeners BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ALBUMS
CREATE TABLE IF NOT EXISTS albums (
    album_id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    release_year INTEGER,
    cover_image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE
);

-- 4. SONGS (TRACKS)
CREATE TABLE IF NOT EXISTS songs (
    song_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(150) NOT NULL,
    primary_artist_id INTEGER NOT NULL,
    album_id INTEGER,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    play_count BIGINT DEFAULT 0 CHECK (play_count >= 0),
    popularity_score REAL DEFAULT 0.0 CHECK (popularity_score BETWEEN 0.0 AND 100.0),
    release_date DATE,
    file_path VARCHAR(255),
    audio_format VARCHAR(10) DEFAULT 'mp3',
    bitrate_kbps INTEGER DEFAULT 320,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES albums(album_id) ON DELETE SET NULL
);

-- 5. SONG_GENRES (Many-to-Many to support songs with primary & subgenres)
CREATE TABLE IF NOT EXISTS song_genres (
    song_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT 1,
    PRIMARY KEY (song_id, genre_id),
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE
);

-- 6. USERS
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. PLAYLISTS
CREATE TABLE IF NOT EXISTS playlists (
    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 8. PLAYLIST_SONGS
CREATE TABLE IF NOT EXISTS playlist_songs (
    playlist_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
);

-- 9. USER_FAVORITES (Liked Songs)
CREATE TABLE IF NOT EXISTS user_favorites (
    user_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, song_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
);

-- 10. LISTENING_HISTORY (Playback logs for recommendations and analytics)
CREATE TABLE IF NOT EXISTS listening_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_played_seconds INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_songs_popularity ON songs (popularity_score DESC);
CREATE INDEX IF NOT EXISTS idx_songs_play_count ON songs (play_count DESC);
CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs (primary_artist_id);
CREATE INDEX IF NOT EXISTS idx_song_genres_genre ON song_genres (genre_id);
CREATE INDEX IF NOT EXISTS idx_listening_history_user ON listening_history (user_id, played_at DESC);

-- ============================================================================
-- VIEWS: TOP 50 SONGS BY GENRE & GLOBAL CHARTS
-- ============================================================================

-- View: Computes dynamic rank within each genre
CREATE VIEW IF NOT EXISTS vw_genre_song_rankings AS
SELECT 
    g.genre_id,
    g.name AS genre_name,
    s.song_id,
    s.title AS song_title,
    a.artist_id,
    a.name AS artist_name,
    al.title AS album_title,
    s.duration_seconds,
    s.play_count,
    s.popularity_score,
    DENSE_RANK() OVER (
        PARTITION BY g.genre_id 
        ORDER BY s.popularity_score DESC, s.play_count DESC, s.song_id ASC
    ) AS genre_rank
FROM genres g
JOIN song_genres sg ON g.genre_id = sg.genre_id
JOIN songs s ON sg.song_id = s.song_id
JOIN artists a ON s.primary_artist_id = a.artist_id
LEFT JOIN albums al ON s.album_id = al.album_id;

-- View: Filters directly to Top 50 Songs of Every Genre
CREATE VIEW IF NOT EXISTS vw_top_50_by_genre AS
SELECT 
    genre_id,
    genre_name,
    genre_rank,
    song_id,
    song_title,
    artist_name,
    album_title,
    duration_seconds,
    play_count,
    popularity_score
FROM vw_genre_song_rankings
WHERE genre_rank <= 50;
