# CLAUDE.md — scraper-framework

## What this is (and what it isn't)

A standalone, self-contained web scraping framework. No integration with the Resonance Family stack (sovereign_manifold, rfe-core2, unified-observer, etc.). It does not connect to any ports, import any stack libraries, or share state with other repos. It is an independent utility.

## Single configuration point

All configuration lives in `config.py`. Every tunable — target URL, CSS selectors, keyword weights, size thresholds, Tor proxy settings, export filenames — is in that one file. Do not scatter configuration into other modules.

## The pipeline is stateless by design

```
fetch.py → parse.py → scoring.py → filters.py → exporter.py
```

Each stage is a pure function of its inputs. There is no session object, no global state, no database. Results are exported to JSON/CSV on each run. DOM drift snapshots are stored in a JSON file (`history_file` in config) for cross-run comparison only.

## Tor proxy

`socks5h://` is required (not `socks5://`). The `h` ensures DNS resolution happens inside Tor, which is mandatory for .onion domains. If you switch proxy libraries, verify that DNS-via-proxy behavior is preserved.

## Scoring is additive, not multiplicative

Keyword score + size score = total score. Confidence is a separate heuristic (keyword density × size presence × title normalization), not part of the score. Items are ranked by score; confidence is a display annotation. Do not use confidence as a filter threshold — it was designed for display only.

## DOM drift detection

`parse.py` stores a snapshot of the selector output in `history_file` after each run. On subsequent runs, it compares the current snapshot to the last N stored. A large delta flags as drift. `max_history` in config limits file growth. This is the main mechanism for detecting when a target site has changed its structure — not an error, just a signal to update selectors.

## Extending to a new target site

Change only `config.py`:
1. Set `TARGET_URL` and `TARGET_LINK_PREFIX`
2. Update `SELECTORS` dict to match the new site's CSS structure
3. Tune `PRIORITY_KEYWORDS` for the new domain's vocabulary
4. Adjust `SIZE_THRESHOLD_MIN_MB` / `SIZE_THRESHOLD_BOOST_MB` if size scoring applies

Do not modify the pipeline modules for site-specific logic — that belongs in `config.py`.

## Keyword weight semantics

`critical = +4`, `strong = +2`, `weak = +1`. These are relative weights, not absolute. Only the ordering matters — an item with two `strong` matches (+4) outranks an item with one `critical` match (+4) only if you add another `weak` (+5 total). Keep `critical` reserved for terms that definitively identify the target item.

## Anomaly flag is informational

`anomaly = True` when `size_mb >= SIZE_ANOMALY_MB`. This does not filter the item out — it is a flag for the operator to inspect. The item still appears in output and results files. Do not use the anomaly flag as an exclusion criterion.
