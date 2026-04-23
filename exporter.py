# exporter.py
import csv
import json
from datetime import datetime
from typing import List, Dict


def export_json(results: List[Dict]) -> str:
    filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    return filename


def export_csv(results: List[Dict]) -> str:
    if not results:
        return ""

    filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    fieldnames = list(results[0].keys())

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    return filename
