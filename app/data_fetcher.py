"""
Data Fetcher
============
Fetches live macroeconomic data from FRED, World Bank, and OECD APIs.
Fixed with correct series IDs and OECD implementation.
"""

import logging
import streamlit as st
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import api_config, app_config

logger = logging.getLogger(__name__)


@dataclass
class MacroDataPoint:
    """Represents a macroeconomic data point."""
    source: str
    metric: str
    country: str
    country_code: str
    value: Optional[float]
    unit: str
    period: str
    retrieved_at: str
    error: Optional[str] = None


@dataclass
class TriangulatedData:
    """Triangulated data from multiple sources."""
    metric: str
    country: str
    country_code: str
    period: str
    confidence: str
    consensus_value: Optional[float]
    fred_value: Optional[float]
    worldbank_value: Optional[float]
    oecd_value: Optional[float]
    explanation: str


# =============================================================================
# FRED Series IDs - CORRECTED
# FRED primarily has US data. For other countries, we use what's available.
# =============================================================================
FRED_SERIES = {
    "gdp_growth": {
        "USA": "A191RL1Q225SBEA",      # Real GDP Growth Rate (Quarterly)
        # India, China, EU - FRED doesn't have direct GDP growth, use World Bank
    },
    "inflation": {
        "USA": "CPIAUCSL",              # CPI All Urban Consumers
        "IND": "INDCPIALLMINMEI",       # India CPI (this one works)
        "CHN": "CHNCPIALLMINMEI",       # China CPI (this one works)
        "EUU": "CP0000EZ19M086NEST",    # Euro Area HICP
    },
    "unemployment": {
        "USA": "UNRATE",                # US Unemployment Rate
        "EUU": "LRHUTTTTEZM156S",       # Euro Area Unemployment
        # India, China - limited data in FRED
    },
    "interest_rate": {
        "USA": "FEDFUNDS",              # Federal Funds Rate
        "EUU": "ECBMRRFR",              # ECB Main Refinancing Rate
        "CHN": "INTDSRCNM193N",         # China Interest Rate
    }
}

# =============================================================================
# World Bank Indicators - Works for ALL countries
# =============================================================================
WORLDBANK_INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
    "inflation": "FP.CPI.TOTL.ZG",       # Inflation, consumer prices (annual %)
    "unemployment": "SL.UEM.TOTL.ZS",    # Unemployment, total (% of labor force)
    "interest_rate": "FR.INR.RINR"       # Real interest rate (%)
}

# World Bank country codes mapping
WB_COUNTRY_CODES = {
    "USA": "US",
    "IND": "IN", 
    "CHN": "CN",
    "EUU": "EMU"  # Euro Area
}

# =============================================================================
# OECD Dataset IDs - NEW IMPLEMENTATION
# =============================================================================
OECD_DATASETS = {
    "gdp_growth": {
        "dataset": "QNA",  # Quarterly National Accounts
        "subject": "B1_GE",  # GDP
        "measure": "GPSA",   # Growth rate
    },
    "inflation": {
        "dataset": "PRICES_CPI",
        "subject": "CPALTT01",  # CPI All items
        "measure": "GY",        # Growth rate year-on-year
    },
    "unemployment": {
        "dataset": "LFS_SEXAGE_I_R", 
        "subject": "UNE_RATE",
        "measure": "PC_LF",
    },
    "interest_rate": {
        "dataset": "MEI_FIN",
        "subject": "IRSTCI",  # Short-term interest rate
        "measure": "PA",
    }
}

# OECD country codes
OECD_COUNTRY_CODES = {
    "USA": "USA",
    "IND": "IND",
    "CHN": "CHN",
    "EUU": "EA19"  # Euro Area 19
}

# =============================================================================
# Fallback data (when all APIs fail)
# =============================================================================
FALLBACK_DATA = {
    "gdp_growth": {"USA": 2.5, "IND": 6.8, "EUU": 0.5, "CHN": 5.2},
    "inflation": {"USA": 3.4, "IND": 5.1, "EUU": 2.6, "CHN": 0.2},
    "unemployment": {"USA": 3.7, "IND": 7.8, "EUU": 6.4, "CHN": 5.1},
    "interest_rate": {"USA": 5.33, "IND": 6.5, "EUU": 4.0, "CHN": 3.45}
}


