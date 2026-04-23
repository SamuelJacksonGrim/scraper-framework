# filters.py
from typing import Optional, List

from config import EXCLUSION_LIST, SIZE_THRESHOLD_MIN_MB
from scoring import parse_numeric_metric


def should_exclude_item(title: str) -> bool:
    title_low = title.lower()

    # Exclusion keywords
    if any(word.lower() in title_low for word in EXCLUSION_LIST):
        return True

    # Size too small
    size_mb: Optional[float] = parse_numeric_metric(title)
    if size_mb is not None and size_mb < SIZE_THRESHOLD_MIN_MB:
        return True

    return False
