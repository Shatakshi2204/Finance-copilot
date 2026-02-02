"""
Abstract base class for macro data API clients.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ..config import MetricType, MacroDataPoint
from ..http_client import RobustHTTPClient


class MacroDataClient(ABC):
    """Abstract base class for macro data API clients."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.http_client = RobustHTTPClient()

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of the data source."""
        pass

    @abstractmethod
    def fetch_metric(
        self,
        metric: MetricType,
        country_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> MacroDataPoint:
        """Fetch a specific metric for a country."""
        pass

    def _get_current_timestamp(self) -> str:
        """Get current ISO timestamp."""
        return datetime.utcnow().isoformat() + "Z"