"""
API clients for macro data sources.
"""

from .base import MacroDataClient
from .fred import FREDClient
from .worldbank import WorldBankClient
from .oecd import OECDClient

__all__ = [
    "MacroDataClient",
    "FREDClient",
    "WorldBankClient",
    "OECDClient",
]