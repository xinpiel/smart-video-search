import whisper
import torch
import os

def test_whisper():
    """Test if Whisper is properly installed and working"""
    try:
        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"CUDA available: {cuda_available}")
        if cuda_available:
            print(f"GPU Device: {torch.cuda.get_device_name(0)}")

        # Try loading the tiny model (fastest to load)
        print("\nLoading Whisper tiny model...")
        model = whisper.load_model("tiny")
        print("✅ Model loaded successfully!")

        # Create a short test audio or use an existing one
        test_audio = "test_audio.mp3"  # You can replace this with any audio file
        if os.path.exists(test_audio):
            print(f"\nTranscribing test audio: {test_audio}")
            result = model.transcribe(test_audio)
            print("\nTranscription result:")
            print(result["text"])
            print("\n✅ Whisper is working correctly!")
        else:
            print("\n⚠️ No test audio file found.")
            print("Whisper model loaded successfully, but no transcription test performed.")
            print("To test transcription, provide an audio file path.")

    except Exception as e:
        print("\n❌ Whisper test failed:")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if PyTorch is installed:")
        print("   pip install torch")
        print("2. Check if Whisper is installed:")
        print("   pip install openai-whisper")
        print("3. For GPU support, ensure CUDA is properly set up")
        return False

    return True

if __name__ == "__main__":
    print("Testing Whisper Installation\n" + "="*25 + "\n")
    test_whisper()