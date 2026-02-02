"""
OECD Data API (SDMX-JSON) client.
"""

import logging
from typing import Optional

import requests

from ..config import MetricType, MacroDataPoint
from ..mappings import COUNTRY_MAPPINGS, METRIC_MAPPINGS
from .base import MacroDataClient


logger = logging.getLogger(__name__)


class OECDClient(MacroDataClient):
    """Client for OECD Data API (SDMX-JSON)."""

    BASE_URL = "https://sdmx.oecd.org/public/rest/data"

    def __init__(self):
        super().__init__()  # OECD API doesn't require a key

    @property
    def source_name(self) -> str:
        return "OECD"

    def fetch_metric(
        self,
        metric: MetricType,
        country_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> MacroDataPoint:
        """Fetch metric from OECD API."""
        country_info = COUNTRY_MAPPINGS.get(country_code, {"name": country_code})
        oecd_country = country_info.get("oecd", country_code)

        try:
            # Build OECD data query
            dataset_path = METRIC_MAPPINGS[metric]["oecd"].format(country=oecd_country)

            params = {
                "dimensionAtObservation": "AllDimensions",
            }

            if start_year:
                params["startPeriod"] = str(start_year)
            if end_year:
                params["endPeriod"] = str(end_year)

            headers = {"Accept": "application/vnd.sdmx.data+json;version=1.0"}

            response = self.http_client.get(
                f"{self.BASE_URL}/{dataset_path}",
                params=params,
                headers=headers
            )
            data = response.json()

            # Parse SDMX-JSON response
            datasets = data.get("dataSets", [])
            if not datasets:
                return MacroDataPoint(
                    source=self.source_name,
                    metric=metric.value,
                    country=country_info.get("name", country_code),
                    country_code=country_code,
                    value=None,
                    unit="percent",
                    period="N/A",
                    retrieved_at=self._get_current_timestamp(),
                    error="No datasets in response"
                )

            # Extract observations
            observations = datasets[0].get("observations", {})
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
                    error="No observations in dataset"
                )

            # Get the most recent observation (last key)
            last_key = sorted(observations.keys())[-1]
            value = observations[last_key][0]

            # Extract period from structure
            structure = data.get("structure", {})
            dimensions = structure.get("dimensions", {}).get("observation", [])
            time_dim = next((d for d in dimensions if d.get("id") == "TIME_PERIOD"), None)
            period = "N/A"
            if time_dim and time_dim.get("values"):
                period_idx = int(last_key.split(":")[-1]) if ":" in last_key else 0
                if period_idx < len(time_dim["values"]):
                    period = time_dim["values"][period_idx].get("id", "N/A")

            return MacroDataPoint(
                source=self.source_name,
                metric=metric.value,
                country=country_info.get("name", country_code),
                country_code=country_code,
                value=float(value) if value is not None else None,
                unit="percent",
                period=period,
                retrieved_at=self._get_current_timestamp(),
                raw_response=data
            )

        except requests.RequestException as e:
            logger.error(f"OECD API error for {metric.value}/{country_code}: {e}")
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