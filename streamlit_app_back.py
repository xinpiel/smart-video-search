import streamlit as st
from scripts.extract_frames import extract_frames
from scripts.ocr_detection import ocr_detection
from scripts.speech_to_text import process_audio
from scripts.database import reset_database, search_metadata
import os
import base64

def display_uploaded_videos(uploaded_files, cols=3):
    """Display uploaded videos in a grid"""
    # Create columns for video display
    columns = st.columns(cols)
    
    # Display videos in columns
    for idx, uploaded_file in enumerate(uploaded_files):
        col_idx = idx % cols
        with columns[col_idx]:
            st.video(uploaded_file)
            st.caption(uploaded_file.name)

def get_video_data_url(video_path):
    """Convert video file to data URL"""
    with open(video_path, 'rb') as video_file:
        video_bytes = video_file.read()
        base64_video = base64.b64encode(video_bytes).decode()
        return f"data:video/mp4;base64,{base64_video}"

def main():
    st.title("Video Processing and Search")
    
    # File upload
    uploaded_files = st.file_uploader("Choose video files", 
                                    type=['mp4', 'avi', 'mov'], 
                                    accept_multiple_files=True)
    
    if uploaded_files:
        # Display uploaded videos in a grid
        display_uploaded_videos(uploaded_files, cols=3)
        
        # Show list of files to be processed
        st.write("Files to be processed:")
        for file in uploaded_files:
            st.text(f"📁 {file.name}")
        
        # Process new videos
        if st.button("Process New Videos"):
            # Create status containers
            main_status = st.empty()
            sub_status = st.empty()
            progress_bar = st.progress(0)
            
            total_files = len(uploaded_files)
            for idx, uploaded_file in enumerate(uploaded_files):
                try:
                    # Save uploaded file temporarily
                    temp_path = f"temp/{uploaded_file.name}"
                    os.makedirs("temp", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Update main status
                    main_status.info(f"Processing file {idx + 1}/{total_files}: {uploaded_file.name}")
                    
                    # Extract frames with status
                    sub_status.info(f"🎬 Extracting key frames from {uploaded_file.name}...")
                    key_frames = extract_frames(temp_path)
                    sub_status.success(f"✓ Extracted {len(key_frames)} key frames from {uploaded_file.name}")
                    
                    # Perform OCR with status
                    sub_status.info(f"🔍 Performing OCR on frames from {uploaded_file.name}...")
                    ocr_detection(key_frames, uploaded_file.name)
                    sub_status.success(f"✓ OCR processing complete for {uploaded_file.name}")
                    
                    # Process audio with status
                    sub_status.info(f"🎤 Processing audio transcription from {uploaded_file.name}...")
                    process_audio(temp_path)
                    sub_status.success(f"✓ Audio transcription complete for {uploaded_file.name}")
                    
                    # Update progress
                    progress_bar.progress((idx + 1) / total_files)
                    
                    # Final success message for this file
                    main_status.success(f"✅ Completed processing {uploaded_file.name} ({idx + 1}/{total_files})")
                    
                except Exception as e:
                    main_status.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                    continue
            
            # Final completion message
            if progress_bar.progress == 1.0:
                st.success("🎉 All files processed successfully!")
        
        # Reprocess button
        if st.button("Reprocess All Videos"):
            try:
                main_status = st.empty()
                sub_status = st.empty()
                progress_bar = st.progress(0)
                
                main_status.info("🔄 Resetting database...")
                reset_database()
                main_status.success("✓ Database reset")
                
                # Process all videos again
                total_files = len(uploaded_files)
                for idx, uploaded_file in enumerate(uploaded_files):
                    try:
                        temp_path = f"temp/{uploaded_file.name}"
                        
                        main_status.info(f"Reprocessing file {idx + 1}/{total_files}: {uploaded_file.name}")
                        
                        # Extract frames
                        sub_status.info(f"🎬 Extracting key frames...")
                        key_frames = extract_frames(temp_path)
                        sub_status.success(f"✓ Extracted {len(key_frames)} key frames")
                        
                        # Perform OCR
                        sub_status.info(f"🔍 Performing OCR...")
                        ocr_detection(key_frames, uploaded_file.name)
                        sub_status.success("✓ OCR processing complete")
                        
                        # Process audio
                        sub_status.info("Processing audio...")
                        process_audio(temp_path)
                        sub_status.success("✓ Audio transcription complete")
                        
                        main_status.success(f"✅ Completed reprocessing {uploaded_file.name} ({idx + 1}/{total_files})")
                        
                    except Exception as e:
                        main_status.error(f"❌ Error reprocessing {uploaded_file.name}: {str(e)}")
                
            except Exception as e:
                st.error(f"Error during reprocessing: {str(e)}")

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
                # Create columns for video and timestamps
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Custom HTML5 video player with data URL
                    video_data_url = get_video_data_url(video_path)
                    video_player = f"""
                    <video id="myVideo" width="100%" controls>
                        <source src="{video_data_url}" type="video/mp4">
                        Your browser does not support the video element.
                    </video>

                    <script>
                        var video = document.getElementById('myVideo');
                        
                        window.seekToTime = function(hours, minutes, seconds) {{
                            var totalSeconds = hours * 3600 + minutes * 60 + seconds;
                            video.currentTime = totalSeconds;
                            video.play();
                        }}
                    </script>
                    """
                    st.components.v1.html(video_player, height=400)
                
                with col2:
                    st.write("📍 Timestamps:")
                    # Display clickable timestamps
                    for result in video_results[selected_video]:
                        if result['ocr_text']:
                            source_icon = "🔍"
                            text = result['ocr_text'][:50] + "..."
                        elif result['transcription']:
                            source_icon = "👄"
                            text = result['transcription'][:50] + "..."
                        else:
                            continue
                        
                        # Create clickable timestamp with JavaScript
                        h, m, s = result['timestamp'].split(':')
                        timestamp_button = f"""
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
                        st.components.v1.html(timestamp_button, height=70)
                
                # Display full results in expanders
                st.write("🔍 Search Results:")
                for result in video_results[selected_video]:
                    if result['ocr_text']:
                        source_icon = "🔍"
                        text = result['ocr_text']
                    elif result['transcription']:
                        source_icon = "👄"
                        text = result['transcription']
                    else:
                        continue
                    
                    with st.expander(f"{source_icon} at {result['timestamp']} - {text[:50]}..."):
                        st.write(f"Full text: {text}")
                        st.write(f"Timestamp: {result['timestamp']}")
                        h, m, s = result['timestamp'].split(':')
                        jump_button = f"""
                        <button onclick="seekToTime({h}, {m}, {s})" style="
                            background-color: #f0f2f6;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                            cursor: pointer;
                            ">
                            ⏱️ Jump to {result['timestamp']}
                        </button>
                        """
                        st.components.v1.html(jump_button, height=35)
            else:
                st.error(f"Video file not found: {video_path}")

if __name__ == "__main__":
    main()
