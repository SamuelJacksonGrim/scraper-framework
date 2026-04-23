# config.py

# -----------------------------
# Target domain configuration
# -----------------------------
TARGET_URL = "https://example.com/search?q="
TARGET_LINK_PREFIX = "https://example.com/"

# -----------------------------
# Selector configuration
# -----------------------------
# These selectors make the parser adaptable to ANY site.
# You can override them per-site later if you want.
SELECTORS = {
    # CSS selector for each result item
    "item": "a[href]",

    # Attribute containing the link
    "link_attr": "href",

    # Optional: CSS selector for the title (relative to the item)
    # None = fallback to tag text
    "title": None,

    # Optional: CSS selector for context extraction (relative to the item)
    # None = fallback to parent element
    "context_parent": None,
}

# -----------------------------
# Drift detection configuration
# -----------------------------
DRIFT_CONFIG = {
    # Warn if fewer than this many items are found
    "min_items_warning": 3,

    # Where to store historical DOM snapshots
    "history_file": "dom_drift_history.json",

    # How many snapshots to keep
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
# Proxy configuration
# -----------------------------
USE_TOR_PROXY = False
TOR_PROXY = "socks5h://127.0.0.1:9050"

# -----------------------------
# Logging configuration
# -----------------------------
LOG_FILE = "scraper.log"
