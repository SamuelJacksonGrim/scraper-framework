# scraper-framework

A modular, adaptive web scraper framework built for real-world instability. Targets a single configurable URL, extracts and scores results by keyword relevance and file size, detects DOM drift between runs, and exports to JSON/CSV. All behavior is driven by `config.py` — no code changes required to target a new site.

In the Resonance Family stack, this is the **optional external world input layer** — the top of the data flow diagram, feeding structured content events into rfe-core2 for cognitive field inference.

---

## Quickstart

```bash
git clone https://github.com/SamuelJacksonGrim/scraper-framework.git
cd scraper-framework
pip install -r requirements.txt
python main.py
```

Outputs:
- Terminal (colorized if `colorama` is installed)
- `results_YYYYMMDD_HHMM.json`
- `results_YYYYMMDD_HHMM.csv`
- `scraper.log`

---

## Architecture

```
config.py          All configuration (URL, selectors, keywords, thresholds, export)
    ↓
fetch.py           HTTP fetch with retry/backoff, optional Tor SOCKS5h proxy
    ↓
parse.py           BeautifulSoup DOM parsing, drift detection, per-item extraction
    ├── scoring.py    Keyword score + size score + confidence heuristic
    └── filters.py    Exclusion keyword filtering
    ↓
ui.py              Colorized terminal output, result and summary display
exporter.py        JSON + CSV export with timestamps
```

---

## Module reference

### `config.py` — single configuration source

| Setting | Default | Purpose |
|---------|---------|----------|
| `TARGET_URL` | `https://example.com/search` | Base URL for `?q=query` requests |
| `TARGET_LINK_PREFIX` | `https://example.com/` | Only keep links starting with this |
| `SELECTORS["item"]` | `"a[href]"` | CSS selector for result items |
| `SELECTORS["link_attr"]` | `"href"` | Attribute on item tag containing the link |
| `SELECTORS["title"]` | `None` | Optional CSS selector for title (falls back to tag text) |
| `SELECTORS["context_parent"]` | `None` | Optional parent selector for context extraction |
| `DRIFT_CONFIG["min_items_warning"]` | `3` | Warn if fewer items matched |
| `DRIFT_CONFIG["history_file"]` | `dom_drift_history.json` | Drift snapshot storage |
| `DRIFT_CONFIG["max_history"]` | `50` | Max snapshots to retain |
| `PRIORITY_KEYWORDS["critical"]` | `["iso", "release", "final"]` | +4 per hit |
| `PRIORITY_KEYWORDS["strong"]` | `["update", "patch", "installer"]` | +2 per hit |
| `PRIORITY_KEYWORDS["weak"]` | `["misc", "notes"]` | +1 per hit |
| `EXCLUSION_KEYWORDS` | `["beta", "old", "deprecated"]` | Discard any result matching these |
| `SIZE_THRESHOLD_MIN_MB` | `10` | Exclude results with parsed size below this |
| `SIZE_THRESHOLD_BOOST_MB` | `500` | +3 size score if size ≥ this |
| `SIZE_ANOMALY_MB` | `4096` | Mark as anomaly if size ≥ this |
| `USE_TOR_PROXY` | `False` | Route via Tor SOCKS5h |
| `TOR_PROXY` | `socks5h://127.0.0.1:9050` | Tor proxy address |
| `REQUEST_TIMEOUT` | `10` | HTTP timeout in seconds |
| `MAX_RETRIES` | `5` | Retry attempts on failure |
| `BACKOFF_FACTOR` | `1.5` | Exponential backoff multiplier |
| `HEADERS["User-Agent"]` | `Mozilla/5.0 compatible` | Request headers |

### `fetch.py` — HTTP with retry

- `fetch_page(url, params)` — sends `GET url?q=query`, returns raw HTML string
- Retries up to `MAX_RETRIES` times with exponential backoff (`BACKOFF_FACTOR`)
- Applies Tor SOCKS5h proxy if `USE_TOR_PROXY = True`
- `socks5h://` ensures DNS resolution happens inside Tor (required for .onion domains)

### `parse.py` — DOM parsing and drift detection

`parse_results(html)` — main entry point. Returns `List[Dict]` sorted by `(score, confidence)` DESC.

Per-item extraction:
1. Select all items matching `SELECTORS["item"]`
2. Extract `href` via `SELECTORS["link_attr"]`; discard if not starting with `TARGET_LINK_PREFIX`
3. Extract title via `SELECTORS["title"]` selector (or fall back to tag text)
4. Apply `filters.should_exclude_item(title)` — discard if any exclusion keyword matches
5. Call `scoring.compute_total_score(title)` for keyword, size, confidence scores
6. Extract optional context from `SELECTORS["context_parent"]` (or parent tag), max 200 chars

