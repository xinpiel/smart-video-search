import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import os
from .database import index_metadata

class GOT_OCR:
    def __init__(self):
        """Initialize GOT-OCR2.0 model"""
        self.tokenizer = AutoTokenizer.from_pretrained('stepfun-ai/GOT-OCR2_0', trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            'stepfun-ai/GOT-OCR2_0', 
            trust_remote_code=True, 
            low_cpu_mem_usage=True, 
            device_map='cuda' if torch.cuda.is_available() else 'cpu',
            use_safetensors=True, 
            pad_token_id=self.tokenizer.eos_token_id
        )
        self.model = self.model.eval()
        if torch.cuda.is_available():
            self.model = self.model.cuda()

def ocr_detection(frames_folder, video_name):
    """Perform OCR on extracted frames using GOT-OCR2.0"""
    try:
        # Initialize OCR model
        ocr = GOT_OCR()
        print("OCR model loaded successfully")
        
        frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith(('.jpg', '.png'))])
        
        if not frame_files:
            print(f"No frames found in {frames_folder}")
            return

        processed_count = 0
        for frame in frame_files:
            frame_path = os.path.join(frames_folder, frame)
            frame_number = int(frame.split('_')[1].split('.')[0])
            
            try:
                # Process frame with GOT-OCR2.0
                result = ocr.model.chat(ocr.tokenizer, frame_path, ocr_type='ocr')
                
                # Clean and validate text
                text = result.strip()
                
                # Index the OCR results if text was found
                if text:
                    print(f"Found text in frame {frame}: {text[:100]}...")
                    index_metadata(
                        video_name=video_name,
                        frame_number=frame_number,
                        timestamp=frame_number / 30,
                        transcription=None,
                        ocr_text=text,
                        objects_detected=None
                    )
                    processed_count += 1
                
            except Exception as e:
                print(f"Error processing frame {frame}: {str(e)}")
                continue

        print(f"OCR completed: processed {processed_count} frames out of {len(frame_files)} from {video_name}")
        
    except Exception as e:
        print(f"Error initializing OCR model: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Install required packages:")
        print("   pip install torch==2.0.1 torchvision==0.15.2 transformers==4.37.2")
        print("2. Ensure you have enough GPU memory")
        print("3. Try using CPU if GPU is not available")
