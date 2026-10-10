import os
import json
import sqlite3
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "music_player.db")
DIST_DIR = os.path.join(BASE_DIR, "dist")
DATA_DIR = os.path.join(DIST_DIR, "data")

def build():
    print("Building static site bundle for GitHub Pages...")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    if not os.path.exists(DB_PATH):
        print("Database not found, generating from schema & seeds...")
        from seed_database import seed_database
        seed_database()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Export Genres
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
    genres = [dict(r) for r in cursor.fetchall()]
    with open(os.path.join(DATA_DIR, "genres.json"), "w", encoding="utf-8") as f:
        json.dump(genres, f, indent=2)
    print(f"Exported {len(genres)} genres to data/genres.json")

    # 2. Export Top 50 per genre
    all_top_songs = []
    for g in genres:
        gid = g["genre_id"]
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
        """, (gid,))
        songs = [dict(r) for r in cursor.fetchall()]
        all_top_songs.extend(songs)
        with open(os.path.join(DATA_DIR, f"genre_{gid}.json"), "w", encoding="utf-8") as f:
            json.dump(songs, f, indent=2)

    with open(os.path.join(DATA_DIR, "all_songs.json"), "w", encoding="utf-8") as f:
        json.dump(all_top_songs, f, indent=2)
    print(f"Exported {len(all_top_songs)} songs to data/all_songs.json")

    # 3. Copy static assets to dist/
    static_src = os.path.join(BASE_DIR, "static")
    for item in os.listdir(static_src):
        s_item = os.path.join(static_src, item)
        d_item = os.path.join(DIST_DIR, item)
        if os.path.isfile(s_item):
            shutil.copy2(s_item, d_item)
        elif os.path.isdir(s_item):
            shutil.copytree(s_item, d_item)

    # 4. Create .nojekyll for GitHub Pages
    with open(os.path.join(DIST_DIR, ".nojekyll"), "w") as f:
        f.write("")

    conn.close()
    print("Static build complete in 'dist/' directory!")

if __name__ == "__main__":
    build()
