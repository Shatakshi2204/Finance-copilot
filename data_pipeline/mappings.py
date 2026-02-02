"""
Country and metric mappings for API clients.
"""

from .config import MetricType


# ============================================================================
# COUNTRY & METRIC MAPPINGS
# ============================================================================

# ISO country codes to names and API-specific codes
# Target countries: USA, India, European Union, China
COUNTRY_MAPPINGS = {
    "USA": {"name": "United States", "fred": "USA", "wb": "USA", "oecd": "USA"},
    "IND": {"name": "India", "fred": "IND", "wb": "IND", "oecd": "IND"},
    "EUU": {"name": "European Union", "fred": "EUU", "wb": "EUU", "oecd": "EA20"},
    "CHN": {"name": "China", "fred": "CHN", "wb": "CHN", "oecd": "CHN"},
}

# Metric mappings per API
METRIC_MAPPINGS = {
    MetricType.GDP_GROWTH: {
        "fred": {
            "USA": "A191RL1Q225SBEA",    # US Real GDP Growth Rate
            "IND": "INDGDPRQPSMEI",       # India GDP Growth
            "EUU": "CLVMNACSCAB1GQEA19",  # Euro Area GDP
            "CHN": "CHNGDPRQPSMEI",       # China GDP Growth
            "default": "CLVMNACSCAB1GQ{country}",
        },
        "worldbank": "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
        "oecd": "QNA/B1_GE.{country}.VOBARSA.Q",  # Quarterly GDP
    },
    MetricType.INFLATION: {
        "fred": {
            "USA": "CPIAUCSL",             # US CPI
            "IND": "INDCPIALLMINMEI",      # India CPI
            "EUU": "CP0000EZ19M086NEST",   # Euro Area HICP
            "CHN": "CHNCPIALLMINMEI",      # China CPI
            "default": "CPALTT01{country}M659N",
        },
        "worldbank": "FP.CPI.TOTL.ZG",  # Inflation, consumer prices (annual %)
        "oecd": "PRICES_CPI/CPALTT01.{country}.GP.A",
    },
    MetricType.UNEMPLOYMENT: {
        "fred": {
            "USA": "UNRATE",               # US Unemployment Rate
            "IND": "LMUNRRTTINQ156S",      # India Unemployment Rate
            "EUU": "LRHUTTTTEZM156S",      # Euro Area Unemployment
            "CHN": "LMUNRRTTCNM156S",      # China Unemployment Rate
            "default": "LRUN64TT{country}Q156S",
        },
        "worldbank": "SL.UEM.TOTL.ZS",  # Unemployment, total (% of labor force)
        "oecd": "LFS_SEXAGE_I_R/{country}.MW.Y15T64.UR.A",
    },
    MetricType.INTEREST_RATE: {
        "fred": {
            "USA": "FEDFUNDS",             # US Federal Funds Rate
            "IND": "INDIRLTLT01STM",       # India Interest Rate
            "EUU": "ECBMRRFR",             # ECB Main Refinancing Rate
            "CHN": "INTDSRCNM193N",        # China Interest Rate
            "default": "IR3TIB01{country}M156N",
        },
        "worldbank": "FR.INR.RINR",  # Real interest rate (%)
        "oecd": "MEI_FIN/{country}.IRSTCI.ST.M",
    },
}