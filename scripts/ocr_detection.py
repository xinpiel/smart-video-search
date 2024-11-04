import easyocr
import os
from .database import index_metadata

def ocr_detection(key_frames, video_name):
    """Perform OCR on frames using easyOCR."""
    # Initialize EasyOCR reader once
    reader = easyocr.Reader(['en'])
    
    for frame_data in key_frames:
        # Original frame number from extract_frames
        original_frame_number = frame_data['frame_number']
        
        # Original timestamp from extract_frames
        original_timestamp = frame_data['timestamp']
        
        # Perform OCR on the frame
        results = reader.readtext(frame_data['frame'])
        
        # Combine all detected text
        text = ' '.join([result[1] for result in results])
        
        try:
            index_metadata(
                video_name=video_name,
                frame_number=str(original_frame_number),  # Original frame number
                timestamp=original_timestamp,  # Original timestamp
                transcription=None,
                ocr_text=text,
                objects_detected=None
            )
        except Exception as e:
            print(f"Error indexing metadata: {str(e)}")