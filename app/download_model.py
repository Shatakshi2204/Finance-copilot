"""
Download Model Script
=====================
Downloads the GGUF model from HuggingFace before running the app.
Run this once: python download_model.py
"""

from huggingface_hub import hf_hub_download
from pathlib import Path
import os

# Model configuration
HF_REPO_ID = "ty8890/financial-mistral-qlora-gguf"
HF_FILENAME = "mistral-7b-instruct-v0.3.Q4_K_M.gguf"
LOCAL_DIR = "models"

def download_model():
    print(f"=" * 60)
    print("Financial LLM Copilot - Model Downloader")
    print(f"=" * 60)
    print(f"\nRepository: {HF_REPO_ID}")
    print(f"Filename: {HF_FILENAME}")
    print(f"Local Directory: {LOCAL_DIR}")
    print(f"\nStarting download... (This may take several minutes)\n")
    
    # Create models directory
    Path(LOCAL_DIR).mkdir(parents=True, exist_ok=True)
    
    try:
        downloaded_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_FILENAME,
            local_dir=LOCAL_DIR,
            resume_download=True,  # Resume if interrupted
        )
        
        print(f"\n✅ Model downloaded successfully!")
        print(f"📁 Saved to: {downloaded_path}")
        print(f"\nYou can now run the app with:")
        print(f"   python -m streamlit run app.py")
        
        return downloaded_path
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Try running the script again (it will resume)")
        print("3. Manually download from: https://huggingface.co/{HF_REPO_ID}")
        return None

if __name__ == "__main__":
    download_model()
