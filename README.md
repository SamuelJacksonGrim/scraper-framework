# 📦 scraper-framework  
### Adaptive, Drift‑Resistant Web Scraper Framework

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)
![Scraping](https://img.shields.io/badge/Scraper-Modular-orange)
![Tor](https://img.shields.io/badge/Tor_Proxy-Optional-purple)

A modular, adaptive scraping framework built for real‑world instability:

- Selector‑driven parsing (swap selectors per site)
- DOM drift detection with historical snapshots
- Tiered keyword scoring (critical/strong/weak)
- Size parsing + anomaly detection
- Confidence heuristics
- Filtering rules (keywords + size thresholds)
- Retry/backoff networking
- Optional Tor proxy routing
- Colorized terminal UI
- JSON/CSV export with timestamps

Everything is configured in one file: `config.py`.

---

## 🚀 Quickstart

```bash
git clone https://github.com/SamuelJacksonGrim/scraper-framework.git
cd scraper-framework
pip install -r requirements.txt
python main.py
```

Results appear in:
- Terminal (with color if colorama is installed)
- results_YYYYMMDD_HHMM.json
- results_YYYYMMDD_HHMM.csv
- scraper.log

---

## 🧩 Project Structure

```text
scraper-framework/
├── config.py
├── scoring.py
├── filters.py
├── fetch.py
├── parse.py
├── exporter.py
├── ui.py
├── main.py
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## ⚙️ Configuration (Everything Lives in `config.py`)

### Target Settings
TARGET_URL — Base URL for the search endpoint  
TARGET_LINK_PREFIX — Only keep links starting with this prefix  

### Selector Configuration
item — CSS selector for each result item  
link_attr — Attribute containing the link  
title — Optional title selector  
context_parent — Optional parent selector for context extraction  

### Drift Detection
min_items_warning — Warn if fewer items than expected  
history_file — JSON file storing DOM snapshots  
max_history — How many snapshots to keep  

### Scoring & Filtering
PRIORITY_KEYWORDS — Tiered keyword scoring  
EXCLUSION_KEYWORDS — Keywords that disqualify a result  
EXCLUSION_LIST — Alias used by filters.py  
SIZE_THRESHOLD_MIN_MB — Exclude items smaller than this  
SIZE_THRESHOLD_BOOST_MB — Boost score if size ≥ this  
SIZE_ANOMALY_MB — Flag as anomaly if size ≥ this  

### Networking
USE_TOR_PROXY — Enable/disable Tor routing  
TOR_PROXY — SOCKS5 proxy address  
REQUEST_TIMEOUT — Request timeout  
MAX_RETRIES — Retry attempts  
BACKOFF_FACTOR — Exponential backoff multiplier  
HEADERS — Optional request headers  

### Export & Logging
EXPORT_JSON — Default JSON filename  
EXPORT_CSV — Default CSV filename  
TOP_N_SUMMARY — Items shown in summary blocks  
LOG_FILE — Log output file  

---

## 🧠 How Scoring Works

### 1. Keyword Score
Defined in PRIORITY_KEYWORDS:

```markdown
{
    "critical": ["iso", "release", "final"],
    "strong": ["update", "patch", "installer"],
    "weak": ["misc", "notes"]
}
```

Weights:  
critical = +4  
strong = +2  
weak = +1  

### 2. Size Score
If size_mb ≥ SIZE_THRESHOLD_BOOST_MB → +3  
Else → +0  

### 3. Anomaly Detection
If size_mb ≥ SIZE_ANOMALY_MB → anomaly = True  

### 4. Confidence
Heuristic combining:
- keyword density  
- presence of size  
- title length normalization  
Clamped to [0, 1].

---

## 🧭 How to Adapt This to Any Site

Modify only `config.py`.

### Step 1 — Set the Target URL
```text
TARGET_URL = "https://somesite.com/search"
```

### Step 2 — Set the Link Prefix
```text
TARGET_LINK_PREFIX = "https://somesite.com/"
```

### Step 3 — Update Selectors
```markdown
SELECTORS = {
    "item": ".result-item",
    "link_attr": "href",
    "title": ".title",
    "context_parent": ".description"
}
```

### Step 4 — Tune Scoring
```markdown
PRIORITY_KEYWORDS = {
    "critical": ["stable", "LTS"],
    "strong": ["update", "release"],
    "weak": ["info", "notes"]
}
```

### Step 5 — Adjust Size Thresholds
```text
SIZE_THRESHOLD_MIN_MB = 5
SIZE_THRESHOLD_BOOST_MB = 500
SIZE_ANOMALY_MB = 4096
```

### Step 6 — Run
```text
python main.py
```

---

## 🧅 Tor Proxy Support

Enable Tor:
```text
USE_TOR_PROXY = True
TOR_PROXY = "socks5h://127.0.0.1:9050"
```

Disable:
```text
USE_TOR_PROXY = False
```

`socks5h://` ensures DNS resolution happens inside Tor (required for .onion domains).

---

## 🧪 Example Output (Colorized)

```text
[HIGH PRIORITY] Ubuntu 22.04 LTS ISO
    Score: 7 | Conf: 0.82 | Size: 4200 MB | Link: https://...
```

---

## 📜 License

MIT License — see LICENSE for details.  .gitignore
  LICENSE

---

## ⚙️ Configuration (Everything Lives in config.py)

### Target Settings
TARGET_URL — Base URL for the search endpoint  
TARGET_LINK_PREFIX — Only keep links starting with this prefix  

### Selector Configuration
item — CSS selector for each result item  
link_attr — Attribute containing the link  
title — Optional title selector  
context_parent — Optional parent selector for context extraction  

### Drift Detection
min_items_warning — Warn if fewer items than expected  
history_file — JSON file storing DOM snapshots  
max_history — How many snapshots to keep  

### Scoring & Filtering
PRIORITY_KEYWORDS — Tiered keyword scoring  
EXCLUSION_KEYWORDS — Keywords that disqualify a result  
EXCLUSION_LIST — Alias used by filters.py  
SIZE_THRESHOLD_MIN_MB — Exclude items smaller than this  
SIZE_THRESHOLD_BOOST_MB — Boost score if size ≥ this  
SIZE_ANOMALY_MB — Flag as anomaly if size ≥ this  

### Networking
USE_TOR_PROXY — Enable/disable Tor routing  
TOR_PROXY — SOCKS5 proxy address  
REQUEST_TIMEOUT — Request timeout  
MAX_RETRIES — Retry attempts  
BACKOFF_FACTOR — Exponential backoff multiplier  
HEADERS — Optional request headers  

### Export & Logging
EXPORT_JSON — Default JSON filename  
EXPORT_CSV — Default CSV filename  
TOP_N_SUMMARY — Items shown in summary blocks  
LOG_FILE — Log output file  

---

## 🧠 How Scoring Works

Keyword Score:
critical = +4  
strong = +2  
weak = +1  

Size Score:
If size_mb ≥ SIZE_THRESHOLD_BOOST_MB → +3  
Else → +0  

Anomaly Detection:
If size_mb ≥ SIZE_ANOMALY_MB → anomaly = True  

Confidence:
Heuristic combining keyword density, size presence, and title length.  
Clamped to [0, 1].

---

## 🧭 How to Adapt This to Any Site

Modify only config.py.

1. Set the target URL:
   TARGET_URL = "https://somesite.com/search"

2. Set the link prefix:
   TARGET_LINK_PREFIX = "https://somesite.com/"

3. Update selectors:
   item = ".result-item"
   link_attr = "href"
   title = ".title"
   context_parent = ".description"

4. Tune scoring:
   PRIORITY_KEYWORDS = { critical: [...], strong: [...], weak: [...] }

5. Adjust size thresholds:
   SIZE_THRESHOLD_MIN_MB = 5
   SIZE_THRESHOLD_BOOST_MB = 500
   SIZE_ANOMALY_MB = 4096

6. Run:
   python main.py

---

## 🧅 Tor Proxy Support

Enable Tor:
USE_TOR_PROXY = True
TOR_PROXY = "socks5h://127.0.0.1:9050"

Disable:
USE_TOR_PROXY = False

socks5h ensures DNS resolution happens inside Tor (required for .onion domains).

---

## 🧪 Example Output (Colorized)

[HIGH PRIORITY] Ubuntu 22.04 LTS ISO  
Score: 7 | Conf: 0.82 | Size: 4200 MB | Link: https://...

---

## 📜 License

MIT License — see LICENSE for details.
