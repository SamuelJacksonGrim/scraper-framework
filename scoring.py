# scoring.py
import re
from typing import Optional, Dict

from config import (
    PRIORITY_KEYWORDS,
    SIZE_THRESHOLD_BOOST_MB,
    SIZE_ANOMALY_MB,
)

SIZE_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(GB|MB|KB)', re.IGNORECASE)


def parse_numeric_metric(text_data: str) -> Optional[float]:
    """
    Parse size from text and return MB.
    Supports GB, MB, KB.
    """
    match = SIZE_PATTERN.search(text_data)
    if not match:
        return None

    val = float(match.group(1))
    unit = match.group(2).upper()

    if unit == "GB":
        return val * 1024
    if unit == "KB":
        return val / 1024
    return val  # MB


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


def compute_total_score(title: str) -> Dict[str, float]:
    size_mb = parse_numeric_metric(title)
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
