# scoring.py
import re
from typing import Optional, Dict

from config import (
    PRIORITY_KEYWORDS,
    SIZE_THRESHOLD_BOOST_MB,
    SIZE_ANOMALY_MB,
)

SIZE_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(GB|MB|KB|TB)', re.IGNORECASE)

# Directory listings (Apache autoindex, nginx, `ls -h`) render sizes with a
# bare suffix and no "B": "3.7G", "4.2K". This pattern is deliberately NOT used
# on titles - in free text "4K" and "5G" are resolutions and network standards,
# and reading them as sizes would push real items under SIZE_THRESHOLD_MIN_MB
# and silently drop them. It is applied only to structured context such as a
# listing's size column.
SIZE_PATTERN_LOOSE = re.compile(r'(\d+(?:\.\d+)?)\s*([KMGT])B?\b', re.IGNORECASE)

_UNIT_TO_MB = {"K": 1 / 1024, "M": 1.0, "G": 1024.0, "T": 1024.0 * 1024.0}


def parse_numeric_metric(text_data: str, loose: bool = False) -> Optional[float]:
    """
    Parse a size from text and return it in MB.

    Supports KB/MB/GB/TB. With `loose=True`, also accepts the bare suffixes
    used by directory listings ("3.7G"). Use loose only on structured context,
    never on a free-text title - see the note on SIZE_PATTERN_LOOSE.
    """
    pattern = SIZE_PATTERN_LOOSE if loose else SIZE_PATTERN
    match = pattern.search(text_data)
    if not match:
        return None

    val = float(match.group(1))
    unit = match.group(2).upper()[0]
    return val * _UNIT_TO_MB[unit]


def keyword_score(title: str) -> int:
    title_low = title.lower()
    score = 0

    weights: Dict[str, int] = {
        "critical": 4,
        "strong": 2,
        "weak": 1,
    }

    for tier, words in PRIORITY_KEYWORDS.items():
        weight = weights.get(tier, 1)
        for w in words:
            if w.lower() in title_low:
                score += weight

    return score


def size_score(size_mb: Optional[float]) -> int:
    if size_mb is None:
        return 0
    if size_mb >= SIZE_THRESHOLD_BOOST_MB:
        return 3
    return 0


def compute_confidence(title: str, size_mb: Optional[float]) -> float:
    """
    Simple heuristic confidence:
    - more keyword hits -> higher
    - having a parsed size -> higher
    - normalized by title length
    """
    base = keyword_score(title)
    if size_mb is not None:
        base += 2

    length = max(len(title), 10)
    density = base / length

    # Clamp to [0, 1]
    return max(0.0, min(1.0, density * 5))


def is_anomalous_size(size_mb: Optional[float]) -> bool:
    if size_mb is None:
        return False
    return size_mb >= SIZE_ANOMALY_MB


def compute_total_score(title: str, context: str = "") -> Dict[str, float]:
    """
    Score an item.

    `context` is the surrounding text of the item (e.g. the rest of the table
    row on a directory listing). Sizes are frequently rendered in a sibling
    column rather than in the link text, so the title alone often carries no
    size at all. Falling back to context is what keeps size_score, the anomaly
    flag and the minimum-size filter alive on those pages.
    """
    size_mb = parse_numeric_metric(title)
    if size_mb is None and context:
        size_mb = parse_numeric_metric(context, loose=True)
    kw_score = keyword_score(title)
    sz_score = size_score(size_mb)
    total = kw_score + sz_score
    confidence = compute_confidence(title, size_mb)
    anomaly = is_anomalous_size(size_mb)

    return {
        "size_mb": size_mb,
        "keyword_score": kw_score,
        "size_score": sz_score,
        "total_score": total,
        "confidence": confidence,
        "anomaly": anomaly,
    }
