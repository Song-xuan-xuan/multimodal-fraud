"""Convert curated case_data JSON files into the backend RAG import format.

Usage:
  python scripts/convert_case_data_to_rag.py
  python scripts/convert_case_data_to_rag.py --input-dir backend/app/static/case_data --output backend/data/fraud_knowledge.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / "backend" / "app" / "static" / "case_data"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "backend" / "data" / "fraud_knowledge.json"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert case_data JSON files into RAG import JSON")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR, help="Directory containing the source case_data JSON files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Output path for the flattened RAG JSON file")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def build_record(prefix: str, index: int, website_name: str, source_url: str, item: dict) -> dict:
    title = normalize_text(item.get("title"))
    content = normalize_text(item.get("content"))

    return {
        "id": f"{prefix}_{index}",
        "type": "case",
        "title": title,
        "content": content,
        "conclusion": "",
        "fraud_type": "",
        "risk_level": "",
        "source": source_url,
        "tags": [website_name] if website_name else [],
        "target_groups": [],
        "signals": [],
        "advice": [],
    }


def convert_file(path: Path, prefix: str) -> tuple[list[dict], dict]:
    payload = load_json(path)
    website_name = normalize_text(payload.get("website_name"))
    source_url = normalize_text(payload.get("source_url"))
    source_data = payload.get("source_data") or []

    if not isinstance(source_data, list):
        raise ValueError(f"source_data must be a list in {path}")

    records: list[dict] = []
    skipped = 0
    for item in source_data:
        if not isinstance(item, dict):
            skipped += 1
            continue

        title = normalize_text(item.get("title"))
        content = normalize_text(item.get("content"))
        if not title or not content:
            skipped += 1
            continue

        records.append(build_record(prefix, len(records), website_name, source_url, item))

    stats = {
        "file": path.name,
        "prefix": prefix,
        "source_total": len(source_data),
        "converted": len(records),
        "skipped": skipped,
    }
    return records, stats


def resolve_prefix(payload: dict) -> str:
    website_name = normalize_text(payload.get("website_name"))
    source_url = normalize_text(payload.get("source_url"))

    if "baidu.com" in source_url:
        return "baidu"
    if "套路" in website_name:
        return "sogou_taolu"
    if "预警" in website_name:
        return "sogou_warning"
    if "反诈" in website_name:
        return "sogou"
    if "%E5%A5%97%E8%B7%AF" in source_url:
        return "sogou_taolu"
    if "%E9%A2%84%E8%AD%A6" in source_url:
        return "sogou_warning"
    if "sogou.com" in source_url:
        return "sogou"

    raise ValueError(f"Unable to determine prefix from payload metadata: {source_url}")


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_path = args.output.resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    all_records: list[dict] = []
    all_stats: list[dict] = []

    json_files = sorted(input_dir.glob("*.json"))
    if len(json_files) != 4:
        raise ValueError(f"Expected 4 source files in {input_dir}, found {len(json_files)}")

    seen_prefixes: set[str] = set()
    for file_path in json_files:
        payload = load_json(file_path)
        prefix = resolve_prefix(payload)
        if prefix in seen_prefixes:
            raise ValueError(f"Duplicate prefix resolved for {file_path}: {prefix}")

        records, stats = convert_file(file_path, prefix)
        seen_prefixes.add(prefix)
        all_records.extend(records)
        all_stats.append(stats)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(all_records, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(all_records)} records to {output_path}")
    for stats in all_stats:
        print(
            f"- {stats['file']}: converted={stats['converted']} skipped={stats['skipped']} "
            f"source_total={stats['source_total']} prefix={stats['prefix']}"
        )


if __name__ == "__main__":
    main()
