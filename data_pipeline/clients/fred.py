"""
FRED (Federal Reserve Economic Data) API client.
"""

import os
import logging
from typing import Optional

import requests

from ..config import MetricType, MacroDataPoint
from ..mappings import COUNTRY_MAPPINGS, METRIC_MAPPINGS
from .base import MacroDataClient


logger = logging.getLogger(__name__)


class FREDClient(MacroDataClient):
    """Client for Federal Reserve Economic Data (FRED) API."""

    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("FRED_API_KEY"))
        if not self.api_key:
            logger.warning("FRED_API_KEY not set. FRED requests will fail.")

    @property
    def source_name(self) -> str:
        return "FRED"

    def _get_series_id(self, metric: MetricType, country_code: str) -> str:
        """Get the FRED series ID for a metric and country."""
        metric_config = METRIC_MAPPINGS[metric]["fred"]

        if country_code in metric_config:
            return metric_config[country_code]

        template = metric_config.get("default", "")
        return template.format(country=country_code)

    def fetch_metric(
        self,
        metric: MetricType,
        country_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> MacroDataPoint:
        """Fetch metric from FRED API."""
        series_id = self._get_series_id(metric, country_code)
        country_info = COUNTRY_MAPPINGS.get(country_code, {"name": country_code})

        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 10,
            }

            if start_year:
                params["observation_start"] = f"{start_year}-01-01"
            if end_year:
                params["observation_end"] = f"{end_year}-12-31"

            response = self.http_client.get(
                f"{self.BASE_URL}/series/observations",
                params=params
            )
            data = response.json()

            if "observations" not in data or not data["observations"]:
                return MacroDataPoint(
                    source=self.source_name,
                    metric=metric.value,
                    country=country_info.get("name", country_code),
                    country_code=country_code,
                    value=None,
                    unit="percent",
                    period="N/A",
                    retrieved_at=self._get_current_timestamp(),
                    error="No observations found"
                )

            # Get the most recent valid observation
            for obs in data["observations"]:
                if obs["value"] != ".":
                    return MacroDataPoint(
                        source=self.source_name,
                        metric=metric.value,
                        country=country_info.get("name", country_code),
                        country_code=country_code,
                        value=float(obs["value"]),
                        unit="percent",
                        period=obs["date"],
                        retrieved_at=self._get_current_timestamp(),
                        raw_response=data
                    )

            return MacroDataPoint(
                source=self.source_name,
                metric=metric.value,
                country=country_info.get("name", country_code),
                country_code=country_code,
                value=None,
                unit="percent",
                period="N/A",
                retrieved_at=self._get_current_timestamp(),
                error="All observations are missing values"
            )

        except requests.RequestException as e:
            logger.error(f"FRED API error for {metric.value}/{country_code}: {e}")
            return MacroDataPoint(
                source=self.source_name,
                metric=metric.value,
                country=country_info.get("name", country_code),
                country_code=country_code,
                value=None,
                unit="percent",
                period="N/A",
                retrieved_at=self._get_current_timestamp(),
                error=str(e)
            )