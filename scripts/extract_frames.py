import cv2
import os
import numpy as np
from datetime import timedelta

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    try:
        # Ensure seconds is a float or int
        seconds = float(seconds)
        td = timedelta(seconds=seconds)
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        seconds = td.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except Exception as e:
        print(f"Error formatting timestamp: {str(e)}")
        return "00:00:00"  # Return default timestamp if there's an error

def calculate_frame_difference(frame1, frame2):
    """Calculate the difference between two frames using grayscale"""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    return np.mean(diff)

def extract_frames(video_path):
    """Extract key frames based on scene changes with optimized processing"""
    FRAME_SKIP = 15
    SCENE_THRESHOLD = 20.0
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate dimensions for processing
    process_width = width // 4   # 1/4 size for processing
    process_height = height // 4
    
    frame_count = 0
    previous_frame_small = None
    key_frames = []  # Store frames and their info
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % FRAME_SKIP == 0:
            # Downsize for processing
            frame_small = cv2.resize(frame, (process_width, process_height))
            timestamp = format_timestamp(frame_count / fps)
            
            is_key_frame = False
            if previous_frame_small is not None:
                diff = calculate_frame_difference(frame_small, previous_frame_small)
                if diff > SCENE_THRESHOLD:
                    is_key_frame = True
            else:
                is_key_frame = True  # First frame
            
            if is_key_frame:
                # Store frame and its metadata
                key_frames.append({
                    'frame': frame,
                    'frame_number': frame_count,
                    'timestamp': timestamp
                })
            
            previous_frame_small = frame_small
        
        frame_count += 1

    cap.release()
    return key_frames

def get_frame_info(frames_folder):
    """Read key frames info from file"""
    info_path = os.path.join(frames_folder, "key_frames_info.txt")
    if os.path.exists(info_path):
        with open(info_path, "r") as f:
            return f.readlines()
    return []

def process_video(video_path, video_name, db_path="data/video_metadata.db"):
    """Process a single video."""
    try:
        # Extract frames and perform OCR in memory
        key_frames = extract_frames(video_path)
        
        # Perform OCR directly on the frames
        ocr_detection(key_frames, video_name)
        
        # Process audio
        process_audio(video_path)
        
        return True
    except Exception as e:
        print(f"Error processing {video_name}: {str(e)}")
        return False
