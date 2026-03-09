"""Manually rebuild the backend RAG index from the exported knowledge JSON.

Usage:
  python scripts/rebuild_rag_index.py
  python scripts/rebuild_rag_index.py --data backend/data/fraud_knowledge.json --storage backend/storage
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def load_backend_env(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild the backend RAG index from fraud_knowledge.json")
    parser.add_argument("--env-file", type=Path, default=BACKEND_DIR / ".env", help="Path to backend environment file")
    parser.add_argument("--data", type=Path, default=BACKEND_DIR / "data" / "fraud_knowledge.json", help="Input knowledge JSON file")
    parser.add_argument("--storage", type=Path, default=BACKEND_DIR / "storage", help="Output storage directory for the persisted index")
    return parser.parse_args()


def print_progress(message: str) -> None:
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def main() -> None:
    args = parse_args()
    print_progress("Loading backend environment")
    load_backend_env(args.env_file)

    print_progress("Importing backend settings and RAG service")
    from app.core.config import get_settings
    from model.rag.service import get_rag_service

    settings = get_settings()
    data_path = args.data.resolve()
    storage_path = args.storage.resolve()

    if not data_path.exists():
        raise FileNotFoundError(f"Knowledge JSON not found: {data_path}")

    with data_path.open("r", encoding="utf-8") as file:
        item_count = len(json.load(file))

    print_progress(f"Knowledge file found: {data_path}")
    print_progress(f"Knowledge items: {item_count}")
    print_progress(f"Target storage: {storage_path}")
    print_progress("Starting RAG rebuild")

    service = get_rag_service()
    service.rebuild(
        data_path=data_path,
        storage_path=storage_path,
        api_key=settings.OPENAI_API_KEY,
        api_base=settings.OPENAI_BASE_URL,
        model=settings.OPENAI_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_device=settings.EMBEDDING_DEVICE,
        chunk_size=settings.CHUNK_SIZE,
    )

    print_progress("RAG index rebuild completed")
    print(f"data_path={data_path}")
    print(f"storage_path={storage_path}")
    print(f"embedding_model={settings.EMBEDDING_MODEL}")
    print(f"embedding_device={settings.EMBEDDING_DEVICE}")
    print(f"llm_model={settings.OPENAI_MODEL}")


if __name__ == "__main__":
    main()
