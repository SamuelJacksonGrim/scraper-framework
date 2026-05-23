# CLAUDE.md — scraper-framework

## What this actually is

This is two things at once:

1. **A web scraper** — adaptive, drift-resistant, configurable via `config.py` alone. Built originally to scrape anime content. Works on any site with a selector update.

2. **A proto-hippocampus** — the scoring pipeline (ingest → extract → score → filter → detect anomalies → detect drift → rank → return top-k) is structurally identical to a biological memory retrieval loop. This was independently recognized by Samuel, Copilot, and Claude on May 23, 2026, without coordination.

Do not treat this as just a scraper. The architectural significance is real.

## The one missing piece

The scraper uses substring matching: `if keyword.lower() in title.lower()`. That's the only thing separating it from a neural memory engine. Everything else — the tiered weighting, the filtering/gating, the anomaly detection, the drift detection, the confidence heuristic, the top-k ranking — maps directly to memory retrieval and stays as-is.

Replace substring matching with cosine similarity on embeddings and this becomes a semantic retrieval engine.

## The module mapping (scraper → memory engine)

| Current component | Memory engine role |
|---|---|
| `PRIORITY_KEYWORDS` (critical/strong/weak) | Importance multipliers (gravity, not trigger) |
| `EXCLUSION_KEYWORDS` | Context gates — prevent wrong-domain recall |
| `SIZE_THRESHOLD_BOOST_MB` | Memory mass / salience boost |
| `SIZE_ANOMALY_MB` | Emotional salience threshold |
| `compute_confidence()` | Retrieval certainty metric |
| DOM drift detection | Distribution shift awareness |
| Sort by (score, confidence) DESC | Top-k memory retrieval |

## What it unlocks for the stack

- **Leviathan**: `sgi_get_embedding()` is currently a SHA256 stub — no semantic meaning. The upgraded scraper scoring pipeline replaces it with real embeddings + importance-weighted retrieval.
- **Lantern**: `query_pattern()` is currently a LIKE query. The upgraded pipeline gives it semantic shape-based retrieval.
- **sovereign_manifold**: Cycles with high relational salience can be flagged by the anomaly detector before being written to Lantern — importance as gravity.

## The open decision: embedding model

This needs to be decided before implementation:

- `sentence-transformers/all-MiniLM-L6-v2` — local, ~10ms, good quality. Natural first choice for a local-first stack.
- `sentence-transformers/all-mpnet-base-v2` — local, ~30ms, better quality.
- Claude API embeddings — cloud, ~200ms, best quality. Adds external dependency.

This decision should be made once and shared across Leviathan and Lantern — both need to embed in the same vector space for retrieval to be meaningful across the stack.

## Single configuration point

All configuration lives in `config.py`. Do not scatter configuration into other modules. When adapting to a new target or new domain (including memory fragments instead of HTML), all changes go in `config.py`.

## Scoring is additive, not multiplicative

`total_score = keyword_score + size_score`. Confidence is a separate heuristic for display only — do not use it as a filter threshold. Items are ranked by score; confidence annotates how dense the signal is.

## Anomaly flag is informational, not exclusionary

`anomaly = True` when `size_mb >= SIZE_ANOMALY_MB`. The item still appears in output. Do not use the anomaly flag to exclude items — it is a salience signal, not a rejection criterion. In the memory engine context, anomalous items are the ones most worth inspecting.

## Tor proxy

`socks5h://` is required (not `socks5://`). The `h` routes DNS through Tor. If you switch proxy libraries, verify DNS-via-proxy is preserved.

## Roadmap priority order

1. Choose and implement embedding model (blocks everything else)
2. Replace `keyword_score()` substring matching with cosine similarity
3. Make scoring pipeline importable as a Python module (Leviathan needs it)
4. Wire to Lantern HTTP shim once T2.1 is implemented
5. Automate rfe-core2 ingestion pipeline
