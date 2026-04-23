# fetch.py
import time
import logging
from typing import Optional, Dict

import requests

from config import (
    USE_PROXY,
    PROXY_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    BACKOFF_FACTOR,
)


logger = logging.getLogger(__name__)


def get_proxies() -> Optional[Dict[str, str]]:
    if not USE_PROXY:
        return None
    return {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }


def fetch_page(url: str, params: Optional[Dict] = None) -> str:
    proxies = get_proxies()
    attempt = 0
    backoff = 1.0

    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            logger.info(
                "Requesting %s (attempt %d, proxy=%s)",
                url, attempt, bool(proxies)
            )
            resp = requests.get(
                url,
                params=params,
                proxies=proxies,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            return resp.text

        except requests.exceptions.ProxyError as e:
            logger.error("Proxy error on attempt %d: %s", attempt, e)
        except requests.exceptions.RequestException as e:
            logger.error("Request error on attempt %d: %s", attempt, e)

        time.sleep(backoff)
        backoff *= BACKOFF_FACTOR

    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts")
