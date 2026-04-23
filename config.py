# config.py
USE_PROXY = True
PROXY_URL = "socks5h://127.0.0.1:9150"

BASE_URL = "https://example-target-url.com"
SEARCH_QUERY = "your specific search terms"
TARGET_LINK_PREFIX = "protocol:?identifier"

PRIORITY_KEYWORDS = {
    "critical": ["term1", "term2"],
    "strong": ["alpha", "beta"],
    "weak": ["misc", "other"]
}

EXCLUSION_LIST = ["skip1", "skip2"]

SIZE_THRESHOLD_MIN_MB = 90          # Minimum size to keep (MB)
SIZE_THRESHOLD_BOOST_MB = 1000      # Boost threshold (MB)
SIZE_ANOMALY_MB = 10240             # 10 GB

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 45
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0

LOG_FILE = "scraper.log"
TOP_N_SUMMARY = 5
