import sqlite3
import random
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "music_player.db")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")
SQL_DUMP_FILE = os.path.join(os.path.dirname(__file__), "seed_data.sql")

GENRE_CATALOG = {
    "Pop": {
        "artists": [
            "Taylor Swift", "The Weeknd", "Dua Lipa", "Harry Styles", "Ariana Grande",
            "Billie Eilish", "Ed Sheeran", "Bruno Mars", "Olivia Rodrigo", "Justin Bieber"
        ],
        "keywords": [
            "Midnight", "Levitating", "Blinding Lights", "As It Was", "Golden Hour",
            "Cruel Summer", "Watermelon Sugar", "Anti-Hero", "Save Your Tears", "Bad Guy",
            "Starboy", "Vampire", "Deja Vu", "Peaches", "Positions", "Lover", "Cardigan",
            "Shivers", "Don't Start Now", "Stay", "Espresso", "Flowers", "Dance The Night",
            "Physical", "Good 4 U", "Dynamite", "Butter", "Greedy", "Houdini", "Feather",
            "Treasure", "Uptown Funk", "24K Magic", "Blank Space", "Style", "Shake It Off",
            "Paint The Town Red", "Say So", "Kiss Me More", "Attention", "We Don't Talk Anymore",
            "Shape of You", "Perfect", "Thinking Out Loud", "Circles", "Sunflower", "Ghost",
            "Happier Than Ever", "Ocean Eyes", "Lovely"
        ]
    },
    "Rock": {
        "artists": [
            "Queen", "Led Zeppelin", "Pink Floyd", "AC/DC", "Nirvana",
            "The Rolling Stones", "Foo Fighters", "Arctic Monkeys", "Red Hot Chili Peppers", "Linkin Park"
        ],
        "keywords": [
            "Bohemian Rhapsody", "Stairway to Heaven", "Comfortably Numb", "Back in Black", "Smells Like Teen Spirit",
            "Paint It Black", "Everlong", "Do I Wanna Know?", "Californication", "In the End",
            "Highway to Hell", "Under the Bridge", "Kashmir", "Wish You Were Here", "Hotel California",
            "Sweet Child O' Mine", "Come As You Are", "R U Mine?", "The Pretender", "Numb",
            "Don't Stop Me Now", "Whole Lotta Love", "Time", "Thunderstruck", "Lithium",
            "Sympathy for the Devil", "Learn to Fly", "505", "Scar Tissue", "Faint",
            "We Will Rock You", "Black Dog", "Money", "You Shook Me All Night Long", "Heart-Shaped Box",
            "Start Me Up", "Best of You", "Brianstorm", "Can't Stop", "Crawling",
            "Radio Ga Ga", "Immigrant Song", "Another Brick in the Wall", "Hells Bells", "All Apologies",
            "Gimme Shelter", "Monkey Wrench", "Fluorescent Adolescent", "Otherside", "One Step Closer"
        ]
    },
    "Hip-Hop": {
        "artists": [
            "Kendrick Lamar", "Drake", "J. Cole", "Eminem", "Kanye West",
            "Travis Scott", "Nas", "Future", "21 Savage", "Post Malone"
        ],
        "keywords": [
            "HUMBLE.", "God's Plan", "No Role Modelz", "Lose Yourself", "Stronger",
            "SICKO MODE", "N.Y. State of Mind", "Mask Off", "Bank Account", "Rockstar",
            "Alright", "Hotline Bling", "Middle Child", "Stan", "POWER",
            "goosebumps", "The World Is Yours", "Codeine Crazy", "A Lot", "Congratulations",
            "DNA.", "One Dance", "Wet Dreamz", "Without Me", "Flashing Lights",
            "FE!N", "Halftime", "March Madness", "Redrum", "White Iverson",
            "King Kunta", "In My Feelings", "First Person Shooter", "The Real Slim Shady", "Heartless",
            "Antidote", "Memory Lane", "Life Is Good", "Runnin", "Better Now",
            "Money Trees", "Nonstop", "Crooked Smile", "Till I Collapse", "Runaway",
            "TELEKINESIS", "It Ain't Hard to Tell", "Thought It Was a Drought", "Glock in My Lap", "Psycho"
        ]
    },
    "Electronic / Dance": {
        "artists": [
            "Daft Punk", "Calvin Harris", "Avicii", "David Guetta", "Deadmau5",
            "Skrillex", "Tiësto", "Martin Garrix", "Disclosure", "Swedish House Mafia"
        ],
        "keywords": [
            "One More Time", "Summer", "Wake Me Up", "Titanium", "Strobe",
            "Bangarang", "The Business", "Animals", "Latch", "Don't You Worry Child",
            "Harder Better Faster Stronger", "Feel So Close", "Levels", "Memories", "Ghosts 'n' Stuff",
            "Scary Monsters and Nice Sprites", "Adagio for Strings", "Scared to Be Lonely", "Omen", "Save the World",
            "Around the World", "This Is What You Came For", "Waiting for Love", "Play Hard", "I Remember",
            "Where Are Ü Now", "Red Lights", "In the Name of Love", "White Noise", "Greyhound",
            "Get Lucky", "Sweet Nothing", "The Nights", "Without You", "Raise Your Weapon",
            "Kyoto", "Silence", "Tremor", "Help Me Lose My Mind", "Moth To A Flame",
            "Instant Crush", "Outside", "Hey Brother", "She Wolf", "The Veldt",
            "First of the Year", "Secrets", "Byte", "You & Me (Flume Remix)", "One"
        ]
    },
    "R&B / Soul": {
        "artists": [
            "SZA", "Frank Ocean", "Alicia Keys", "Stevie Wonder", "Leon Bridges",
            "Daniel Caesar", "H.E.R.", "Usher", "Lauryn Hill", "Brent Faiyaz"
        ],
        "keywords": [
            "Kill Bill", "Thinkin Bout You", "Fallin'", "Superstition", "Texas Sun",
            "Best Part", "Damage", "Yeah!", "Doo Wop (That Thing)", "Clouded",
            "Snooze", "Pink + White", "If I Ain't Got You", "Isn't She Lovely", "Beyond",
            "Get You", "Focus", "Burn", "Ex-Factor", "Dead Man Walking",
            "Good Days", "Novacane", "No One", "Sir Duke", "River",
            "Japanese Denim", "Hard Place", "U Got It Bad", "Lost Ones", "Trust",
            "Broken Clocks", "Nights", "Empire State of Mind Part II", "I Wish", "Coming Home",
            "Always", "Could've Been", "Confessions Part II", "To Zion", "Gravity",
            "The Weekend", "Lost", "Diary", "Higher Ground", "Bad Bad News",
            "Hold Me Down", "Every Kind of Way", "My Boo", "Tell Him", "Wasting Time"
        ]
    },
    "Jazz": {
        "artists": [
            "Miles Davis", "John Coltrane", "Ella Fitzgerald", "Bill Evans", "Thelonious Monk",
            "Chet Baker", "Herbie Hancock", "Dave Brubeck", "Norah Jones", "Kamasi Washington"
        ],
        "keywords": [
            "So What", "Giant Steps", "Summertime", "Waltz for Debby", "Round Midnight",
            "My Funny Valentine", "Cantaloupe Island", "Take Five", "Don't Know Why", "Truth",
            "Blue in Green", "A Love Supreme Pt 1", "Dream a Little Dream of Me", "Peace Piece", "Straight No Chaser",
            "I Fall in Love Too Easily", "Watermelon Man", "Blue Rondo à la Turk", "Come Away With Me", "Fists of Fury",
            "Freddie Freeloader", "Naima", "Cheek to Cheek", "Autumn Leaves", "Blue Monk",
            "Almost Blue", "Maiden Voyage", "Unsquare Dance", "Sunrise", "Street Fighter Mas",
            "All Blues", "My Favorite Things", "Night and Day", "My Foolish Heart", "Ruby My Dear",
            "Time After Time", "Chameleon", "Pick Up Sticks", "Turn Me On", "The Rhythm Changes",
            "Flamenco Sketches", "Equinox", "Cry Me a River", "Someday My Prince Will Come", "Well You Needn't",
            "Born to Be Blue", "Dolphin Dance", "Everybody's Jumpin'", "The Nearness of You", "Hum-Allah-Hum-Allah"
        ]
    },
    "Classical": {
        "artists": [
            "Ludwig van Beethoven", "Wolfgang Amadeus Mozart", "Johann Sebastian Bach", "Pyotr Ilyich Tchaikovsky", "Frédéric Chopin",
            "Antonio Vivaldi", "Claude Debussy", "Johannes Brahms", "Gustav Mahler", "Ludovico Einaudi"
        ],
        "keywords": [
            "Symphony No. 5 in C Minor", "Eine kleine Nachtmusik", "Air on the G String", "Swan Lake Theme", "Nocturne in E-flat Major",
            "Spring (The Four Seasons)", "Clair de Lune", "Hungarian Dance No. 5", "Symphony No. 5: Adagietto", "Nuvole Bianche",
            "Moonlight Sonata", "Requiem: Lacrimosa", "Cello Suite No. 1 in G Major", "1812 Overture", "Ballade No. 1 in G Minor",
            "Summer (Storm)", "Prelude to the Afternoon of a Faun", "Lullaby (Wiegenlied)", "Symphony No. 2: Resurrection", "Divenire",
            "Für Elise", "The Magic Flute: Overture", "Brandenburg Concerto No. 3", "The Nutcracker: Waltz of the Flowers", "Fantaisie-Impromptu",
            "Winter (The Four Seasons)", "Arabesque No. 1", "Symphony No. 1 in C Minor", "Symphony No. 9: Finale", "Fly",
            "Symphony No. 9: Ode to Joy", "Symphony No. 40 in G Minor", "Toccata and Fugue in D Minor", "Sleeping Beauty Waltz", "Prelude in E Minor",
            "Autumn (The Four Seasons)", "La Mer", "Academic Festival Overture", "Kindertotenlieder", "Experience",
            "Pathétique Sonata", "Piano Concerto No. 21 (Elvira Madigan)", "Goldberg Variations (Aria)", "Piano Concerto No. 1 in B-flat Minor", "Polonaise in A-flat Major (Heroic)",
            "Gloria in D Major", "Reverie", "Violin Concerto in D Major", "Das Lied von der Erde", "I Giorni"
        ]
    },
    "Country": {
        "artists": [
            "Johnny Cash", "Dolly Parton", "Morgan Wallen", "Luke Combs", "Chris Stapleton",
            "Zach Bryan", "Carrie Underwood", "Willie Nelson", "Garth Brooks", "Kacey Musgraves"
        ],
        "keywords": [
            "Ring of Fire", "Jolene", "Last Night", "Fast Car", "Tennessee Whiskey",
            "Something in the Orange", "Before He Cheats", "On the Road Again", "Friends in Low Places", "Follow Your Arrow",
            "I Walk the Line", "9 to 5", "Wasted on You", "Beautiful Crazy", "Broken Halos",
            "Heading South", "Jesus Take the Wheel", "Always on My Mind", "The Dance", "Rainbow",
            "Folsom Prison Blues", "Coat of Many Colors", "Whiskey Glasses", "When It Rains It Pours", "Parachute",
            "I Remember Everything", "Cowboy Casanova", "Blue Eyes Crying in the Rain", "The Thunder Rolls", "Slow Burn",
            "Hurt", "I Will Always Love You", "Chasin' You", "She Got the Best of Me", "Cold",
            "Sun to Me", "Blown Away", "Pancho and Lefty", "Unanswered Prayers", "Butterflies",
            "Sunday Morning Coming Down", "Here You Come Again", "Sand in My Boots", "Hurricane", "Starting Over",
            "Dawns", "Church Bells", "Crazy", "Rodeo", "Space Cowboy"
        ]
    },
    "Latin": {
        "artists": [
            "Bad Bunny", "Rosalía", "J Balvin", "Shakira", "Daddy Yankee",
            "Peso Pluma", "Karol G", "Maluma", "Rauw Alejandro", "Ozuna"
        ],
        "keywords": [
            "Tití Me Preguntó", "DESPECHÁ", "Mi Gente", "Hips Don't Lie", "Gasolina",
            "Ella Baila Sola", "PROVENZA", "Hawái", "Todo De Ti", "Baila Baila Baila",
            "Me Porto Bonito", "MALAMENTE", "Ginza", "Whenever Wherever", "Dura",
            "La Bebe (Remix)", "TQG", "Felices los 4", "Punto 40", "Se Preparó",
            "Ojitos Lindos", "SAKURA", "Ay Vamos", "Waka Waka", "Con Calma",
            "PRC", "MAMIII", "Sobrio", "LOKERA", "El Farsante",
            "Callaíta", "BIZCOCHITO", "Safari", "Chantaje", "Limbo",
            "Lady Gaga", "Bichota", "Corazón", "Cúrame", "Caramelo",
            "Moscow Mule", "LA FAMA", "In Da Getto", "La Tortura", "Despacito",
            "Qlona", "AMARGURA", "11 PM", "Party", "Dile Que Tu Me Quieres"
        ]
    },
    "Metal": {
        "artists": [
            "Metallica", "Iron Maiden", "Black Sabbath", "Slayer", "Megadeth",
            "Slipknot", "System of a Down", "Judas Priest", "Pantera", "Avenged Sevenfold"
        ],
        "keywords": [
            "Enter Sandman", "The Trooper", "Paranoid", "Raining Blood", "Holy Wars... The Punishment Due",
            "Duality", "Chop Suey!", "Painkiller", "Walk", "Hail to the King",
            "Master of Puppets", "Hallowed Be Thy Name", "Iron Man", "Angel of Death", "Symphony of Destruction",
            "Psychosocial", "Toxicity", "Breaking the Law", "Cowboys from Hell", "Bat Country",
            "One", "Run to the Hills", "War Pigs", "South of Heaven", "Peace Sells",
            "Wait and Bleed", "B.Y.O.B.", "Electric Eye", "Cemetery Gates", "Nightmare",
            "Fade to Black", "Fear of the Dark", "Children of the Grave", "Seasons in the Abyss", "Tornado of Souls",
            "Before I Forget", "Aerials", "Living After Midnight", "5 Minutes Alone", "Afterlife",
            "For Whom the Bell Tolls", "Aces High", "Sweet Leaf", "War Ensemble", "A Tout Le Monde",
            "Snuff", "Sugar", "Turbo Lover", "Domination", "So Far Away"
        ]
    }
}

