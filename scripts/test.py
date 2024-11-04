import streamlit as st
import sqlite3
import os
from datetime import timedelta

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    return str(timedelta(seconds=int(seconds)))

def get_video_names():
    """Get list of all unique video names from database"""
    try:
        conn = sqlite3.connect('data/video_metadata.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT video_name FROM video_metadata")
        videos = [row[0] for row in c.fetchall()]
        conn.close()
        return videos
    except Exception as e:
        print(f"Error getting video names: {str(e)}")
        return []

def get_timestamps(video_name):
    """Get all timestamps for a specific video"""
    try:
        conn = sqlite3.connect('data/video_metadata.db')
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT timestamp 
            FROM video_metadata 
            WHERE video_name = ? 
            AND timestamp != ''
            ORDER BY CAST(timestamp AS FLOAT)
        """, (video_name,))
        timestamps = [float(row[0]) for row in c.fetchall() if row[0]]
        conn.close()
        return timestamps
    except Exception as e:
        print(f"Error getting timestamps: {str(e)}")
        return []

def get_results_at_timestamp(video_name, timestamp, tolerance=1.0):
    """Get OCR and transcription results near the timestamp"""
    try:
        conn = sqlite3.connect('data/video_metadata.db')
        c = conn.cursor()
        
        # Get results within tolerance seconds of the timestamp
        c.execute("""
            SELECT timestamp, transcription, ocr_text
            FROM video_metadata
            WHERE video_name = ?
            AND CAST(timestamp AS FLOAT) BETWEEN ? - ? AND ? + ?
        """, (video_name, timestamp, tolerance, timestamp, tolerance))
        
        results = c.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Error getting results: {str(e)}")
        return []

def main():
    st.title("Video Processing Results Viewer")

    # Get list of processed videos
    videos = get_video_names()
    
    if not videos:
        st.error("No processed videos found in the database.")
        return

    # Video selection
    selected_video = st.selectbox("Select a video:", videos)

    if selected_video:
        # Get timestamps for selected video
        timestamps = get_timestamps(selected_video)
        
        if not timestamps:
            st.warning(f"No timestamps found for {selected_video}")
            return

        # Create timestamp selection
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Select timestamp:")
            selected_timestamp = st.slider(
                "Time (seconds)",
                min_value=float(min_time),
                max_value=float(max_time),
                value=float(min_time),
                step=0.5
            )
        
        with col2:
            st.write("Formatted time:")
            st.write(format_timestamp(selected_timestamp))

        # Get and display results
        results = get_results_at_timestamp(selected_video, selected_timestamp)
        
        if results:
            st.header("Results")
            
            for timestamp, transcription, ocr_text in results:
                with st.expander(f"Results at {format_timestamp(float(timestamp))}"):
                    if transcription:
                        st.subheader("🗣️ Transcription")
                        st.write(transcription)
                    
                    if ocr_text:
                        st.subheader("📝 OCR Text")
                        st.write(ocr_text)
                    
                    if not transcription and not ocr_text:
                        st.write("No text or transcription found at this timestamp.")
        else:
            st.info("No results found at this timestamp.")

        # Add statistics
        st.sidebar.header("Statistics")
        st.sidebar.write(f"Total timestamps: {len(timestamps)}")
        
        # Count entries with transcription and OCR
        conn = sqlite3.connect('data/video_metadata.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                COUNT(CASE WHEN transcription != '' THEN 1 END) as transcription_count,
                COUNT(CASE WHEN ocr_text != '' THEN 1 END) as ocr_count
            FROM video_metadata
            WHERE video_name = ?
        """, (selected_video,))
        
        trans_count, ocr_count = c.fetchone()
        conn.close()
        
        st.sidebar.write(f"Segments with transcription: {trans_count}")
        st.sidebar.write(f"Frames with OCR text: {ocr_count}")

if __name__ == "__main__":
    main()