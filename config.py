# config.py

# -----------------------------
# Target domain configuration
# -----------------------------
TARGET_URL = "https://example.com/search"
TARGET_LINK_PREFIX = "https://example.com/"

# -----------------------------
# Selector configuration
# -----------------------------
SELECTORS = {
    "item": "a[href]",
    "link_attr": "href",
    "title": None,
    "context_parent": None,
}

# -----------------------------
# Scoring thresholds
# -----------------------------
SIZE_THRESHOLD_BOOST_MB = 500      # boost score if >= this size
SIZE_ANOMALY_MB = 4096             # mark as anomaly if >= this size

# -----------------------------
# Filtering thresholds
# -----------------------------
EXCLUSION_LIST = EXCLUSION_KEYWORDS
SIZE_THRESHOLD_MIN_MB = 10         # exclude items smaller than this

# -----------------------------
# Drift detection configuration
# -----------------------------
DRIFT_CONFIG = {
    "min_items_warning": 3,
    "history_file": "dom_drift_history.json",
    "max_history": 50,
}

# -----------------------------
# Keyword scoring configuration
# -----------------------------
PRIORITY_KEYWORDS = {
    "critical": ["iso", "release", "final"],
    "strong": ["update", "patch", "installer"],
    "weak": ["misc", "notes"],
}

EXCLUSION_KEYWORDS = ["beta", "old", "deprecated"]

# -----------------------------
# Size detection configuration
# -----------------------------
SIZE_KEYWORDS = ["mb", "gb", "kb"]

# -----------------------------
# Export configuration
# -----------------------------
EXPORT_JSON = "results.json"
EXPORT_CSV = "results.csv"

# -----------------------------
# Summary configuration
# -----------------------------
TOP_N_SUMMARY = 5

# -----------------------------
# Proxy configuration
# -----------------------------
USE_TOR_PROXY = False
TOR_PROXY = "socks5h://127.0.0.1:9050"

# -----------------------------
# Request / Retry configuration
# -----------------------------
REQUEST_TIMEOUT = 10
MAX_RETRIES = 5
BACKOFF_FACTOR = 1.5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AdaptiveScraper/1.0)"
}

# -----------------------------
# Logging configuration
# -----------------------------
LOG_FILE = "scraper.log"