def esc(s: str) -> str:
    return str(s).replace("'", "''")

def seed_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Execute schema
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    sql_statements = [schema_sql, "\n-- ================= SEED DATA =================\n"]

    print("Populating genres and artists...")
    genre_ids = {}
    artist_ids = {}

    for genre_name, data in GENRE_CATALOG.items():
        desc = f"Top charts and iconic tracks for {genre_name} music."
        cursor.execute("INSERT INTO genres (name, description) VALUES (?, ?)", (genre_name, desc))
        genre_id = cursor.lastrowid
        genre_ids[genre_name] = genre_id
        sql_statements.append(f"INSERT INTO genres (genre_id, name, description) VALUES ({genre_id}, '{esc(genre_name)}', '{esc(desc)}');")

        for artist_name in data["artists"]:
            if artist_name not in artist_ids:
                monthly_listeners = random.randint(5_000_000, 85_000_000)
                country = random.choice(["United States", "United Kingdom", "Canada", "Australia", "Germany", "Sweden", "Colombia", "Puerto Rico", "Austria"])
                cursor.execute(
                    "INSERT INTO artists (name, bio, country, monthly_listeners) VALUES (?, ?, ?, ?)",
                    (artist_name, f"Acclaimed {artist_name} artist.", country, monthly_listeners)
                )
                artist_id = cursor.lastrowid
                artist_ids[artist_name] = artist_id
                sql_statements.append(
                    f"INSERT INTO artists (artist_id, name, bio, country, monthly_listeners) VALUES ({artist_id}, '{esc(artist_name)}', 'Acclaimed {esc(artist_name)} artist.', '{country}', {monthly_listeners});"
                )

    # 2. Populate Albums and 50 Songs per Genre
    print("Generating exactly 50 top songs for each genre...")
    album_ids = {}
    song_counter = 0

    for genre_name, data in GENRE_CATALOG.items():
        genre_id = genre_ids[genre_name]
        artists_list = data["artists"]
        song_titles = data["keywords"] # Length is 50

        # Sort songs with decreasing popularity so rank 1 is highest
        # Popularity score descending from 99.9 down to 75.0
        # Play count descending from ~1.8 Billion down to ~50 Million
        base_pop = 99.8
        base_plays = 1_850_000_000

        for i, title in enumerate(song_titles):
            song_counter += 1
            artist_name = artists_list[i % len(artists_list)]
            artist_id = artist_ids[artist_name]

            # Album
            album_title = f"{title} (Album)"
            if (artist_id, album_title) not in album_ids:
                year = random.randint(1970, 2024)
                cursor.execute(
                    "INSERT INTO albums (artist_id, title, release_year) VALUES (?, ?, ?)",
                    (artist_id, album_title, year)
                )
                alb_id = cursor.lastrowid
                album_ids[(artist_id, album_title)] = alb_id
                sql_statements.append(
                    f"INSERT INTO albums (album_id, artist_id, title, release_year) VALUES ({alb_id}, {artist_id}, '{esc(album_title)}', {year});"
                )
            else:
                alb_id = album_ids[(artist_id, album_title)]

            # Song attributes
            pop_score = round(base_pop - (i * 0.45) - random.uniform(0.01, 0.1), 2)
            play_count = int(base_plays - (i * 35_000_000) + random.randint(-500_000, 500_000))
            if play_count < 10_000_000:
                play_count = 10_000_000 + random.randint(100_000, 5_000_000)
            duration = random.randint(170, 310)
            file_path = f"/music/{genre_name.lower().replace(' ', '_').replace('/', '_')}/{title.lower().replace(' ', '_')}.mp3"

            cursor.execute(
                """INSERT INTO songs 
                   (title, primary_artist_id, album_id, duration_seconds, play_count, popularity_score, file_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, artist_id, alb_id, duration, play_count, pop_score, file_path)
            )
            s_id = cursor.lastrowid
            sql_statements.append(
                f"INSERT INTO songs (song_id, title, primary_artist_id, album_id, duration_seconds, play_count, popularity_score, file_path) "
                f"VALUES ({s_id}, '{esc(title)}', {artist_id}, {alb_id}, {duration}, {play_count}, {pop_score}, '{esc(file_path)}');"
            )

            # Map to genre
            cursor.execute("INSERT INTO song_genres (song_id, genre_id, is_primary) VALUES (?, ?, 1)", (s_id, genre_id))
            sql_statements.append(f"INSERT INTO song_genres (song_id, genre_id, is_primary) VALUES ({s_id}, {genre_id}, 1);")

    # 3. Add Sample Users & Playlists
    print("Adding sample users, playlists, and history...")
    users = [
        ("alex_turner", "alex@example.com"),
        ("sarah_connor", "sarah@example.com"),
        ("david_bowman", "david@example.com")
    ]
    for u_name, u_email in users:
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (u_name, u_email))
        u_id = cursor.lastrowid
        sql_statements.append(f"INSERT INTO users (user_id, username, email) VALUES ({u_id}, '{u_name}', '{u_email}');")

        # Create user playlist
        pl_title = f"{u_name.split('_')[0].title()}'s Favorites"
        cursor.execute("INSERT INTO playlists (user_id, title, description) VALUES (?, ?, ?)", (u_id, pl_title, "My top curated tracks"))
        pl_id = cursor.lastrowid
        sql_statements.append(f"INSERT INTO playlists (playlist_id, user_id, title, description) VALUES ({pl_id}, {u_id}, '{pl_title}', 'My top curated tracks');")

        # Pick 5 random songs for this playlist and favorites
        sample_song_ids = random.sample(range(1, song_counter + 1), 5)
        for pos, s_id in enumerate(sample_song_ids, 1):
            cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id, position) VALUES (?, ?, ?)", (pl_id, s_id, pos))
            sql_statements.append(f"INSERT INTO playlist_songs (playlist_id, song_id, position) VALUES ({pl_id}, {s_id}, {pos});")

            cursor.execute("INSERT INTO user_favorites (user_id, song_id) VALUES (?, ?)", (u_id, s_id))
            sql_statements.append(f"INSERT INTO user_favorites (user_id, song_id) VALUES ({u_id}, {s_id});")

            cursor.execute("INSERT INTO listening_history (user_id, song_id, duration_played_seconds, completed) VALUES (?, ?, ?, 1)", (u_id, s_id, 200))
            sql_statements.append(f"INSERT INTO listening_history (user_id, song_id, duration_played_seconds, completed) VALUES ({u_id}, {s_id}, 200, 1);")

    conn.commit()

    # Save to seed_data.sql
    with open(SQL_DUMP_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))

    print(f"Database successfully populated at {DB_FILE}!")
    print(f"Total songs generated: {song_counter} (50 songs x {len(GENRE_CATALOG)} genres)")
    print(f"SQL seed dump exported to {SQL_DUMP_FILE}")

    # Verify query for Top 5 songs of each genre from vw_top_50_by_genre
    print("\n--- SAMPLE CHECK: TOP 3 SONGS FOR EACH GENRE ---")
    cursor.execute("""
        SELECT genre_name, genre_rank, song_title, artist_name, popularity_score, play_count
        FROM vw_top_50_by_genre
        WHERE genre_rank <= 3
        ORDER BY genre_name, genre_rank;
    """)
    rows = cursor.fetchall()
    curr_genre = None
    for row in rows:
        genre, rank, song, artist, pop, plays = row
        if genre != curr_genre:
            print(f"\n[{genre}]")
            curr_genre = genre
        print(f"  #{rank}: {song} by {artist} (Score: {pop}, Plays: {plays:,})")

    # Check song count per genre in the Top 50 view
    cursor.execute("""
        SELECT genre_name, COUNT(*) 
        FROM vw_top_50_by_genre 
        GROUP BY genre_name
        ORDER BY genre_name;
    """)
    print("\n--- TOP 50 VERIFICATION: COUNT PER GENRE ---")
    for genre, count in cursor.fetchall():
        print(f"  {genre}: {count} songs in Top 50 chart")

    conn.close()

if __name__ == "__main__":
    seed_database()
