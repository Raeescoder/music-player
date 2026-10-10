import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "music_player.db")

def run_tests():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("=================================================================")
    print("MUSIC PLAYER DATABASE - VERIFICATION & TOP 50 TEST")
    print("=================================================================")

    # 1. Total Counts
    cursor.execute("SELECT COUNT(*) FROM genres")
    genre_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM songs")
    song_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM artists")
    artist_count = cursor.fetchone()[0]

    print(f"Total Genres  : {genre_count}")
    print(f"Total Artists : {artist_count}")
    print(f"Total Songs   : {song_count}")
    print("-----------------------------------------------------------------")

    # 2. Test Top 5 for Rock and Pop
    for target_genre in ["Rock", "Pop", "Hip-Hop"]:
        print(f"\n[TOP 5 SONGS IN GENRE: '{target_genre}']")
        cursor.execute("""
            SELECT genre_rank, song_title, artist_name, play_count, popularity_score
            FROM vw_top_50_by_genre
            WHERE genre_name = ?
            ORDER BY genre_rank ASC
            LIMIT 5;
        """, (target_genre,))
        rows = cursor.fetchall()
        for r in rows:
            print(f"  #{r[0]:2d} | {r[1]:<25} | {r[2]:<20} | Plays: {r[3]:,d} | Pop: {r[4]}")

    print("\n-----------------------------------------------------------------")
    print("Genre Play Distribution:")
    cursor.execute("""
        SELECT 
            g.name,
            COUNT(sg.song_id) as songs,
            SUM(s.play_count) as total_plays
        FROM genres g
        JOIN song_genres sg ON g.genre_id = sg.genre_id
        JOIN songs s ON sg.song_id = s.song_id
        GROUP BY g.genre_id
        ORDER BY total_plays DESC;
    """)
    for g, sc, tp in cursor.fetchall():
        print(f"  {g:<20}: {sc} songs | {tp:,d} total plays")

    conn.close()

if __name__ == "__main__":
    run_tests()
