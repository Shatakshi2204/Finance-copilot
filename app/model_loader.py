"""
Model Loader
============
Robust model loading with proper Streamlit caching.
"""

import logging
import streamlit as st
from pathlib import Path
from typing import Optional
import gc

from config import model_config

logger = logging.getLogger(__name__)

# Global model reference (outside Streamlit)
_GLOBAL_MODEL = None


def get_model_path() -> str:
    """Get the local model path, download if needed."""
    local_path = Path(model_config.local_model_path)
    
    if local_path.exists():
        return str(local_path)
    
    # Download model
    from huggingface_hub import hf_hub_download
    
    logger.info(f"Downloading model from {model_config.hf_repo_id}...")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    
    hf_hub_download(
        repo_id=model_config.hf_repo_id,
        filename=model_config.hf_filename,
        local_dir=str(local_path.parent),
    )
    
    return str(local_path)


def load_llm_model():
    """Load model using global singleton pattern."""
    global _GLOBAL_MODEL
    
    if _GLOBAL_MODEL is not None:
        return _GLOBAL_MODEL
    
    from llama_cpp import Llama
    
    model_path = get_model_path()
    logger.info(f"Loading model from {model_path}...")
    
    _GLOBAL_MODEL = Llama(
        model_path=model_path,
        n_ctx=model_config.n_ctx,
        n_threads=model_config.n_threads,
        n_gpu_layers=model_config.n_gpu_layers,
        n_batch=model_config.n_batch,
        verbose=False,
    )
    
    logger.info("Model loaded successfully")
    return _GLOBAL_MODEL


def generate_response(prompt: str) -> str:
    """
    Generate a response - handles errors gracefully.
    """
    global _GLOBAL_MODEL
    
    try:
        # Ensure model is loaded
        if _GLOBAL_MODEL is None:
            load_llm_model()
        
        model = _GLOBAL_MODEL
        
        # Build simple prompt
        system = "You are a financial analyst. Be concise. Cite numbers. Max 80 words."
        full_prompt = f"[INST] {system}\n\n{prompt} [/INST]"
        
        # Generate with very conservative settings
        result = model(
            full_prompt,
            max_tokens=100,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.1,
            stop=["</s>", "[/INST]"],
            echo=False
        )
        
        # Force garbage collection after generation
        gc.collect()
        
        text = result["choices"][0]["text"].strip()
        return text if text else "Could not generate response."
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        # Try to recover by reloading model
        _GLOBAL_MODEL = None
        gc.collect()
        return "Error occurred. Please try again."


def is_model_loaded() -> bool:
    """Check if model is loaded."""
    return _GLOBAL_MODEL is not None


# Backward compatibility wrapper
class ModelLoader:
    @property
    def is_loaded(self) -> bool:
        return is_model_loaded()
    
    def load_model(self):
        return load_llm_model()
    
    def generate(self, prompt: str, **kwargs) -> str:
        return generate_response(prompt)


model_loader = ModelLoader()
