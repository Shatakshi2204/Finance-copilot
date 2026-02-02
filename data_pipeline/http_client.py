"""
Robust HTTP client with retry logic and rate limiting.
"""

import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RobustHTTPClient:
    """HTTP client with retry logic and rate limiting."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        timeout: int = 30,
        rate_limit_delay: float = 0.5
    ):
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> requests.Response:
        """Make GET request with rate limiting."""
        time.sleep(self.rate_limit_delay)
        response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response