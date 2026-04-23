# scraper-framework

A modular, general-purpose web scraper framework with configurable scoring, filtering, and export pipelines. Features optional Tor proxy support, tiered keyword prioritization, confidence heuristics, anomaly detection, retry/backoff logic, and dual JSON/CSV export. Designed as a reusable scaffold — swap config values for any target.

---

## Structure

```
scraper-framework/
├── config.py       # All configuration — swap values here for any target
├── scoring.py      # Tiered keyword scoring, size parsing, confidence heuristics
├── filters.py      # Exclusion logic based on keywords and size thresholds
├── fetch.py        # HTTP requests with optional Tor proxy and retry/backoff
├── parse.py        # HTML parsing and result assembly
├── exporter.py     # JSON and CSV export
├── ui.py           # Terminal output with optional color via colorama
├── main.py         # Entry point
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## Requirements

- Python 3.8+
- Install dependencies:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
requests
beautifulsoup4
colorama
```

---

## Configuration

All settings live in `config.py`. You do not need to touch any other file for basic use.

| Variable | Description |
|---|---|
| `USE_PROXY` | Toggle Tor proxy on/off |
| `PROXY_URL` | Proxy address (default: Tor Browser port 9150) |
| `BASE_URL` | Target URL to scrape |
| `SEARCH_QUERY` | Search terms passed as query parameter |
| `TARGET_LINK_PREFIX` | Link prefix to match (e.g. `https://`, `magnet:?xt=`) |
| `PRIORITY_KEYWORDS` | Tiered dict of keywords that boost score (`critical`, `strong`, `weak`) |
| `EXCLUSION_LIST` | Keywords that disqualify a result entirely |
| `SIZE_THRESHOLD_MIN_MB` | Results below this size (MB) are excluded |
| `SIZE_THRESHOLD_BOOST_MB` | Results above this size get a score boost |
| `SIZE_ANOMALY_MB` | Results above this size are flagged as anomalies |

---

## Usage

```bash
python main.py
```

Results are printed to terminal and exported to timestamped `results_YYYYMMDDHHMM.json` and `.csv` files in the working directory. A `scraper.log` file is also written.

---

## Tor Proxy

If `USE_PROXY = True`, requests are routed through a local SOCKS5 proxy. The default is port `9150` (Tor Browser). If you're running the Tor service directly, change to port `9050`:

```python
PROXY_URL = "socks5h://127.0.0.1:9050"
```

The `socks5h://` prefix ensures DNS resolution happens on the proxy side, which is required for `.onion` addresses.

To disable the proxy entirely:

```python
USE_PROXY = False
```

---

## Setup from Scratch

```bash
# Clone the repo
git clone https://github.com/SamuelJacksonGrim/scraper-framework.git
cd scraper-framework

# Install dependencies
pip install -r requirements.txt

# Edit config.py with your target values, then run
python main.py
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
