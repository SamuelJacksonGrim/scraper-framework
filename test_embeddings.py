# test_embeddings.py
"""
Verification for the embedding + semantic_score work.

Two layers:
  1. Deterministic stub embedder - proves the semantic_score math,
     the Protocol wiring, the config plumbing, and no-regression
     of the existing keyword pipeline. Runs anywhere with numpy.
  2. Real LocalSTEmbedder - loads all-MiniLM-L6-v2 from Hugging Face,
     runs real cosine similarity. Requires network access to huggingface.co
     (or the model already cached locally). Auto-skips if the download
     fails so the stub layer still gates the merge.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from scoring import (
    semantic_score,
    keyword_score,
    compute_total_score,
    parse_numeric_metric,
)
import embeddings
from embeddings import Embedder

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
SKIP = "\033[33mSKIP\033[0m"

results = []


def check(name, condition, detail=""):
    tag = PASS if condition else FAIL
    print(f"  [{tag}] {name}" + (f" - {detail}" if detail else ""))
    results.append(condition)


# -----------------------------------------------------------------------------
# Layer 1 - Stub embedder
# -----------------------------------------------------------------------------
class StubEmbedder:
    """Bag-of-words projection onto a fixed vocab. Real cosine, no network."""

    _VOCAB = [
        "iso", "release", "final", "update", "patch", "installer",
        "software", "application", "download", "version", "file", "image",
        "chocolate", "cake", "baking", "recipe", "flour", "sugar",
        "random", "unrelated", "text", "about", "cooking", "kitchen",
        "semantic", "retrieval", "memory", "neural", "embedding", "vector",
    ]

    @property
    def dim(self) -> int:
        return len(self._VOCAB)

    def embed(self, text: str) -> np.ndarray:
        words = text.lower().split()
        vec = np.zeros(self.dim, dtype=np.float32)
        for w in words:
            if w in self._VOCAB:
                vec[self._VOCAB.index(w)] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        else:
            # No known words: seed a deterministic-per-text random signature
            # so unrelated OOV strings cosine-differ instead of 0/0-ing.
            rng = np.random.default_rng(abs(hash(text)) % (2**31))
            vec = rng.random(self.dim).astype(np.float32)
            vec /= np.linalg.norm(vec)
        return vec


stub = StubEmbedder()


print("\n=== StubEmbedder ===")
v = stub.embed("iso release final")
check("embed returns ndarray", isinstance(v, np.ndarray))
check("embed shape matches dim", v.shape == (stub.dim,), f"shape={v.shape}")
check("embed is unit-normalised", abs(float(np.linalg.norm(v)) - 1.0) < 1e-5)


print("\n=== Embedder Protocol ===")
check("StubEmbedder satisfies Embedder Protocol", isinstance(stub, Embedder))


print("\n=== semantic_score math ===")
s_identical = semantic_score("iso release final", "iso release final", stub)
check("identical text -> score ~= 1.0", abs(s_identical - 1.0) < 1e-5, f"{s_identical:.6f}")

s_high = semantic_score("iso release final", "iso release final version 2", stub)
check("high vocab overlap -> score > 0.8", s_high > 0.8, f"{s_high:.4f}")

s_low = semantic_score("iso release final", "chocolate cake baking recipe", stub)
check("no vocab overlap -> score ~ 0", s_low < 0.01, f"{s_low:.4f}")

s_mid = semantic_score("iso release final", "software release update", stub)
check("partial overlap -> 0 < score < 1", 0.0 < s_mid < 1.0, f"{s_mid:.4f}")


print("\n=== get_embedder factory ===")
# Test the factory selects the right class without actually downloading a model.
class _FakeLocalST:
    def __init__(self, model_name):
        self._name = model_name
    def embed(self, text):
        return stub.embed(text)
    @property
    def dim(self):
        return stub.dim


import config as _cfg
_orig = _cfg.EMBEDDING_BACKEND
_orig_LocalST = embeddings.LocalSTEmbedder
embeddings.LocalSTEmbedder = _FakeLocalST
embeddings._reset_cache()
_cfg.EMBEDDING_BACKEND = "local"

emb = embeddings.get_embedder()
check("get_embedder returns LocalSTEmbedder for 'local'", isinstance(emb, _FakeLocalST))

emb2 = embeddings.get_embedder()
check("get_embedder caches the instance", emb is emb2)

embeddings.LocalSTEmbedder = _orig_LocalST
_cfg.EMBEDDING_BACKEND = _orig
embeddings._reset_cache()


print("\n=== keyword_score (no regression) ===")
check("'iso release final' > 0", keyword_score("iso release final v2.0") > 0)
check("'random text' == 0", keyword_score("random unrelated text") == 0)
check("'iso' scores 4 (critical)", keyword_score("iso") == 4)
check("'update' scores 2 (strong)", keyword_score("update") == 2)
check("'misc' scores 1 (weak)", keyword_score("misc") == 1)


print("\n=== parse_numeric_metric (no regression) ===")
check("2.5GB parses to 2560 MB", parse_numeric_metric("Ubuntu 2.5GB") == 2560.0)
check("500MB parses to 500", parse_numeric_metric("size 500MB") == 500.0)
check("1TB parses to 1048576", parse_numeric_metric("archive 1TB") == 1024.0 * 1024.0)
check("loose '3.7G' -> 3788.8 MB",
      abs(parse_numeric_metric("3.7G", loose=True) - 3.7 * 1024) < 0.1)
check("free text '4K' NOT parsed strictly (safety)",
      parse_numeric_metric("Movie 4K") is None)


print("\n=== compute_total_score (no regression) ===")
s = compute_total_score("Ubuntu ISO release final 2.5GB")
check("total_score > 0", s["total_score"] > 0, f"score={s['total_score']}")
check("size_mb == 2560.0", s["size_mb"] == 2560.0, f"size_mb={s['size_mb']}")
check("size_score kicks in (>= 500MB boost)", s["size_score"] == 3)
check("anomaly False (2560 < 4096)", not s["anomaly"])
check("keyword_score == 12 (3 critical keywords)", s["keyword_score"] == 12)

s2 = compute_total_score("release-notes.txt", context="release-notes.txt  3.7G  2026-01-01")
check("context fallback parses size", s2["size_mb"] is not None and s2["size_mb"] > 3700)


print("\n=== config sanity ===")
import importlib
importlib.reload(_cfg)
check("EXCLUSION_LIST alias works", _cfg.EXCLUSION_LIST == _cfg.EXCLUSION_KEYWORDS)
check("EMBEDDING_BACKEND is str", isinstance(_cfg.EMBEDDING_BACKEND, str))
check("EMBEDDING_MODEL is str", isinstance(_cfg.EMBEDDING_MODEL, str))
check("default backend is 'local'", _cfg.EMBEDDING_BACKEND == "local")


# -----------------------------------------------------------------------------
# Layer 2 - Real LocalSTEmbedder
# -----------------------------------------------------------------------------
print("\n=== Real LocalSTEmbedder (network-gated) ===")
real_ok = True
try:
    from embeddings import LocalSTEmbedder
    real_emb = LocalSTEmbedder("all-MiniLM-L6-v2")
except Exception as e:
    print(f"  [{SKIP}] LocalSTEmbedder construction - {type(e).__name__}")
    print(f"          (requires huggingface.co network access or a cached model)")
    real_ok = False

if real_ok:
    check("real embedder dim == 384", real_emb.dim == 384, f"dim={real_emb.dim}")

    s_similar = semantic_score("iso release final", "iso release final v2", real_emb)
    check("real: similar pair > 0.85", s_similar > 0.85, f"{s_similar:.4f}")

    s_diff = semantic_score("iso release final", "chocolate cake baking recipe", real_emb)
    check("real: dissimilar pair < 0.5", s_diff < 0.5, f"{s_diff:.4f}")

    # This is the whole point - semantic synonyms with NO substring overlap
    # get high scores. Substring matching would score these zero.
    s_synonym = semantic_score("software update installer", "application patch download", real_emb)
    check("real: cross-word synonyms > 0.5", s_synonym > 0.5, f"{s_synonym:.4f}")


print("\n=== Results ===")
passed = sum(results)
total = len(results)
print(f"  {passed}/{total} checks passed")
sys.exit(0 if passed == total else 1)
