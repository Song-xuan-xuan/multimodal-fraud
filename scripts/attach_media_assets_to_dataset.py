"""把 test-dataset/images 与 test-dataset/audio 的媒体资源挂到数据集 JSON 上。

设计目标：尽量简单、可手工维护。

约定：
- 图片放到 test-dataset/images/，音频放到 test-dataset/audio/
- 文件名使用“样本 case_id”作为 stem，例如：
  - TXT_WHITE_006.jpg
  - TXT_BLACK_019.png
  - TXT_WHITE_012.wav
- 一个 case_id 只取“一个”图片/音频（优先级按扩展名排序）。

输出：
- 在原有 text 条目基础上，额外追加 media 条目，case_id 会加后缀避免重复：
  - TXT_WHITE_006_IMAGE
  - TXT_WHITE_012_AUDIO
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = PROJECT_ROOT / "test-dataset" / "evaluation_text_dataset.json"
DEFAULT_OUT = PROJECT_ROOT / "test-dataset" / "evaluation_dataset_with_media.json"
DEFAULT_IMAGES_DIR = PROJECT_ROOT / "test-dataset" / "images"
DEFAULT_AUDIO_DIR = PROJECT_ROOT / "test-dataset" / "audio"

IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp"]
AUDIO_EXTS = [".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"]


def _load_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("dataset json must be a list")
    out: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict):
            out.append(item)
    return out


def _relpath(p: Path) -> str:
    try:
        return p.relative_to(PROJECT_ROOT).as_posix()
    except Exception:
        return p.as_posix()


def _index_assets(dir_path: Path, exts: list[str]) -> dict[str, dict[str, Path]]:
    """Return: stem_lower -> {ext_lower -> path}."""
    index: dict[str, dict[str, Path]] = {}
    if not dir_path.exists():
        return index
    for p in dir_path.iterdir():
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext not in exts:
            continue
        stem = p.stem.lower()
        index.setdefault(stem, {})[ext] = p
    return index


def _pick_asset(stem: str, asset_index: dict[str, dict[str, Path]], exts_priority: list[str]) -> Path | None:
    bucket = asset_index.get((stem or "").lower())
    if not bucket:
        return None
    for ext in exts_priority:
        p = bucket.get(ext)
        if p:
            return p
    # 兜底：随便取一个
    return next(iter(bucket.values()), None)


def _build_media_item(base: dict[str, Any], *, modality: str, file_path: Path) -> dict[str, Any]:
    case_id = str(base.get("case_id") or "")
    label = int(base.get("label") or 0)

    suffix = "_IMAGE" if modality == "image" else "_AUDIO"
    new_case_id = case_id + suffix if case_id else modality.upper()

    # 复制大多数字段，覆盖几个关键字段
    item = dict(base)
    item["case_id"] = new_case_id
    item["modality"] = modality
    item["file_path"] = _relpath(file_path)

    # 非文本样本，content 置空更直观（必要时你也可以手工填“说明/转写”）
    item["content"] = ""

    # 难度/期望风险可以沿用原条目；如果原条目是 text 白样本，则 label=0 也没问题。
    item["label"] = label
    return item


def attach_media(
    dataset: list[dict[str, Any]],
    images_dir: Path,
    audio_dir: Path,
) -> list[dict[str, Any]]:
    images_index = _index_assets(images_dir, IMAGE_EXTS)
    audio_index = _index_assets(audio_dir, AUDIO_EXTS)

    out: list[dict[str, Any]] = list(dataset)
    for base in dataset:
        case_id = str(base.get("case_id") or "")
        if not case_id:
            continue

        # 只基于“原始 case_id”去找资源，避免重复挂载
        stem = case_id

        image_path = _pick_asset(stem, images_index, IMAGE_EXTS)
        if image_path:
            out.append(_build_media_item(base, modality="image", file_path=image_path))

        audio_path = _pick_asset(stem, audio_index, AUDIO_EXTS)
        if audio_path:
            out.append(_build_media_item(base, modality="audio", file_path=audio_path))

    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="为测评数据集附加图片/音频条目")
    parser.add_argument("--input", default=str(DEFAULT_IN), help="输入 JSON（通常是 evaluation_text_dataset.json）")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="输出 JSON（附加 media 条目）")
    parser.add_argument("--images-dir", default=str(DEFAULT_IMAGES_DIR), help="图片目录")
    parser.add_argument("--audio-dir", default=str(DEFAULT_AUDIO_DIR), help="音频目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)
    images_dir = Path(args.images_dir)
    audio_dir = Path(args.audio_dir)

    dataset = _load_json(in_path)
    merged = attach_media(dataset, images_dir=images_dir, audio_dir=audio_dir)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[attach-media] in={in_path} out={out_path} items={len(dataset)} -> {len(merged)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

