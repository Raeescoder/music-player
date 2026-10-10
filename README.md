# Music Player Database & Web Player (Top 50 Songs per Genre)

A full-stack music player application and relational SQL database supporting genres, artists, albums, songs, playlists, user listening history, and dynamic **Top 50 charts for every genre** with real studio audio streaming.

---

## 🚀 Live Deployment via GitHub Actions (GitHub Pages)

This project includes an automated GitHub Actions CI/CD workflow ([`.github/workflows/deploy.yml`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/.github/workflows/deploy.yml)) that builds the database and publishes the entire music player live to **GitHub Pages** for free!

### Step 1: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com/new) and create a new repository (e.g., `music-player`).
2. Make it **Public** (or Private with GitHub Pro).

### Step 2: Push This Code to GitHub
Open your terminal in this directory (`C:\Users\SM\.gemini\antigravity\scratch\music_player_db`) and run:
```bash
git init
git add .
git commit -m "Initial commit: Music Player with Top 50 SQL Database & GitHub Actions deploy"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
git push -u origin main
```

### Step 3: Enable GitHub Pages with Actions
1. On your GitHub repository page, click **Settings** (⚙️).
2. In the left sidebar, click **Pages**.
3. Under **Build and deployment** > **Source**, select **GitHub Actions**.

### Step 4: Your Site is Live!
The GitHub Action will immediately run:
1. Sets up Python.
2. Runs `build_static.py` to compile the SQLite database into static API endpoints.
3. Deploys the web player to GitHub Pages.

Your live music player link will be available at:
👉 **`https://<YOUR_USERNAME>.github.io/<YOUR_REPOSITORY>/`**

---

## 📁 Project Structure

| File / Folder | Description |
|---|---|
| [`.github/workflows/deploy.yml`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/.github/workflows/deploy.yml) | GitHub Actions workflow that automatically builds and deploys to GitHub Pages on every push. |
| [`build_static.py`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/build_static.py) | Generates static JSON data bundles from the SQLite database for serverless production hosting. |
| [`static/index.html`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/static/index.html) | Modern dark-theme music player with real audio previews, album artwork, and dual-mode API support. |
| [`app.py`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/app.py) | Flask REST backend for running locally or on container hosts (Render, Railway, Fly.io). |
| [`schema.sql`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/schema.sql) | DDL table definitions, foreign keys, indexes, and `vw_top_50_by_genre` ranking view. |
| [`seed_data.sql`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/seed_data.sql) | Standalone SQL inserts for 500 songs (50 per genre across 10 genres) and 100 artists. |
| [`seed_database.py`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/seed_database.py) | Python generator to populate the SQLite database. |
| [`queries.sql`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/queries.sql) | Production SQL query examples. |
| [`music_player.db`](file:///C:/Users/SM/.gemini/antigravity/scratch/music_player_db/music_player.db) | Seeded SQLite database. |

---

## 🗄️ Database Schema Design

### Core Tables
1. **`genres`**: Stores musical genres (`Pop`, `Rock`, `Hip-Hop`, `Electronic / Dance`, `R&B / Soul`, `Jazz`, `Classical`, `Country`, `Latin`, `Metal`).
2. **`artists`**: Artist names, biographies, origins, and monthly listeners.
3. **`albums`**: Discography linked to artists with release year and artwork URLs.
4. **`songs`**: Track titles, audio duration, play counts, popularity scores (0.0 to 100.0), release dates, and audio file paths.
5. **`song_genres`**: Many-to-many relationship supporting primary and secondary genres.
6. **`users`**: User profiles with authentication metadata.
7. **`playlists` & `playlist_songs`**: User playlists with custom ordered track sequences.
8. **`user_favorites`**: Liked songs / bookmarks.
9. **`listening_history`**: Playback logs tracking completion rate, timestamp, and duration listened.

---

## 🏆 How Top 50 Songs Per Genre Works

The database utilizes SQL window functions (`DENSE_RANK()`) partitioned by genre to automatically rank songs by popularity and play count.

### The View: `vw_top_50_by_genre`
```sql
CREATE VIEW vw_top_50_by_genre AS
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
FROM (
    SELECT 
        g.genre_id,
        g.name AS genre_name,
        s.song_id,
        s.title AS song_title,
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
    LEFT JOIN albums al ON s.album_id = al.album_id
)
WHERE genre_rank <= 50;
```

---

## 💻 Local Development

Run the Flask server locally:
```powershell
python app.py
```
Open **http://127.0.0.1:5000** in your browser.
