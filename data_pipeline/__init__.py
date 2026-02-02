"""
Macro Data Triangulation Pipeline
=================================
Production-grade script for fetching, triangulating, and formatting
macroeconomic data from FRED, World Bank, and OECD APIs.

Outputs ChatML-formatted .jsonl for Unsloth/QLoRA fine-tuning.

Author: Financial LLM Copilot Project
"""

from .config import MetricType, ConfidenceLevel, MacroDataPoint, TriangulatedResult, ChatMLMessage, ChatMLSample
from .triangulation import TriangulationEngine
from .formatter import ChatMLFormatter
from .generator import DatasetGenerator

__all__ = [
    "MetricType",
    "ConfidenceLevel",
    "MacroDataPoint",
    "TriangulatedResult",
    "ChatMLMessage",
    "ChatMLSample",
    "TriangulationEngine",
    "ChatMLFormatter",
    "DatasetGenerator",
]