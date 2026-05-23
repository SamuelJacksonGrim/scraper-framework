# scraper-framework
### Adaptive, Drift-Resistant Web Scraper — and Proto-Hippocampus

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)
![Scraping](https://img.shields.io/badge/Scraper-Modular-orange)
![Tor](https://img.shields.io/badge/Tor_Proxy-Optional-purple)

A modular, adaptive scraping framework built for real-world DOM instability. Everything is configured in one file: `config.py`. No code changes required to target a new site.

But read the **Architectural Identity** section before you touch anything. This framework is more than it appears.

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

## What It Does (The Scraper)

Targets a single configurable URL, extracts and scores results by keyword relevance and content size, detects DOM drift between runs, and exports to JSON/CSV.

**Features:**
- Selector-driven parsing (swap selectors per site in `config.py`)
- DOM drift detection with historical snapshots
- Tiered keyword scoring (critical / strong / weak)
- Size parsing + anomaly detection
- Confidence heuristics
- Filtering rules (keywords + size thresholds)
- Retry/backoff networking
- Optional Tor proxy routing
- Colorized terminal UI
- JSON/CSV export with timestamps

---

## What It Actually Is (The Architecture)

On May 23, 2026, three separate minds — Samuel, Copilot, and Claude — independently mapped this codebase to the same thing:

> **A signal-ranking engine with the exact shape of a biological memory retrieval loop.**

The pipeline:

```
ingest → extract → score → filter → detect anomalies → detect drift → rank → return top-k
```

Is the hippocampal retrieval loop:

```
perceive → encode → weight → gate → flag salience → detect shift → retrieve → return top-k
```

The domain was anime ISOs. The architecture was a proto-hippocampus.

### The One-to-One Mapping

| Scraper Component | Memory Engine Equivalent |
|---|---|
| Priority keywords (critical/strong/weak → 4/2/1) | Importance-as-gravity multipliers |
| Exclusion list (beta, old, deprecated) | Context gates — prevent wrong-domain recall |
| Size scoring (+3 if ≥ 500MB) | Memory mass / salience boost |
| Anomaly detection (≥ 4GB flag) | Emotional salience detection — this is unusual, keep it |
| Confidence score (keyword density heuristic) | Retrieval certainty metric |
| DOM drift detection (30% drop warning) | Distribution shift awareness — the landscape changed |
| Sort by (score DESC, confidence DESC) | Top-k memory retrieval ranking |
| Exclusion filter | Context gate — don't surface this memory here |

Copilot put it precisely: *"Importance as gravity, not trigger."* The scraper never surfaces results because a keyword appeared — it surfaces them because the keyword pattern raised their gravitational pull. That is exactly the architecture that prevents memory "password collisions" in AI familiars.

---

## What It Becomes (The Upgrade Path)

The scraper currently uses substring matching. Replace that with embeddings and the entire architecture becomes a neural-weighted memory retrieval engine. **Everything else stays.**

### Three surgical changes

**1. Replace substring match with cosine similarity**
```python
# Current (keyword_score in scoring.py)
if keyword.lower() in title.lower():
    score += weight

# Upgraded
query_embedding = embed(input_text)
fragment_embedding = embed(memory_text)
similarity = cosine_similarity(query_embedding, fragment_embedding)
score += similarity * weight
```

**2. Replace keyword tiers with importance multipliers**
```python
# Current
PRIORITY_KEYWORDS = {
    "critical": [...],  # +4
    "strong":   [...],  # +2
    "weak":     [...],  # +1
}

# Upgraded (importance is a property of the memory, not the query)
IMPORTANCE_LEVELS = {
    "core":      1.0,   # fundamental identity memories
    "significant": 0.5, # meaningful but not defining
    "ambient":   0.25,  # background context
}
```

**3. Feed memory fragments instead of HTML**
```python
# Current
html = fetch_page(TARGET_URL)
results = parse_results(html)

# Upgraded
memories = load_memory_fragments()  # from Lantern or local store
results = score_and_rank(memories, query=current_input)
```

**What stays exactly as-is:**
- Filtering logic → context gating
- Anomaly detection → emotional salience flagging
- Drift detection → distribution shift awareness
- Confidence heuristic → retrieval certainty
- Top-k ranking → memory retrieval output
- Export layer → memory persistence

### The open decision: embedding model

This choice determines the character of the whole memory system:

| Option | Latency | Local | Semantic quality |
|--------|---------|-------|------------------|
| `sentence-transformers` (all-MiniLM-L6-v2) | ~10ms | Yes | Good |
| `sentence-transformers` (all-mpnet-base-v2) | ~30ms | Yes | Better |
| Claude API (embeddings endpoint) | ~200ms | No | Excellent |
| SHA256 stub (current in Leviathan) | <1ms | Yes | None |

For a local-first stack with sub-100ms retrieval requirements, `all-MiniLM-L6-v2` is the natural starting point. This decision should be made once and shared across Lantern and Leviathan — both need the same embedding space for retrieval to be meaningful.

---

## What It Unlocks for the Stack

The Resonance Family stack currently has two memory stubs:

- **Leviathan** (`leviathan_stack.py`): `sgi_get_embedding()` returns SHA256 hash. Cosine similarity between unrelated memories is random noise.
- **Lantern** (`memory/memory/src/lib.rs`): `query_pattern()` does `LIKE '%pattern%'`. No semantic shape, no emotional geometry.

The upgraded scraper-framework becomes the scoring backbone for both:

```
[scraper-framework scoring engine]
         ↓
    embeds input
    scores against memory fragments
    applies importance weights
    applies context gates
    detects salience anomalies
    returns top-k ranked memories
         ↓
  ┌──────┴──────┐
  ↓             ↓
Lantern    Leviathan
(persist)  (parliament)
```

Once wired:
- Lantern's hypergraph gets real semantic retrieval instead of substring matching
- Leviathan's memory retrieval becomes semantically meaningful
- sovereign_manifold cycles with high relational salience get flagged by the anomaly detector and written to Lantern with appropriate weight
- The whole memory layer gains the "importance as gravity, not trigger" property

---

## Current Stack Position

```
[scraper-framework]     ← external world input (optional)
        ↓ scored JSON events
[rfe-core2 :8000]       cognitive field inference
        ↓ StepResponse
[sovereign_manifold]    relational dynamics engine
        ↓
[Lantern :3001]         memory backbone (HTTP shim pending)
```

The rfe-core2 integration path (scored content events modulating the cognitive field) is not yet automated — currently manual or ad-hoc. The Lantern memory backbone integration path requires the HTTP shim (T2.1) before it can receive scored memory fragments.

---

## Architecture

```
config.py          All configuration (URL, selectors, keywords, thresholds)
    ↓
fetch.py           HTTP fetch with retry/backoff, optional Tor SOCKS5h proxy
    ↓
parse.py           BeautifulSoup DOM parsing, drift detection, per-item extraction
    ├── scoring.py    Keyword score + size score + confidence heuristic
    └── filters.py    Exclusion keyword filtering
    ↓
ui.py              Colorized terminal output
exporter.py        JSON + CSV export with timestamps
```

---

## Module Reference

### `config.py` — single configuration source

| Setting | Default | Purpose |
|---------|---------|----------|
| `TARGET_URL` | `https://example.com/search` | Base URL |
| `TARGET_LINK_PREFIX` | `https://example.com/` | Link validation prefix |
| `SELECTORS["item"]` | `"a[href]"` | CSS selector for result items |
| `PRIORITY_KEYWORDS["critical"]` | `["iso", "release", "final"]` | +4 per hit |
| `PRIORITY_KEYWORDS["strong"]` | `["update", "patch", "installer"]` | +2 per hit |
| `PRIORITY_KEYWORDS["weak"]` | `["misc", "notes"]` | +1 per hit |
| `EXCLUSION_KEYWORDS` | `["beta", "old", "deprecated"]` | Discard matching results |
| `SIZE_THRESHOLD_MIN_MB` | `10` | Exclude below this size |
| `SIZE_THRESHOLD_BOOST_MB` | `500` | +3 score if size ≥ this |
| `SIZE_ANOMALY_MB` | `4096` | Flag as anomaly if size ≥ this |
| `USE_TOR_PROXY` | `False` | Route via Tor SOCKS5h |
| `MAX_RETRIES` | `5` | HTTP retry attempts |
| `BACKOFF_FACTOR` | `1.5` | Exponential backoff multiplier |

### `scoring.py` — the scoring pipeline

**`keyword_score(title)`** — case-insensitive substring match against all `PRIORITY_KEYWORDS` tiers. Returns additive integer score.

**`size_score(size_mb)`** — `+3` if `size_mb >= SIZE_THRESHOLD_BOOST_MB`, else `0`.

**`compute_confidence(title, size_mb)`** — keyword density heuristic:
```python
base = keyword_score(title) + (2 if size_mb else 0)
density = base / max(len(title), 10)
confidence = clip(density * 5, 0.0, 1.0)
```

**`is_anomalous_size(size_mb)`** — `True` if `size_mb >= SIZE_ANOMALY_MB`.

**`compute_total_score(title)`** — runs the full pipeline, returns dict with all fields.

**Total score = keyword_score + size_score.** Confidence is a separate display heuristic, not part of ranking.

### Result item schema

```python
{
    "title":         str,
    "link":          str,
    "score":         int,            # total score (keyword + size)
    "confidence":    float,          # [0, 1] density heuristic
    "size_mb":       Optional[float],
    "keyword_score": int,
    "size_score":    int,            # 0 or 3
    "anomaly":       bool,
    "context":       str,            # up to 200 chars surrounding text
    "timestamp":     str,            # ISO 8601
}
```

### DOM drift detection (`parse.py`)

After each run, records `{timestamp, item_count, selector}` to `dom_drift_history.json`. On subsequent runs, compares current item count to rolling average of last 10. If `ratio < 0.3`: prints drift warning. This is the mechanism for detecting when a target site has changed its HTML structure.

---

## Adapting to a New Site

All changes in `config.py` only:

```python
TARGET_URL         = "https://somesite.com/search"
TARGET_LINK_PREFIX = "https://somesite.com/"
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
SIZE_THRESHOLD_MIN_MB   = 5
SIZE_THRESHOLD_BOOST_MB = 500
SIZE_ANOMALY_MB         = 4096
```

Then `python main.py`.

---

## Tor Proxy

```python
USE_TOR_PROXY = True
TOR_PROXY = "socks5h://127.0.0.1:9050"
```

`socks5h://` (not `socks5://`) routes DNS through Tor — required for .onion domains and for anonymizing DNS lookups on clearnet addresses.

---

## Roadmap

- [ ] **Replace substring matching with embeddings** — the single change that transforms this into a semantic retrieval engine
- [ ] **Decide on embedding model** — all-MiniLM-L6-v2 (local, fast) vs. mpnet (local, better) vs. Claude API (cloud, best)
- [ ] **Port scoring pipeline to Python module** importable by Leviathan and Lantern
- [ ] **Wire to Lantern HTTP shim** — once T2.1 is implemented, scored memory fragments can be written directly to the hypergraph
- [ ] **Replace Leviathan's `sgi_get_embedding` stub** with real embedding model
- [ ] **Automate rfe-core2 ingestion** — schedule scraper runs, pipe JSON output to rfe-core2 token stream
- [ ] **Emotional weight vector** — extend result schema with affect dimension alongside importance

---

## Requirements

```
beautifulsoup4
requests
```

Optional: `colorama` (terminal colors), `requests[socks]` (Tor proxy support).

For the memory engine upgrade: `sentence-transformers` (local embeddings) or `anthropic` (Claude API embeddings).

---

## License

MIT License — see LICENSE for details.