class DataFetcher:
    """Fetches and triangulates macro data from multiple sources."""
    
    _session = None
    
    def __init__(self):
        if DataFetcher._session is None:
            DataFetcher._session = self._create_session()
        self.session = DataFetcher._session
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _get_timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"
    
    def _get_fallback(self, metric: str, country_code: str) -> Optional[float]:
        return FALLBACK_DATA.get(metric, {}).get(country_code)

    # =========================================================================
    # FRED API
    # =========================================================================
    def fetch_fred(self, metric: str, country_code: str) -> MacroDataPoint:
        """Fetch data from FRED API."""
        country_name = app_config.countries.get(country_code, country_code)
        
        if not api_config.fred_api_key:
            return self._empty_datapoint("FRED", metric, country_name, country_code, "API key not configured")
        
        series_id = FRED_SERIES.get(metric, {}).get(country_code)
        if not series_id:
            # FRED doesn't have this data - not an error, just no data
            return self._empty_datapoint("FRED", metric, country_name, country_code, None)
        
        try:
            params = {
                "series_id": series_id,
                "api_key": api_config.fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 5
            }
            
            response = self.session.get(
                f"{api_config.fred_base_url}/series/observations",
                params=params,
                timeout=api_config.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            for obs in data.get("observations", []):
                if obs.get("value") and obs["value"] != ".":
                    return MacroDataPoint(
                        source="FRED",
                        metric=metric,
                        country=country_name,
                        country_code=country_code,
                        value=float(obs["value"]),
                        unit="percent",
                        period=obs["date"],
                        retrieved_at=self._get_timestamp()
                    )
            
            return self._empty_datapoint("FRED", metric, country_name, country_code, "No data")
            
        except Exception as e:
            logger.warning(f"FRED error for {metric}/{country_code}: {e}")
            return self._empty_datapoint("FRED", metric, country_name, country_code, str(e))

    # =========================================================================
    # World Bank API
    # =========================================================================
    def fetch_worldbank(self, metric: str, country_code: str) -> MacroDataPoint:
        """Fetch data from World Bank API."""
        country_name = app_config.countries.get(country_code, country_code)
        indicator = WORLDBANK_INDICATORS.get(metric)
        wb_country = WB_COUNTRY_CODES.get(country_code, country_code)
        
        if not indicator:
            return self._empty_datapoint("World Bank", metric, country_name, country_code, "No indicator")
        
        try:
            current_year = datetime.now().year
            response = self.session.get(
                f"{api_config.worldbank_base_url}/country/{wb_country}/indicator/{indicator}",
                params={"format": "json", "per_page": 10, "date": f"{current_year-5}:{current_year}"},
                timeout=api_config.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) >= 2 and data[1]:
                for obs in data[1]:
                    if obs.get("value") is not None:
                        return MacroDataPoint(
                            source="World Bank",
                            metric=metric,
                            country=country_name,
                            country_code=country_code,
                            value=float(obs["value"]),
                            unit="percent",
                            period=obs.get("date", "N/A"),
                            retrieved_at=self._get_timestamp()
                        )
            
            return self._empty_datapoint("World Bank", metric, country_name, country_code, "No data")
            
        except Exception as e:
            logger.warning(f"World Bank error for {metric}/{country_code}: {e}")
            return self._empty_datapoint("World Bank", metric, country_name, country_code, str(e))

    # =========================================================================
    # OECD API - NEW IMPLEMENTATION
    # =========================================================================
    def fetch_oecd(self, metric: str, country_code: str) -> MacroDataPoint:
        """Fetch data from OECD API."""
        country_name = app_config.countries.get(country_code, country_code)
        oecd_config = OECD_DATASETS.get(metric)
        oecd_country = OECD_COUNTRY_CODES.get(country_code)
        
        if not oecd_config or not oecd_country:
            return self._empty_datapoint("OECD", metric, country_name, country_code, None)
        
        try:
            # OECD SDMX REST API
            dataset = oecd_config["dataset"]
            
            # Build the SDMX query URL
            # Format: https://sdmx.oecd.org/public/rest/data/{dataset}/{filter}
            url = f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_KEI@DF_KEI,4.0/{oecd_country}.{oecd_config['subject']}..{oecd_config['measure']}"
            
            headers = {"Accept": "application/json"}
            response = self.session.get(url, headers=headers, timeout=api_config.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse SDMX-JSON format
                try:
                    observations = data.get("data", {}).get("dataSets", [{}])[0].get("observations", {})
                    if observations:
                        # Get the most recent observation
                        latest_key = list(observations.keys())[-1]
                        value = observations[latest_key][0]
                        
                        return MacroDataPoint(
                            source="OECD",
                            metric=metric,
                            country=country_name,
                            country_code=country_code,
                            value=float(value),
                            unit="percent",
                            period="Latest",
                            retrieved_at=self._get_timestamp()
                        )
                except:
                    pass
            
            return self._empty_datapoint("OECD", metric, country_name, country_code, "No data")
            
        except Exception as e:
            logger.warning(f"OECD error for {metric}/{country_code}: {e}")
            return self._empty_datapoint("OECD", metric, country_name, country_code, str(e))

    # =========================================================================
    # Helper Methods
    # =========================================================================
    def _empty_datapoint(self, source: str, metric: str, country: str, code: str, error: Optional[str]) -> MacroDataPoint:
        return MacroDataPoint(
            source=source,
            metric=metric,
            country=country,
            country_code=code,
            value=None,
            unit="percent",
            period="N/A",
            retrieved_at=self._get_timestamp(),
            error=error
        )

    # =========================================================================
    # Triangulation - Combines all sources
    # =========================================================================
    def triangulate(self, metric: str, country_code: str) -> TriangulatedData:
        """Fetch and triangulate data from all three sources."""
        country_name = app_config.countries.get(country_code, country_code)
        
        # Fetch from all sources
        fred_data = self.fetch_fred(metric, country_code)
        wb_data = self.fetch_worldbank(metric, country_code)
        oecd_data = self.fetch_oecd(metric, country_code)
        
        # Collect valid values
        values = []
        sources_used = []
        
        if fred_data.value is not None:
            values.append(fred_data.value)
            sources_used.append(f"FRED ({fred_data.value:.2f}%)")
        if wb_data.value is not None:
            values.append(wb_data.value)
            sources_used.append(f"World Bank ({wb_data.value:.2f}%)")
        if oecd_data.value is not None:
            values.append(oecd_data.value)
            sources_used.append(f"OECD ({oecd_data.value:.2f}%)")
        
        # Determine confidence and consensus
        if len(values) == 0:
            fallback = self._get_fallback(metric, country_code)
            return TriangulatedData(
                metric=metric,
                country=country_name,
                country_code=country_code,
                period="2024 (cached)",
                confidence="fallback",
                consensus_value=fallback,
                fred_value=None,
                worldbank_value=None,
                oecd_value=None,
                explanation="Using cached data (APIs unavailable)"
            )
        
        consensus = sum(values) / len(values)
        
        if len(values) == 1:
            confidence = "single_source"
            explanation = f"Data from {sources_used[0]}"
        elif len(values) == 2:
            # Check agreement (within 20% tolerance)
            diff = abs(values[0] - values[1]) / max(abs(values[0]), abs(values[1]), 0.1) * 100
            confidence = "high" if diff <= 20 else "medium"
            explanation = f"Sources: {', '.join(sources_used)}"
        else:  # 3 sources
            # Check agreement across all three
            avg = consensus
            max_diff = max(abs(v - avg) for v in values) / max(abs(avg), 0.1) * 100
            confidence = "high" if max_diff <= 15 else "medium"
            explanation = f"All sources: {', '.join(sources_used)}"
        
        # Get best period
        periods = [fred_data.period, wb_data.period, oecd_data.period]
        period = next((p for p in periods if p not in ["N/A", None]), "Latest")
        
        return TriangulatedData(
            metric=metric,
            country=country_name,
            country_code=country_code,
            period=period,
            confidence=confidence,
            consensus_value=consensus,
            fred_value=fred_data.value,
            worldbank_value=wb_data.value,
            oecd_value=oecd_data.value,
            explanation=explanation
        )


# Global instance
data_fetcher = DataFetcher()


@st.cache_data(ttl=3600, show_spinner=False)
def get_data(metric: str, country_code: str) -> TriangulatedData:
    """Get data with Streamlit caching (1 hour TTL)."""
    return data_fetcher.triangulate(metric, country_code)
