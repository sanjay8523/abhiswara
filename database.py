import sqlite3
import hashlib
import os
from contextlib import contextmanager

DB_PATH = 'songs.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize the database with songs table and preloaded data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create songs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                song_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                mood TEXT NOT NULL,
                cover_url TEXT NOT NULL,
                youtube_link TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood ON songs(mood)')
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM songs')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert sample songs
            sample_songs = [
                # Happy songs
                ("Happy", "Pharrell Williams", "Happy", "https://i.ytimg.com/vi/ZbZSe6N_BXs/maxresdefault.jpg", "https://www.youtube.com/watch?v=ZbZSe6N_BXs"),
                ("Good as Hell", "Lizzo", "Happy", "https://i.ytimg.com/vi/SmbmeOgWsqE/maxresdefault.jpg", "https://www.youtube.com/watch?v=SmbmeOgWsqE"),
                ("Uptown Funk", "Mark Ronson ft. Bruno Mars", "Happy", "https://i.ytimg.com/vi/OPf0YbXqDm0/maxresdefault.jpg", "https://www.youtube.com/watch?v=OPf0YbXqDm0"),
                ("Can't Stop the Feeling", "Justin Timberlake", "Happy", "https://i.ytimg.com/vi/ru0K8uYEZWw/maxresdefault.jpg", "https://www.youtube.com/watch?v=ru0K8uYEZWw"),
                ("Walking on Sunshine", "Katrina and the Waves", "Happy", "https://i.ytimg.com/vi/iPUmE-tne5U/maxresdefault.jpg", "https://www.youtube.com/watch?v=iPUmE-tne5U"),
                
                # Sad songs
                ("Someone Like You", "Adele", "Sad", "https://i.ytimg.com/vi/hLQl3WQQoQ0/maxresdefault.jpg", "https://www.youtube.com/watch?v=hLQl3WQQoQ0"),
                ("Hello", "Adele", "Sad", "https://i.ytimg.com/vi/YQHsXMglC9A/maxresdefault.jpg", "https://www.youtube.com/watch?v=YQHsXMglC9A"),
                ("The Sound of Silence", "Disturbed", "Sad", "https://i.ytimg.com/vi/u9Dg-g7t2l4/maxresdefault.jpg", "https://www.youtube.com/watch?v=u9Dg-g7t2l4"),
                ("Mad World", "Gary Jules", "Sad", "https://i.ytimg.com/vi/4N3N1MlvVc4/maxresdefault.jpg", "https://www.youtube.com/watch?v=4N3N1MlvVc4"),
                ("Hurt", "Johnny Cash", "Sad", "https://i.ytimg.com/vi/8AHCfZTRGiI/maxresdefault.jpg", "https://www.youtube.com/watch?v=8AHCfZTRGiI"),
                
                # Angry songs
                ("Break Stuff", "Limp Bizkit", "Angry", "https://i.ytimg.com/vi/ZpUYjpKg9KY/maxresdefault.jpg", "https://www.youtube.com/watch?v=ZpUYjpKg9KY"),
                ("Bodies", "Drowning Pool", "Angry", "https://i.ytimg.com/vi/04F4xlWSFh0/maxresdefault.jpg", "https://www.youtube.com/watch?v=04F4xlWSFh0"),
                ("Chop Suey", "System of a Down", "Angry", "https://i.ytimg.com/vi/CSvFpBOe8eY/maxresdefault.jpg", "https://www.youtube.com/watch?v=CSvFpBOe8eY"),
                ("In the End", "Linkin Park", "Angry", "https://i.ytimg.com/vi/eVTXPUF4Oz4/maxresdefault.jpg", "https://www.youtube.com/watch?v=eVTXPUF4Oz4"),
                ("Killing in the Name", "Rage Against the Machine", "Angry", "https://i.ytimg.com/vi/bWXazVhlyxQ/maxresdefault.jpg", "https://www.youtube.com/watch?v=bWXazVhlyxQ"),
                
                # Depressed songs
                ("Breathe Me", "Sia", "Depressed", "https://i.ytimg.com/vi/hSjIz8oQuko/maxresdefault.jpg", "https://www.youtube.com/watch?v=hSjIz8oQuko"),
                ("Heavy", "Linkin Park ft. Kiiara", "Depressed", "https://i.ytimg.com/vi/5dmQ3QWpy1Q/maxresdefault.jpg", "https://www.youtube.com/watch?v=5dmQ3QWpy1Q"),
                ("Numb", "Linkin Park", "Depressed", "https://i.ytimg.com/vi/kXYiU_JCYtU/maxresdefault.jpg", "https://www.youtube.com/watch?v=kXYiU_JCYtU"),
                ("Boulevard of Broken Dreams", "Green Day", "Depressed", "https://i.ytimg.com/vi/Soa3gO7tL-c/maxresdefault.jpg", "https://www.youtube.com/watch?v=Soa3gO7tL-c"),
                ("Fade to Black", "Metallica", "Depressed", "https://i.ytimg.com/vi/WEQnzs8wl6E/maxresdefault.jpg", "https://www.youtube.com/watch?v=WEQnzs8wl6E"),
                
                # Calm songs
                ("Weightless", "Marconi Union", "Calm", "https://i.ytimg.com/vi/UfcAVejslrU/maxresdefault.jpg", "https://www.youtube.com/watch?v=UfcAVejslrU"),
                ("Clair de Lune", "Claude Debussy", "Calm", "https://i.ytimg.com/vi/CvFH_6DNRCY/maxresdefault.jpg", "https://www.youtube.com/watch?v=CvFH_6DNRCY"),
                ("Holocene", "Bon Iver", "Calm", "https://i.ytimg.com/vi/TWcyIpul8OE/maxresdefault.jpg", "https://www.youtube.com/watch?v=TWcyIpul8OE"),
                ("The Night We Met", "Lord Huron", "Calm", "https://i.ytimg.com/vi/KtlgYxa6BMU/maxresdefault.jpg", "https://www.youtube.com/watch?v=KtlgYxa6BMU"),
                ("Skinny Love", "Bon Iver", "Calm", "https://i.ytimg.com/vi/ssdgFoHLwnk/maxresdefault.jpg", "https://www.youtube.com/watch?v=ssdgFoHLwnk"),
            ]
            
            cursor.executemany('''
                INSERT INTO songs (title, artist, mood, cover_url, youtube_link)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_songs)
            
            print(f"Database initialized with {len(sample_songs)} songs")

def get_songs_by_mood(mood):
    """Get all songs for a specific mood"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # ✅ ADDED COLLATE NOCASE HERE
        cursor.execute('''
            SELECT song_id, title, artist, mood, cover_url, youtube_link 
            FROM songs 
            WHERE mood COLLATE NOCASE = ?
            ORDER BY RANDOM()
            LIMIT 10
        ''', (mood,))
        
        songs = cursor.fetchall()
        
        # Convert to list of dictionaries
        return [dict(song) for song in songs]

def init_users_table():
    """Initialize the users table"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for email lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
        
        print("Users table initialized")

def create_user(username, email, password):
    """Create a new user"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None

def verify_user(email, password):
    """Verify user credentials"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, email 
            FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None

def get_user_by_email(email):
    """Get user by email"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, email 
            FROM users 
            WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None

if __name__ == "__main__":
    init_database()
    init_users_table()
    print("Database setup complete!")
