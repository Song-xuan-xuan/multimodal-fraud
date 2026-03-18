"""构建比赛提交用数据集（保持黑白 1:1，包含多模态案例）。

你当前已经有：
- 40 条文本样本（20 黑 + 20 白）：test-dataset/evaluation_text_dataset.json
- 若干图片：test-dataset/images/TXT_*.{jpg,png,...}
- 若干音频：test-dataset/audio/TXT_*.{wav,mp3,...}

比赛要求常见理解是“案例总数”需要黑白 1:1，且数据集中要包含文本/图片/音频(或视频)。

为了避免“追加媒体条目”导致总体黑白比例偏斜，本脚本会：
- 从 40 条文本样本出发
- 选出 1 条黑样本 + 1 条白样本改成 audio 案例（modality=audio, file_path 指向音频）
- 选出 1 条黑样本 + 1 条白样本改成 image 案例（modality=image, file_path 指向图片）
- 其余保持 text

输出：test-dataset/evaluation_submission_dataset.json（仍然 40 条，黑白 1:1）
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEXT_DATASET = PROJECT_ROOT / "test-dataset" / "evaluation_text_dataset.json"
DEFAULT_OUT = PROJECT_ROOT / "test-dataset" / "evaluation_submission_dataset.json"
DEFAULT_IMAGES_DIR = PROJECT_ROOT / "test-dataset" / "images"
DEFAULT_AUDIO_DIR = PROJECT_ROOT / "test-dataset" / "audio"

IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp"]
AUDIO_EXTS = [".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"]


def _load_list(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("dataset json must be a list")
    return [x for x in payload if isinstance(x, dict)]


def _relpath(p: Path) -> str:
    try:
        return p.relative_to(PROJECT_ROOT).as_posix()
    except Exception:
        return p.as_posix()


def _index_assets(dir_path: Path, exts: list[str]) -> dict[str, Path]:
    """stem_lower -> chosen_path (prefer stable ext order)."""
    index: dict[str, dict[str, Path]] = {}
    if not dir_path.exists():
        return {}
    for p in dir_path.iterdir():
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext not in exts:
            continue
        index.setdefault(p.stem.lower(), {})[ext] = p

    chosen: dict[str, Path] = {}
    for stem, bucket in index.items():
        for ext in exts:
            if ext in bucket:
                chosen[stem] = bucket[ext]
                break
        if stem not in chosen:
            chosen[stem] = next(iter(bucket.values()))
    return chosen


def _pick_case_id(
    items: list[dict[str, Any]],
    *,
    label: int,
    available: dict[str, Path],
    prefer_case_id: str = "",
) -> str:
    prefer_case_id = (prefer_case_id or "").strip()
    if prefer_case_id:
        for it in items:
            if str(it.get("case_id") or "") == prefer_case_id and int(it.get("label") or 0) == label:
                if prefer_case_id.lower() in available:
                    return prefer_case_id
        raise ValueError(f"指定 case_id 不可用或缺少资源: {prefer_case_id}")

    for it in items:
        if int(it.get("label") or 0) != label:
            continue
        cid = str(it.get("case_id") or "")
        if cid and cid.lower() in available:
            return cid
    return ""


def _apply_media(items_by_id: dict[str, dict[str, Any]], case_id: str, modality: str, file_path: Path) -> None:
    if not case_id:
        return
    item = items_by_id.get(case_id)
    if not item:
        return
    item["modality"] = modality
    item["file_path"] = _relpath(file_path)
    item["content"] = ""


def build_submission_dataset(
    text_items: list[dict[str, Any]],
    images_dir: Path,
    audio_dir: Path,
    *,
    audio_black: str = "",
    audio_white: str = "",
    image_black: str = "",
    image_white: str = "",
) -> list[dict[str, Any]]:
    items = [dict(x) for x in text_items]
    items_by_id = {str(x.get("case_id") or ""): x for x in items}

    image_index = _index_assets(images_dir, IMAGE_EXTS)
    audio_index = _index_assets(audio_dir, AUDIO_EXTS)

    # Pick 1 black + 1 white for audio, 1 black + 1 white for image.
    cid_audio_black = _pick_case_id(items, label=1, available=audio_index, prefer_case_id=audio_black)
    cid_audio_white = _pick_case_id(items, label=0, available=audio_index, prefer_case_id=audio_white)
    cid_image_black = _pick_case_id(items, label=1, available=image_index, prefer_case_id=image_black)
    cid_image_white = _pick_case_id(items, label=0, available=image_index, prefer_case_id=image_white)

    # Apply changes
    if cid_audio_black:
        _apply_media(items_by_id, cid_audio_black, "audio", audio_index[cid_audio_black.lower()])
    if cid_audio_white:
        _apply_media(items_by_id, cid_audio_white, "audio", audio_index[cid_audio_white.lower()])
    if cid_image_black:
        _apply_media(items_by_id, cid_image_black, "image", image_index[cid_image_black.lower()])
    if cid_image_white:
        _apply_media(items_by_id, cid_image_white, "image", image_index[cid_image_white.lower()])

    return items


def _summarize(items: list[dict[str, Any]]) -> str:
    by_label = Counter(int(x.get("label") or 0) for x in items)
    by_modality = Counter(str(x.get("modality") or "") for x in items)
    return f"items={len(items)} labels={dict(by_label)} modalities={dict(by_modality)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="构建比赛提交用数据集（40条，含多模态）")
    parser.add_argument("--input", default=str(DEFAULT_TEXT_DATASET), help="输入 text 数据集 JSON")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="输出提交数据集 JSON")
    parser.add_argument("--images-dir", default=str(DEFAULT_IMAGES_DIR), help="图片目录")
    parser.add_argument("--audio-dir", default=str(DEFAULT_AUDIO_DIR), help="音频目录")
    parser.add_argument("--audio-black", default="", help="指定黑样本 audio 的 case_id（可选）")
    parser.add_argument("--audio-white", default="", help="指定白样本 audio 的 case_id（可选）")
    parser.add_argument("--image-black", default="", help="指定黑样本 image 的 case_id（可选）")
    parser.add_argument("--image-white", default="", help="指定白样本 image 的 case_id（可选）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)
    images_dir = Path(args.images_dir)
    audio_dir = Path(args.audio_dir)

    text_items = _load_list(in_path)
    submission = build_submission_dataset(
        text_items,
        images_dir=images_dir,
        audio_dir=audio_dir,
        audio_black=args.audio_black,
        audio_white=args.audio_white,
        image_black=args.image_black,
        image_white=args.image_white,
    )

    # Basic sanity: keep black:white 1:1 (20:20 by default)
    labels = Counter(int(x.get("label") or 0) for x in submission)
    if labels.get(0, 0) != labels.get(1, 0):
        print(f"[submission] 警告：黑白比例不是 1:1: {dict(labels)}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(submission, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[submission] wrote {out_path} {_summarize(submission)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

