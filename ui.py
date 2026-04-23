# ui.py
from typing import List, Dict

from config import TOP_N_SUMMARY

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_AVAILABLE = True
except ImportError:
    COLOR_AVAILABLE = False


def _color(text: str, color) -> str:
    if not COLOR_AVAILABLE:
        return text
    return color + text + Style.RESET_ALL


def print_results(results: List[Dict], query: str) -> None:
    print(f"\n--- Found {len(results)} matches for '{query}' ---\n")

    for item in results:
        tag = "MATCH"
        if item["score"] >= 5:
            tag = "HIGH PRIORITY"
        if item["anomaly"]:
            tag = "ANOMALY"

        if tag == "HIGH PRIORITY":
            tag_str = _color(f"[{tag}]", Fore.GREEN)
        elif tag == "ANOMALY":
            tag_str = _color(f"[{tag}]", Fore.RED)
        else:
            tag_str = _color(f"[{tag}]", Fore.CYAN)

        print(
            f"{tag_str} {item['title']}\n"
            f"    Score: {item['score']} | "
            f"Conf: {item['confidence']:.2f} | "
            f"Size: {item['size_mb'] or 'N/A'} MB | "
            f"Link: {item['link']}\n"
        )


def print_summary(results: List[Dict]) -> None:
    if not results:
        print("[!] No results matched. Try adjusting your thresholds.")
        return

    print("\n--- Summary ---\n")

    top_by_score = sorted(results, key=lambda x: x["score"], reverse=True)[:TOP_N_SUMMARY]
    top_by_size = sorted(
        [r for r in results if r["size_mb"] is not None],
        key=lambda x: x["size_mb"],
        reverse=True
    )[:TOP_N_SUMMARY]
    top_by_conf = sorted(results, key=lambda x: x["confidence"], reverse=True)[:TOP_N_SUMMARY]

    def _print_block(title: str, items: List[Dict]):
        print(title)
        for item in items:
            print(
                f"  - {item['title']} "
                f"(Score={item['score']}, Conf={item['confidence']:.2f}, "
                f"Size={item['size_mb'] or 'N/A'} MB)"
            )
        print()

    _print_block("Top by score:", top_by_score)
    if top_by_size:
        _print_block("Top by size:", top_by_size)
    _print_block("Top by confidence:", top_by_conf)
