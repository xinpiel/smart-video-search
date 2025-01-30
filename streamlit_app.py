import streamlit as st
from scripts.extract_frames import extract_frames
from scripts.ocr_detection import ocr_detection
from scripts.speech_to_text import process_audio
from scripts.database import reset_database, search_metadata
import os
import base64
from google.cloud import storage

# Initialize Google Cloud Storage client
storage_client = storage.Client()
bucket_name = "smart-video-449213-temp"
bucket = storage_client.bucket(bucket_name)

def ensure_bucket_exists():
    """Ensure the bucket exists, create if it doesn't"""
    if not bucket.exists():
        bucket = storage_client.create_bucket(bucket_name)
    return bucket

def upload_to_gcs(file_bytes, destination_blob_name):
    """Upload a file to Google Cloud Storage"""
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(file_bytes)
    return blob

def download_from_gcs(source_blob_name):
    """Download a file from Google Cloud Storage"""
    blob = bucket.blob(source_blob_name)
    return blob.download_as_bytes()

def display_uploaded_videos(uploaded_files, cols=3):
    """Display uploaded videos in a grid"""
    columns = st.columns(cols)
    
    for idx, uploaded_file in enumerate(uploaded_files):
        col_idx = idx % cols
        with columns[col_idx]:
            st.video(uploaded_file)
            st.caption(uploaded_file.name)

def get_video_data_url(blob_name):
    """Get video data URL from Google Cloud Storage"""
    video_bytes = download_from_gcs(blob_name)
    base64_video = base64.b64encode(video_bytes).decode()
    return f"data:video/mp4;base64,{base64_video}"

def main():
    st.title("Video Processing and Search")
    
    # Ensure bucket exists
    ensure_bucket_exists()
    
    # File upload
    uploaded_files = st.file_uploader("Choose video files", 
                                    type=['mp4', 'avi', 'mov'], 
                                    accept_multiple_files=True)
    
    if uploaded_files:
        display_uploaded_videos(uploaded_files, cols=3)
        
        st.write("Files to be processed:")
        for file in uploaded_files:
            st.text(f"📁 {file.name}")
        
        if st.button("Process New Videos"):
            main_status = st.empty()
            sub_status = st.empty()
            progress_bar = st.progress(0)
            
            total_files = len(uploaded_files)
            for idx, uploaded_file in enumerate(uploaded_files):
                try:
                    # Upload to GCS
                    blob_name = f"videos/{uploaded_file.name}"
                    upload_to_gcs(uploaded_file.getvalue(), blob_name)
                    
                    main_status.info(f"Processing file {idx + 1}/{total_files}: {uploaded_file.name}")
                    
                    # Extract frames
                    sub_status.info(f"🎬 Extracting key frames...")
                    video_bytes = download_from_gcs(blob_name)
                    key_frames = extract_frames(video_bytes)
                    sub_status.success(f"✓ Extracted {len(key_frames)} key frames")
                    
                    # Process frames and upload results
                    sub_status.info(f"🔍 Processing OCR...")
                    ocr_results = ocr_detection(key_frames, uploaded_file.name)
                    upload_to_gcs(str(ocr_results).encode(), f"results/ocr/{uploaded_file.name}.json")
                    sub_status.success("✓ OCR processing complete")
                    
                    # Process audio
                    sub_status.info("🎤 Processing audio...")
                    audio_results = process_audio(video_bytes)
                    upload_to_gcs(str(audio_results).encode(), f"results/audio/{uploaded_file.name}.json")
                    sub_status.success("✓ Audio processing complete")
                    
                    progress_bar.progress((idx + 1) / total_files)
                    main_status.success(f"✅ Completed processing {uploaded_file.name}")
                    
                except Exception as e:
                    main_status.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                    continue
            
            if progress_bar.progress == 1.0:
                st.success("🎉 All files processed successfully!")

    # Search interface
    st.header("Search Videos")
    search_query = st.text_input("Enter search term")
    
    if search_query:
        results = search_metadata(search_query, "data/video_metadata.db")
        
        if results:
            # Group results by video
            video_results = {}
            for result in results:
                video_name = result['video_name']
                if video_name not in video_results:
                    video_results[video_name] = []
                video_results[video_name].append(result)
            
            # Create a video selector
            video_names = list(video_results.keys())
            selected_video = st.selectbox("Select video to play:", video_names)
            
            # Get the video file path
            video_path = f"temp/{selected_video}"
            
            if os.path.exists(video_path):
                # Prepare the video data URL
                video_data_url = get_video_data_url(video_path)
                
                # Build the buttons HTML
                button_html = ""
                for result in video_results[selected_video]:
                    if result['ocr_text']:
                        source_icon = "🔍"
                        text = result['ocr_text'][:50] + "..."
                    elif result['transcription']:
                        source_icon = "👄"
                        text = result['transcription'][:50] + "..."
                    else:
                        continue
                    
                    # Get hours, minutes, seconds as integers
                    h, m, s = map(int, result['timestamp'].split(':'))
                    
                    # Build the button HTML
                    button_html += f"""
                    <button onclick="seekToTime({h}, {m}, {s})" style="
                        background-color: #f0f2f6;
                        border: none;
                        padding: 10px;
                        margin: 5px 0;
                        border-radius: 5px;
                        cursor: pointer;
                        width: 100%;
                        text-align: left;
                        ">
                        {source_icon} {result['timestamp']}<br>
                        <small>{text}</small>
                    </button>
                    """
                
                # Build the expanders HTML
                expanders_html = ""
                for result in video_results[selected_video]:
                    if result['ocr_text']:
                        source_icon = "🔍"
                        text = result['ocr_text']
                    elif result['transcription']:
                        source_icon = "👄"
                        text = result['transcription']
                    else:
                        continue
                    
                    h, m, s = map(int, result['timestamp'].split(':'))
                    
                    # Build the expander content
                    expander_content = f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;">
                        <strong>{source_icon} at {result['timestamp']} - {text[:50]}...</strong>
                        <p>Full text: {text}</p>
                        <p>Timestamp: {result['timestamp']}</p>
                        <button onclick="seekToTime({h}, {m}, {s})" style="
                            background-color: #f0f2f6;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                            cursor: pointer;
                            ">
                            ⏱️ Jump to {result['timestamp']}
                        </button>
                    </div>
                    """
                    expanders_html += expander_content
                
                # Combine all HTML content
                html_content = f"""
                <div style="display: flex; flex-direction: row;">
                    <!-- Video Player -->
                    <div style="flex: 2; margin-right: 20px;">
                        <video id="myVideo" width="100%" controls>
                            <source src="{video_data_url}" type="video/mp4">
                            Your browser does not support the video element.
                        </video>
                    </div>
                    <!-- Clickable Timestamps -->
                    <div style="flex: 1;">
                        <h3>📍 Timestamps:</h3>
                        {button_html}
                    </div>
                </div>
                
                <!-- Expanders -->
                <div style="margin-top: 20px;">
                    <h3>🔍 Search Results:</h3>
                    {expanders_html}
                </div>
                
                <script>
                    var video = document.getElementById('myVideo');
                
                    function seekToTime(hours, minutes, seconds) {{
                        var totalSeconds = hours * 3600 + minutes * 60 + seconds;
                        video.currentTime = totalSeconds;
                        video.play();
                    }}
                </script>
                """
                
                # Render the combined HTML content
                st.components.v1.html(html_content, height=800)
            else:
                st.error(f"Video file not found: {video_path}")

if __name__ == "__main__":
    main()
