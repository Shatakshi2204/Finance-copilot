"""
Triangulation engine for cross-referencing macro data across multiple sources.
"""

import logging
from typing import Optional

from .config import MetricType, ConfidenceLevel, TriangulatedResult
from .mappings import COUNTRY_MAPPINGS
from .clients import FREDClient, WorldBankClient, OECDClient


logger = logging.getLogger(__name__)


class TriangulationEngine:
    """
    Engine for triangulating macro data across multiple sources.
    
    Confidence Logic:
    - HIGH: All available sources agree within tolerance
    - MEDIUM: Two sources agree, third differs (or only two sources available and agree)
    - LOW: All sources significantly disagree
    - SINGLE_SOURCE: Only one source returned valid data
    - NO_DATA: No sources returned valid data
    """

    def __init__(
        self,
        tolerance_percent: float = 0.5,
        fred_api_key: Optional[str] = None
    ):
        """
        Initialize triangulation engine.
        
        Args:
            tolerance_percent: Maximum percentage difference for values to be
                             considered "in agreement" (default 0.5%)
            fred_api_key: API key for FRED (can also use FRED_API_KEY env var)
        """
        self.tolerance_percent = tolerance_percent
        self.fred_client = FREDClient(api_key=fred_api_key)
        self.worldbank_client = WorldBankClient()
        self.oecd_client = OECDClient()

    def _values_agree(self, val1: float, val2: float) -> bool:
        """Check if two values agree within tolerance."""
        if val1 == 0 and val2 == 0:
            return True
        if val1 == 0 or val2 == 0:
            return abs(val1 - val2) <= self.tolerance_percent

        avg = (abs(val1) + abs(val2)) / 2
        diff_percent = abs(val1 - val2) / avg * 100
        return diff_percent <= self.tolerance_percent

    def _calculate_consensus(self, values: list[float]) -> float:
        """Calculate consensus value (median for robustness)."""
        if not values:
            return None
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        return sorted_values[n // 2]

    def _determine_confidence(
        self,
        fred_val: Optional[float],
        wb_val: Optional[float],
        oecd_val: Optional[float]
    ) -> tuple[ConfidenceLevel, str]:
        """
        Determine confidence level based on source agreement.
        
        Returns:
            Tuple of (ConfidenceLevel, explanation string)
        """
        valid_values = []
        sources = []

        if fred_val is not None:
            valid_values.append(("FRED", fred_val))
            sources.append("FRED")
        if wb_val is not None:
            valid_values.append(("World Bank", wb_val))
            sources.append("World Bank")
        if oecd_val is not None:
            valid_values.append(("OECD", oecd_val))
            sources.append("OECD")

        if len(valid_values) == 0:
            return ConfidenceLevel.NO_DATA, "No data available from any source."

        if len(valid_values) == 1:
            src, val = valid_values[0]
            return ConfidenceLevel.SINGLE_SOURCE, f"Only {src} provided data ({val:.2f}%)."

        if len(valid_values) == 2:
            src1, val1 = valid_values[0]
            src2, val2 = valid_values[1]
            if self._values_agree(val1, val2):
                return ConfidenceLevel.MEDIUM, (
                    f"{src1} ({val1:.2f}%) and {src2} ({val2:.2f}%) agree within tolerance. "
                    f"Third source unavailable for full triangulation."
                )
            else:
                return ConfidenceLevel.LOW, (
                    f"{src1} ({val1:.2f}%) and {src2} ({val2:.2f}%) disagree. "
                    f"Third source unavailable for tie-breaker."
                )

        # All three sources available
        fred_wb_agree = self._values_agree(fred_val, wb_val)
        fred_oecd_agree = self._values_agree(fred_val, oecd_val)
        wb_oecd_agree = self._values_agree(wb_val, oecd_val)

        agreements = sum([fred_wb_agree, fred_oecd_agree, wb_oecd_agree])

        if agreements == 3:
            return ConfidenceLevel.HIGH, (
                f"All three sources agree: FRED ({fred_val:.2f}%), "
                f"World Bank ({wb_val:.2f}%), OECD ({oecd_val:.2f}%)."
            )
        elif agreements >= 1:
            # Find the agreeing pair and the outlier
            if fred_wb_agree:
                return ConfidenceLevel.MEDIUM, (
                    f"FRED ({fred_val:.2f}%) and World Bank ({wb_val:.2f}%) agree. "
                    f"OECD ({oecd_val:.2f}%) differs but serves as validation."
                )
            elif fred_oecd_agree:
                return ConfidenceLevel.MEDIUM, (
                    f"FRED ({fred_val:.2f}%) and OECD ({oecd_val:.2f}%) agree. "
                    f"World Bank ({wb_val:.2f}%) differs."
                )
            else:  # wb_oecd_agree
                return ConfidenceLevel.MEDIUM, (
                    f"World Bank ({wb_val:.2f}%) and OECD ({oecd_val:.2f}%) agree. "
                    f"FRED ({fred_val:.2f}%) differs."
                )
        else:
            return ConfidenceLevel.LOW, (
                f"All sources disagree significantly: FRED ({fred_val:.2f}%), "
                f"World Bank ({wb_val:.2f}%), OECD ({oecd_val:.2f}%). "
                f"Exercise caution with this data."
            )

    def triangulate(
        self,
        metric: MetricType,
        country_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> TriangulatedResult:
        """
        Triangulate a metric across all three data sources.
        
        Args:
            metric: The macro metric to fetch
            country_code: ISO 3-letter country code
            start_year: Optional start year filter
            end_year: Optional end year filter
            
        Returns:
            TriangulatedResult with consensus value and confidence level
        """
        logger.info(f"Triangulating {metric.value} for {country_code}...")

        # Fetch from all sources
        fred_data = self.fred_client.fetch_metric(metric, country_code, start_year, end_year)
        wb_data = self.worldbank_client.fetch_metric(metric, country_code, start_year, end_year)
        oecd_data = self.oecd_client.fetch_metric(metric, country_code, start_year, end_year)

        # Log results
        logger.info(f"  FRED: {fred_data.value} ({fred_data.period})" + 
                   (f" - Error: {fred_data.error}" if fred_data.error else ""))
        logger.info(f"  World Bank: {wb_data.value} ({wb_data.period})" +
                   (f" - Error: {wb_data.error}" if wb_data.error else ""))
        logger.info(f"  OECD: {oecd_data.value} ({oecd_data.period})" +
                   (f" - Error: {oecd_data.error}" if oecd_data.error else ""))

        # Determine confidence
        confidence, explanation = self._determine_confidence(
            fred_data.value, wb_data.value, oecd_data.value
        )

        # Calculate consensus
        valid_values = [v for v in [fred_data.value, wb_data.value, oecd_data.value] if v is not None]
        consensus = self._calculate_consensus(valid_values)

        # Determine period (prefer most recent)
        periods = [d.period for d in [fred_data, wb_data, oecd_data] if d.period != "N/A"]
        period = max(periods) if periods else "N/A"

        # Build sources used list
        sources_used = []
        if fred_data.value is not None:
            sources_used.append("FRED")
        if wb_data.value is not None:
            sources_used.append("World Bank")
        if oecd_data.value is not None:
            sources_used.append("OECD")

        country_name = COUNTRY_MAPPINGS.get(country_code, {}).get("name", country_code)

        return TriangulatedResult(
            metric=metric.value,
            country=country_name,
            country_code=country_code,
            period=period,
            confidence=confidence,
            consensus_value=consensus,
            fred_value=fred_data.value,
            worldbank_value=wb_data.value,
            oecd_value=oecd_data.value,
            explanation=explanation,
            sources_used=sources_used,
            disagreement_details=None if confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM] 
                                else explanation
        )