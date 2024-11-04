import sqlite3
import json
import os

def setup_database():
    """Initialize SQLite database with FTS5 table"""
    try:
        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect('data/video_metadata.db')
        c = conn.cursor()
        
        # Create the FTS5 table for better text search capabilities
        c.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS video_metadata 
            USING fts5(
                video_name,
                frame_number,
                timestamp,
                transcription,
                ocr_text,
                objects_detected
            )
        ''')
        
        conn.commit()
        print("Database setup completed successfully")
    except Exception as e:
        print(f"Database setup error: {str(e)}")
    finally:
        conn.close()

def index_metadata(video_name, frame_number, timestamp, transcription, ocr_text, objects_detected):
    """Add metadata to the database."""
    try:
        conn = sqlite3.connect("data/video_metadata.db")
        c = conn.cursor()
        
        # Ensure frame_number is a string
        frame_number = str(frame_number) if frame_number is not None else None
        
        # Timestamp should already be formatted as HH:MM:SS
        c.execute('''
            INSERT INTO video_metadata 
            (video_name, frame_number, timestamp, transcription, ocr_text, objects_detected)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (video_name, frame_number, timestamp, transcription, ocr_text, objects_detected))
        
        conn.commit()
    except Exception as e:
        print(f"Error indexing metadata: {str(e)}")
    finally:
        if conn:
            conn.close()

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"

def search_metadata(search_query, db_path="data/video_metadata.db"):
    """Search for metadata in the database."""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Search across all text fields
        c.execute("""
            SELECT * FROM video_metadata 
            WHERE transcription LIKE ? OR ocr_text LIKE ?
        """, (f"%{search_query}%", f"%{search_query}%"))
        
        results = []
        for row in c.fetchall():
            results.append({
                "video_name": row[0],
                "frame_number": row[1],
                "timestamp": row[2],
                "transcription": row[3],
                "ocr_text": row[4],
                "objects_detected": row[5]
            })
        
        return results
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []
    finally:
        conn.close()

def get_processed_videos():
    """Get list of videos that have been processed"""
    try:
        conn = sqlite3.connect('data/video_metadata.db')
        c = conn.cursor()
        
        c.execute("SELECT DISTINCT video_name FROM video_metadata")
        videos = [row[0] for row in c.fetchall()]
        
        return videos
    except Exception as e:
        print(f"Error retrieving processed videos: {str(e)}")
        return []
    finally:
        conn.close()

def reset_database(db_path="data/video_metadata.db"):
    """Reset the database by dropping and recreating the table."""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Drop existing table if it exists
        c.execute('DROP TABLE IF EXISTS video_metadata')
        
        # Create new table
        c.execute('''
            CREATE TABLE video_metadata (
                video_name TEXT,
                frame_number TEXT,
                timestamp TEXT,
                transcription TEXT,
                ocr_text TEXT,
                objects_detected TEXT
            )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Error resetting database: {str(e)}")
    finally:
        conn.close()

def process_video(video_path, video_name, db_path="data/video_metadata.db"):
    """Process a single video."""
    try:
        # Extract frames
        frames_folder = extract_frames(video_path)
        
        # Perform OCR
        ocr_detection(frames_folder, video_name)
        
        # Process audio
        process_audio(video_path)
        
        return True
    except Exception as e:
        print(f"Error processing {video_name}: {str(e)}")
        return False