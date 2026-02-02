"""
World Bank Open Data API client.
"""

import logging
from datetime import datetime
from typing import Optional

import requests

from ..config import MetricType, MacroDataPoint
from ..mappings import COUNTRY_MAPPINGS, METRIC_MAPPINGS
from .base import MacroDataClient


logger = logging.getLogger(__name__)


class WorldBankClient(MacroDataClient):
    """Client for World Bank Open Data API."""

    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self):
        super().__init__()  # World Bank API doesn't require a key

    @property
    def source_name(self) -> str:
        return "World Bank"

    def fetch_metric(
        self,
        metric: MetricType,
        country_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> MacroDataPoint:
        """Fetch metric from World Bank API."""
        indicator = METRIC_MAPPINGS[metric]["worldbank"]
        country_info = COUNTRY_MAPPINGS.get(country_code, {"name": country_code})
        wb_country = country_info.get("wb", country_code)

        try:
            # Build date range
            current_year = datetime.now().year
            date_range = f"{start_year or current_year - 5}:{end_year or current_year}"

            params = {
                "format": "json",
                "per_page": 10,
                "date": date_range,
            }

            response = self.http_client.get(
                f"{self.BASE_URL}/country/{wb_country}/indicator/{indicator}",
                params=params
            )
            data = response.json()

            # World Bank returns [metadata, data] or error
            if not isinstance(data, list) or len(data) < 2:
                return MacroDataPoint(
                    source=self.source_name,
                    metric=metric.value,
                    country=country_info.get("name", country_code),
                    country_code=country_code,
                    value=None,
                    unit="percent",
                    period="N/A",
                    retrieved_at=self._get_current_timestamp(),
                    error="Invalid API response format"
                )

            observations = data[1]
            if not observations:
                return MacroDataPoint(
                    source=self.source_name,
                    metric=metric.value,
                    country=country_info.get("name", country_code),
                    country_code=country_code,
                    value=None,
                    unit="percent",
                    period="N/A",
                    retrieved_at=self._get_current_timestamp(),
                    error="No data available"
                )

            # Find most recent non-null value
            for obs in observations:
                if obs.get("value") is not None:
                    return MacroDataPoint(
                        source=self.source_name,
                        metric=metric.value,
                        country=country_info.get("name", country_code),
                        country_code=country_code,
                        value=float(obs["value"]),
                        unit="percent",
                        period=obs.get("date", "N/A"),
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
                error="All values are null"
            )

        except requests.RequestException as e:
            logger.error(f"World Bank API error for {metric.value}/{country_code}: {e}")
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