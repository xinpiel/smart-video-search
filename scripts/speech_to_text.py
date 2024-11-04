import whisper
import os
from .database import index_metadata

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    try:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception as e:
        print(f"Error formatting timestamp: {str(e)}")
        return "00:00:00"

def process_audio(video_path):
    """Extract and transcribe audio from video"""
    video_name = os.path.basename(video_path)
    
    try:
        # Load Whisper model
        model = whisper.load_model("base")
        
        # Transcribe audio
        result = model.transcribe(video_path)
        
        # Process segments
        for segment in result["segments"]:
            # Format timestamp to HH:MM:SS
            timestamp = format_timestamp(segment["start"])
            
            index_metadata(
                video_name=video_name,
                frame_number=None,
                timestamp=timestamp,  # Now in HH:MM:SS format
                transcription=segment["text"],
                ocr_text=None,
                objects_detected=None
            )
            
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
