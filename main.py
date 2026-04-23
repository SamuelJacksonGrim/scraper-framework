# main.py
import logging

from config import BASE_URL, SEARCH_QUERY, LOG_FILE
from fetch import fetch_page
from parse import parse_results
from exporter import export_json, export_csv
from ui import print_results, print_summary


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def run():
    setup_logging()
    logging.info("Starting scraper for query: %s", SEARCH_QUERY)

    html = fetch_page(BASE_URL, params={"q": SEARCH_QUERY})
    results = parse_results(html)

    print_results(results, SEARCH_QUERY)
    print_summary(results)

    if results:
        json_file = export_json(results)
        csv_file = export_csv(results)
        print(f"[*] Results exported to {json_file} and {csv_file}")
    else:
        print("[!] No results matched. Try adjusting your thresholds.")


if __name__ == "__main__":
    run()