**DOM drift detection**:
- After each run, records `{timestamp, item_count, selector}` to `dom_drift_history.json`
- Computes ratio of current item count to rolling average of last 10 runs
- If `ratio < 0.3`: prints `[!] DOM drift warning` (selector may have changed)
- If `item_count < min_items_warning`: prints a separate warning
- Drift history persists across runs; max 50 snapshots retained (FIFO)

### `scoring.py` — scoring functions

**Size parsing**: `parse_numeric_metric(text)` — regex extracts `NNN GB/MB/KB` from title, converts all to MB.

**Keyword score**: `keyword_score(title)` — case-insensitive substring match against all PRIORITY_KEYWORDS tiers:
```
critical match: +4 per word
strong match:   +2 per word
weak match:     +1 per word
```

**Size score**: `size_score(size_mb)` — `+3` if `size_mb >= SIZE_THRESHOLD_BOOST_MB`, else `0`.

**Confidence**: `compute_confidence(title, size_mb)` — heuristic:
```python
base = keyword_score(title)
if size_mb is not None: base += 2
density = base / max(len(title), 10)
confidence = clip(density * 5, 0.0, 1.0)
```

**Total score**: `total_score = keyword_score + size_score`

**Anomaly flag**: `is_anomalous_size(size_mb)` — `True` if `size_mb >= SIZE_ANOMALY_MB`.

### Result item data model

Each item in the returned list:

```python
{
    "title":        str,            # extracted title text
    "link":         str,            # full URL
    "score":        int,            # total score (keyword + size)
    "confidence":   float,          # [0, 1] heuristic
    "size_mb":      Optional[float],# parsed file size in MB (None if not found)
    "keyword_score":int,            # keyword component
    "size_score":   int,            # size component (0 or 3)
    "anomaly":      bool,           # True if size_mb >= SIZE_ANOMALY_MB
    "context":      str,            # up to 200 chars of surrounding text
    "timestamp":    str,            # ISO 8601 timestamp of this run
}
```

### `filters.py`

`should_exclude_item(title)` — returns `True` if any keyword in `EXCLUSION_LIST` appears in `title.lower()`.

### `ui.py`

`print_results(results, query)` — prints each result with label (HIGH PRIORITY / RELEVANT / WEAK), score, confidence, size, and link. Uses colorama if available.

`print_summary(results)` — prints top N results by score (configurable via `TOP_N_SUMMARY`).

### `exporter.py`

`export_json(results)` and `export_csv(results)` — write to timestamped filenames (`results_YYYYMMDD_HHMM.json/.csv`). Each result includes all fields from the data model.

---

## Adapting to a new site

All changes in `config.py` only:

```python
TARGET_URL          = "https://somesite.com/search"
TARGET_LINK_PREFIX  = "https://somesite.com/"
SELECTORS = {
    "item":           ".result-item",
    "link_attr":      "href",
    "title":          ".title",
    "context_parent": ".description",
}
PRIORITY_KEYWORDS = {
    "critical": ["stable", "LTS"],
    "strong":   ["update", "release"],
    "weak":     ["info", "notes"],
}
SIZE_THRESHOLD_MIN_MB  = 5
SIZE_THRESHOLD_BOOST_MB = 500
SIZE_ANOMALY_MB         = 4096
```

Then `python main.py`.

---

## Tor proxy

```python
USE_TOR_PROXY = True
TOR_PROXY = "socks5h://127.0.0.1:9050"  # default Tor Browser/service port
```

`socks5h://` (not `socks5://`) routes DNS through Tor, which is required for .onion addresses and for anonymizing the DNS lookup on clearnet addresses.

---

## Stack integration context

In the Resonance Family data flow:

```
[scraper-framework]  ← you are here
        ↓ JSON events
[rfe-core2 :8000]    cognitive field inference
        ↓ StepResponse
[sovereign_manifold] relational dynamics engine
```

scraper-framework provides the optional external world signal. Its scored result items can be fed into rfe-core2 as token sequences or event payloads, modulating what the cognitive field engine "thinks about" on a given cycle. The pipeline from scraper output to rfe-core2 input is not yet automated — currently manual or ad-hoc. The framework is designed to be run on a schedule (cron, Task Scheduler, etc.) with results exported for downstream ingestion.

---

## Requirements

```
beautifulsoup4
requests
```

Optional: `colorama` (terminal colors), `stem` (Tor control), `requests[socks]` (SOCKS proxy support).

---

## License

MIT License — see LICENSE for details.
