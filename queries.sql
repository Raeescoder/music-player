-- ============================================================================
-- Music Player Database: Essential Production Queries & Examples
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. GET TOP 50 SONGS OF A SPECIFIC GENRE (e.g., 'Rock', 'Pop', 'Hip-Hop')
-- ----------------------------------------------------------------------------
SELECT 
    genre_rank,
    song_title,
    artist_name,
    album_title,
    duration_seconds,
    play_count,
    popularity_score
FROM vw_top_50_by_genre
WHERE genre_name = 'Rock'
ORDER BY genre_rank ASC;

-- ----------------------------------------------------------------------------
-- 2. GET TOP 10 OVERALL SONGS ACROSS ENTIRE PLATFORM (GLOBAL TOP CHART)
-- ----------------------------------------------------------------------------
SELECT 
    DENSE_RANK() OVER (ORDER BY s.popularity_score DESC, s.play_count DESC) AS global_rank,
    s.title AS song_title,
    a.name AS artist_name,
    g.name AS primary_genre,
    s.play_count,
    s.popularity_score
FROM songs s
JOIN artists a ON s.primary_artist_id = a.artist_id
JOIN song_genres sg ON s.song_id = sg.song_id AND sg.is_primary = 1
JOIN genres g ON sg.genre_id = g.genre_id
ORDER BY global_rank ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- 3. ADD A NEW SONG AND LINK TO A GENRE
-- ----------------------------------------------------------------------------
-- Step A: Insert the song
INSERT INTO songs (title, primary_artist_id, album_id, duration_seconds, play_count, popularity_score, file_path)
VALUES ('New Hit Track', 1, 1, 215, 1200000, 88.5, '/music/pop/new_hit_track.mp3');

-- Step B: Associate with Genre (Genre ID 8 = Pop)
INSERT INTO song_genres (song_id, genre_id, is_primary)
VALUES (last_insert_rowid(), 8, 1);

-- ----------------------------------------------------------------------------
-- 4. SEARCH SONGS BY TITLE, ARTIST, OR GENRE
-- ----------------------------------------------------------------------------
SELECT 
    s.song_id,
    s.title AS song_title,
    a.name AS artist_name,
    al.title AS album_title,
    g.name AS genre_name,
    s.duration_seconds
FROM songs s
JOIN artists a ON s.primary_artist_id = a.artist_id
LEFT JOIN albums al ON s.album_id = al.album_id
JOIN song_genres sg ON s.song_id = sg.song_id
JOIN genres g ON sg.genre_id = g.genre_id
WHERE s.title LIKE '%Love%' OR a.name LIKE '%Love%'
ORDER BY s.popularity_score DESC
LIMIT 20;

-- ----------------------------------------------------------------------------
-- 5. RECORD A PLAY (USER STREAMING A SONG)
-- ----------------------------------------------------------------------------
-- Transaction: update play count and log to listening history
BEGIN TRANSACTION;

UPDATE songs 
SET play_count = play_count + 1 
WHERE song_id = 42;

INSERT INTO listening_history (user_id, song_id, duration_played_seconds, completed)
VALUES (1, 42, 210, 1);

COMMIT;

-- ----------------------------------------------------------------------------
-- 6. GET USER'S RECENTLY PLAYED SONGS WITH DURATION
-- ----------------------------------------------------------------------------
SELECT 
    h.played_at,
    s.title AS song_title,
    a.name AS artist_name,
    h.duration_played_seconds,
    h.completed
FROM listening_history h
JOIN songs s ON h.song_id = s.song_id
JOIN artists a ON s.primary_artist_id = a.artist_id
WHERE h.user_id = 1
ORDER BY h.played_at DESC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- 7. GET ALL SONGS IN A USER'S PLAYLIST IN ORDER
-- ----------------------------------------------------------------------------
SELECT 
    ps.position,
    s.title AS song_title,
    a.name AS artist_name,
    s.duration_seconds,
    s.file_path
FROM playlist_songs ps
JOIN songs s ON ps.song_id = s.song_id
JOIN artists a ON s.primary_artist_id = a.artist_id
WHERE ps.playlist_id = 1
ORDER BY ps.position ASC;

-- ----------------------------------------------------------------------------
-- 8. GENRE BREAKDOWN SUMMARY (SONG COUNT & AVERAGE POPULARITY)
-- ----------------------------------------------------------------------------
SELECT 
    g.name AS genre_name,
    COUNT(sg.song_id) AS total_songs,
    ROUND(AVG(s.popularity_score), 2) AS avg_popularity,
    SUM(s.play_count) AS total_genre_plays
FROM genres g
JOIN song_genres sg ON g.genre_id = sg.genre_id
JOIN songs s ON sg.song_id = s.song_id
GROUP BY g.genre_id, g.name
ORDER BY total_genre_plays DESC;
