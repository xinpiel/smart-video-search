**Smart Video Search Application**

This application allows users to upload videos, process them for key frames, perform OCR and audio transcription, and search through the content. Users can jump to specific timestamps in the video based on search results.


**Features**

Video Upload: Upload multiple video files in formats like MP4, AVI, and MOV.

Key Frame Extraction: Automatically extract key frames from videos based on scene changes.

OCR Processing: Perform Optical Character Recognition on extracted frames to detect text.

Audio Transcription: Transcribe audio from videos using Whisper.

Search Functionality: Search through the transcribed text and OCR results.

Timestamp Navigation: Clickable timestamps allow users to jump to specific points in the video.

Database Management: Reset and reprocess videos to update the database.


**How It Works**

Upload Videos: Use the file uploader to select and upload video files.

Process Videos: Click "Process New Videos" to extract frames, perform OCR, and transcribe audio.

Search: Enter a search term to find relevant text in the videos.

View Results: See search results with clickable timestamps to navigate the video.

Reprocess: Use the "Reprocess All Videos" button to reset the database and reprocess all videos.


**Technical Details**

Frontend: Built with Streamlit for a simple and interactive UI.

Backend: Uses OpenCV for frame extraction, EasyOCR for text detection, and Whisper for audio transcription.

Database: SQLite is used to store video metadata, including timestamps, OCR text, and transcriptions.

Video Playback: Custom HTML5 video player with JavaScript for precise timestamp navigation.

**Setup Instructions**

Install Dependencies:

pip install -r requirements.txt
Run the Application:

streamlit run streamlit_app.py
Access the App: Open your browser and go to http://localhost:8501.


**Future Improvements**

Add more improvements to make the code production ready including optimize for GPU and multiple threads processing.

Add more robust error handling and logging.

Add more tests and improve test coverage.

Add more robust database backup and restore procedures.

Enhance search capabilities with more advanced search algorithms or any cloud search functions.

Add support for more video formats and larger file sizes.


**Contributing**

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

**License**

This project is licensed under the MIT License.
