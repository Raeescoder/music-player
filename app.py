import os
import sqlite3
import json
import urllib.request
import urllib.parse
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")
DB_PATH = os.path.join(os.path.dirname(__file__), "music_player.db")
PREVIEW_CACHE = {}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/genres", methods=["GET"])
def get_genres():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            g.genre_id,
            g.name,
            g.description,
            COUNT(sg.song_id) AS total_songs,
            COALESCE(SUM(s.play_count), 0) AS total_plays
        FROM genres g
        LEFT JOIN song_genres sg ON g.genre_id = sg.genre_id
        LEFT JOIN songs s ON sg.song_id = s.song_id
        GROUP BY g.genre_id
        ORDER BY g.name ASC
    """)
    rows = cursor.fetchall()
    genres = [dict(row) for row in rows]
    conn.close()
    return jsonify(genres)

@app.route("/api/genres/<int:genre_id>/top50", methods=["GET"])
def get_genre_top_50(genre_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
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
        FROM vw_top_50_by_genre
        WHERE genre_id = ?
        ORDER BY genre_rank ASC
    """, (genre_id,))
    rows = cursor.fetchall()
    songs = [dict(row) for row in rows]
    conn.close()
    return jsonify(songs)

@app.route("/api/preview", methods=["GET"])
def get_preview():
    title = request.args.get("title", "").strip()
    artist = request.args.get("artist", "").strip()
    cache_key = f"{artist}:{title}".lower()

    if cache_key in PREVIEW_CACHE:
        return jsonify(PREVIEW_CACHE[cache_key])

    try:
        query = urllib.parse.quote(f"{artist} {title}")
        url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("results"):
                res = data["results"][0]
                result = {
                    "preview_url": res.get("previewUrl"),
                    "artwork_url": res.get("artworkUrl100"),
                    "track_name": res.get("trackName"),
                    "artist_name": res.get("artistName")
                }
                PREVIEW_CACHE[cache_key] = result
                return jsonify(result)
    except Exception:
        pass

    fallback = {"preview_url": None, "artwork_url": None}
    PREVIEW_CACHE[cache_key] = fallback
    return jsonify(fallback)

@app.route("/api/search", methods=["GET"])
def search_songs():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    conn = get_db()
    cursor = conn.cursor()
    pattern = f"%{query}%"
    cursor.execute("""
        SELECT 
            s.song_id,
            s.title AS song_title,
            a.name AS artist_name,
            COALESCE(al.title, 'Single') AS album_title,
            g.name AS genre_name,
            s.duration_seconds,
            s.play_count,
            s.popularity_score
        FROM songs s
        JOIN artists a ON s.primary_artist_id = a.artist_id
        LEFT JOIN albums al ON s.album_id = al.album_id
        JOIN song_genres sg ON s.song_id = sg.song_id
        JOIN genres g ON sg.genre_id = g.genre_id
        WHERE s.title LIKE ? OR a.name LIKE ? OR g.name LIKE ?
        ORDER BY s.popularity_score DESC
        LIMIT 30
    """, (pattern, pattern, pattern))
    rows = cursor.fetchall()
    songs = [dict(row) for row in rows]
    conn.close()
    return jsonify(songs)

@app.route("/api/songs", methods=["POST"])
def add_song():
    data = request.json or {}
    title = data.get("title", "").strip()
    artist_name = data.get("artist_name", "").strip()
    genre_id = data.get("genre_id")
    duration = int(data.get("duration_seconds", 200))
    popularity = float(data.get("popularity_score", 85.0))
    play_count = int(data.get("play_count", 1000000))
    album_title = data.get("album_title", "").strip() or f"{title} (Single)"

    if not title or not artist_name or not genre_id:
        return jsonify({"error": "Title, artist, and genre are required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Find or create artist
    cursor.execute("SELECT artist_id FROM artists WHERE name = ?", (artist_name,))
    artist_row = cursor.fetchone()
    if artist_row:
        artist_id = artist_row["artist_id"]
    else:
        cursor.execute("INSERT INTO artists (name, bio, monthly_listeners) VALUES (?, ?, ?)",
                       (artist_name, f"Artist {artist_name}", 1000000))
        artist_id = cursor.lastrowid

    # Find or create album
    cursor.execute("SELECT album_id FROM albums WHERE title = ? AND artist_id = ?", (album_title, artist_id))
    album_row = cursor.fetchone()
    if album_row:
        album_id = album_row["album_id"]
    else:
        cursor.execute("INSERT INTO albums (artist_id, title, release_year) VALUES (?, ?, 2024)",
                       (artist_id, album_title))
        album_id = cursor.lastrowid

    # Insert song
    cursor.execute("""
        INSERT INTO songs (title, primary_artist_id, album_id, duration_seconds, play_count, popularity_score, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, artist_id, album_id, duration, play_count, popularity, f"/music/{title.lower().replace(' ', '_')}.mp3"))
    song_id = cursor.lastrowid

    # Associate with genre
    cursor.execute("INSERT INTO song_genres (song_id, genre_id, is_primary) VALUES (?, ?, 1)", (song_id, genre_id))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "song_id": song_id, "message": "Song added successfully!"}), 201

@app.route("/api/play/<int:song_id>", methods=["POST"])
def record_play(song_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE songs SET play_count = play_count + 1 WHERE song_id = ?", (song_id,))
    cursor.execute("""
        INSERT INTO listening_history (user_id, song_id, duration_played_seconds, completed)
        VALUES (1, ?, 180, 1)
    """, (song_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "recorded"})

@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT song_id FROM user_favorites WHERE user_id = 1")
    favs = [row["song_id"] for row in cursor.fetchall()]
    conn.close()
    return jsonify(favs)

@app.route("/api/favorites/toggle", methods=["POST"])
def toggle_favorite():
    data = request.json or {}
    song_id = data.get("song_id")
    if not song_id:
        return jsonify({"error": "song_id required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM user_favorites WHERE user_id = 1 AND song_id = ?", (song_id,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute("DELETE FROM user_favorites WHERE user_id = 1 AND song_id = ?", (song_id,))
        liked = False
    else:
        cursor.execute("INSERT INTO user_favorites (user_id, song_id) VALUES (1, ?)", (song_id,))
        liked = True

    conn.commit()
    conn.close()
    return jsonify({"liked": liked, "song_id": song_id})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
