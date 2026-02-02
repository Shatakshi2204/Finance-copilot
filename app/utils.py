"""
Utility Functions
=================
Helper functions for the application.
"""

import logging
import hashlib
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def format_percentage(value: float | None, decimals: int = 2) -> str:
    """Format a number as a percentage string."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_timestamp(timestamp: str) -> str:
    """Format an ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return timestamp


def get_confidence_emoji(confidence: str) -> str:
    """Get an emoji for a confidence level."""
    emoji_map = {
        "high": "🟢",
        "medium": "🟡",
        "low": "🔴",
        "single_source": "🟠",
        "no_data": "⚪"
    }
    return emoji_map.get(confidence, "⚪")


def get_confidence_description(confidence: str) -> str:
    """Get a description for a confidence level."""
    descriptions = {
        "high": "High confidence - Multiple sources agree",
        "medium": "Medium confidence - Sources show some disagreement",
        "low": "Low confidence - Significant source disagreement",
        "single_source": "Limited confidence - Only one source available",
        "no_data": "No data available from any source"
    }
    return descriptions.get(confidence, "Unknown confidence level")


def get_risk_level(metric: str, value: float | None) -> tuple[str, str]:
    """
    Determine risk level for a metric value.
    
    Returns:
        Tuple of (risk_level, emoji)
    """
    if value is None:
        return "unknown", "❓"
    
    risk_thresholds = {
        "gdp_growth": {"low": 3, "moderate": 1},
        "inflation": {"low": 2, "moderate": 4},
        "unemployment": {"low": 4, "moderate": 6},
        "interest_rate": {"low": 2, "moderate": 4}
    }
    
    thresholds = risk_thresholds.get(metric, {})
    
    if metric == "gdp_growth":
        # Lower GDP growth = higher risk
        if value >= thresholds.get("low", 3):
            return "low", "🟢"
        elif value >= thresholds.get("moderate", 1):
            return "moderate", "🟡"
        else:
            return "high", "🔴"
    else:
        # Higher values = higher risk
        if value <= thresholds.get("low", 2):
            return "low", "🟢"
        elif value <= thresholds.get("moderate", 4):
            return "moderate", "🟡"
        else:
            return "high", "🔴"


def hash_message(message: str) -> str:
    """Create a hash of a message for caching."""
    return hashlib.md5(message.encode()).hexdigest()[:8]


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    # Remove potentially harmful characters
    sanitized = text.strip()
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    return sanitized


def setup_logging(level: int = logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )