"""将 test-dataset/txt 下的样本 txt 文件整理为正式 JSON 数据集。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_INPUT_DIR = Path('test-dataset/txt')
DEFAULT_OUTPUT_PATH = Path('test-dataset/evaluation_text_dataset.json')

MANUAL_FRAUD_TYPE_OVERRIDES = {
    'TXT_BLACK_001': '综合型电信网络诈骗',
    'TXT_BLACK_002': '邮寄黄金投资诈骗',
    'TXT_BLACK_003': '校园综合诈骗',
    'TXT_BLACK_004': '婚恋交友诈骗',
    'TXT_BLACK_005': '综合型电信网络诈骗',
    'TXT_BLACK_006': '综合型电信网络诈骗',
    'TXT_BLACK_007': '综合型电信网络诈骗',
    'TXT_BLACK_008': '综合型电信网络诈骗',
    'TXT_BLACK_009': '交友引流刷单诈骗',
    'TXT_BLACK_010': '刷单返利诈骗',
    'TXT_BLACK_011': '综合型电信网络诈骗',
    'TXT_BLACK_012': '节日红包诈骗',
    'TXT_BLACK_013': '兼职招聘诈骗',
    'TXT_BLACK_014': '综合型电信网络诈骗',
    'TXT_BLACK_015': '投资理财诈骗',
    'TXT_BLACK_016': 'AI冒充亲属诈骗',
    'TXT_BLACK_017': '假中奖诈骗',
    'TXT_BLACK_018': '邮寄黄金投资诈骗',
    'TXT_BLACK_019': '冒充班主任收费诈骗',
    'TXT_BLACK_020': '综合型电信网络诈骗',
}


def normalize_content(text: str) -> str:
    value = (text or '').replace('\r\n', '\n').replace('\r', '\n')
    value = re.sub(r'\s+', ' ', value)
    return value.strip()


def _extract_section(raw_text: str, section_name: str, next_section_name: str | None = None) -> str:
    pattern = rf'{re.escape(section_name)}:\n'
    start_match = re.search(pattern, raw_text)
    if not start_match:
        return ''

    start_index = start_match.end()
    if next_section_name:
        next_pattern = rf'\n{re.escape(next_section_name)}:\n'
        next_match = re.search(next_pattern, raw_text[start_index:])
        if next_match:
            end_index = start_index + next_match.start()
            return raw_text[start_index:end_index].strip()
    return raw_text[start_index:].strip()


def parse_txt_sample(raw_text: str) -> dict[str, str]:
    lines = raw_text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    header: dict[str, str] = {}

    for line in lines:
        if not line.strip():
            break
        if ': ' not in line:
            continue
        key, value = line.split(': ', 1)
        header[key.strip()] = value.strip()

    summary = _extract_section(raw_text, 'summary', 'content_candidate')
    content = _extract_section(raw_text, 'content_candidate')
    content = normalize_content(content or summary)

    return {
        'case_id': header.get('case_id', ''),
        'fraud_type': header.get('fraud_type', '待标注'),
        'title': header.get('title', ''),
        'source': header.get('source', ''),
        'publish_time': header.get('publish_time', ''),
        'source_url': header.get('source_url', ''),
        'summary': normalize_content(summary),
        'content': content,
    }


def _infer_label_from_case_id(case_id: str) -> int:
    upper_case_id = (case_id or '').upper()
    if 'WHITE' in upper_case_id:
        return 0
    return 1


def _build_dataset_item(sample: dict[str, str]) -> dict[str, object]:
    case_id = sample.get('case_id', '')
    label = _infer_label_from_case_id(case_id)
    fraud_type = MANUAL_FRAUD_TYPE_OVERRIDES.get(case_id) or sample.get('fraud_type', '待标注') or '待标注'
    if label == 0:
        # 白样本统一标记为 benign，避免历史 TXT 里残留的值污染。
        fraud_type = 'benign'

    return {
        'case_id': case_id,
        'modality': 'text',
        'label': label,
        'fraud_type': fraud_type,
        'title': sample.get('title', ''),
        'content': sample.get('content', ''),
        'file_path': '',
        'source_type': 'real_public_case' if label == 1 else 'real_public_normal',
        'source_url': sample.get('source_url', ''),
        'difficulty': 'medium' if label == 1 else 'easy',
        'expected_risk_level': 'high' if label == 1 else 'low',
        'publish_time': sample.get('publish_time', ''),
    }


def convert_directory_to_dataset(input_dir: Path, output_path: Path) -> list[dict[str, object]]:
    dataset: list[dict[str, object]] = []

    for txt_path in sorted(input_dir.glob('*.txt')):
        raw_text = txt_path.read_text(encoding='utf-8')
        sample = parse_txt_sample(raw_text)
        if not sample.get('case_id'):
            sample['case_id'] = txt_path.stem
        dataset.append(_build_dataset_item(sample))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding='utf-8')
    return dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='将 txt 样本整理为正式 JSON 数据集')
    parser.add_argument('--input-dir', default=str(DEFAULT_INPUT_DIR), help='txt 样本目录')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT_PATH), help='json 输出路径')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = convert_directory_to_dataset(Path(args.input_dir), Path(args.output))
    print(f'已导出 {len(dataset)} 条样本到 {args.output}')


if __name__ == '__main__':
    main()
