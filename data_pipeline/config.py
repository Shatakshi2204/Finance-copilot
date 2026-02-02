"""
Configuration, enums, and dataclasses for the triangulation pipeline.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class MetricType(Enum):
    """Supported macroeconomic metrics."""
    GDP_GROWTH = "gdp_growth"
    INFLATION = "inflation"
    UNEMPLOYMENT = "unemployment"
    INTEREST_RATE = "interest_rate"


class ConfidenceLevel(Enum):
    """Confidence levels based on source agreement."""
    HIGH = "high"          # All sources agree (within tolerance)
    MEDIUM = "medium"      # Two sources agree, one differs
    LOW = "low"            # All sources differ significantly
    SINGLE_SOURCE = "single_source"  # Only one source available
    NO_DATA = "no_data"    # No data available


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class MacroDataPoint:
    """Represents a single macroeconomic data point from a source."""
    source: str
    metric: str
    country: str
    country_code: str
    value: Optional[float]
    unit: str
    period: str
    retrieved_at: str
    raw_response: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class TriangulatedResult:
    """Result of triangulating data across multiple sources."""
    metric: str
    country: str
    country_code: str
    period: str
    confidence: ConfidenceLevel
    consensus_value: Optional[float]
    fred_value: Optional[float]
    worldbank_value: Optional[float]
    oecd_value: Optional[float]
    explanation: str
    sources_used: list = field(default_factory=list)
    disagreement_details: Optional[str] = None


@dataclass
class ChatMLMessage:
    """Single message in ChatML format."""
    role: str
    content: str


@dataclass
class ChatMLSample:
    """Complete ChatML training sample."""
    messages: list