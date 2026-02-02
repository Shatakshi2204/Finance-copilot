"""
Application Configuration
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """Model settings - conservative for stability."""
    
    hf_repo_id: str = "ty8890/financial-mistral-qlora-gguf"
    hf_filename: str = "mistral-7b-instruct-v0.3.Q4_K_M.gguf"
    local_model_dir: str = "models"
    local_model_path: str = "models/mistral-7b-instruct-v0.3.Q4_K_M.gguf"
    
    # Conservative settings for stability
    n_ctx: int = 256
    n_threads: int = 2
    n_gpu_layers: int = 0
    n_batch: int = 128
    
    # Generation
    max_tokens: int = 100
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1


@dataclass
class APIConfig:
    """API settings."""
    fred_api_key: str = field(default_factory=lambda: os.getenv("FRED_API_KEY", ""))
    fred_base_url: str = "https://api.stlouisfed.org/fred"
    worldbank_base_url: str = "https://api.worldbank.org/v2"
    timeout: int = 10
    max_retries: int = 2


@dataclass
class AppConfig:
    """App settings."""
    app_title: str = "Financial LLM Copilot"
    app_icon: str = "📊"
    max_chat_history: int = 10
    
    countries: dict = field(default_factory=lambda: {
        "USA": "United States",
        "IND": "India", 
        "EUU": "European Union",
        "CHN": "China"
    })
    
    metrics: dict = field(default_factory=lambda: {
        "gdp_growth": "GDP Growth",
        "inflation": "Inflation",
        "unemployment": "Unemployment",
        "interest_rate": "Interest Rate"
    })


model_config = ModelConfig()
api_config = APIConfig()
app_config = AppConfig()


def validate_config():
    return {
        "model_configured": True, 
        "fred_api_configured": bool(api_config.fred_api_key)
    }
