#!/usr/bin/env python3
"""Extract IELTS reading high-frequency phrases into structured JSON."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import warnings
from pathlib import Path


DEFAULT_PHRASES_PDF = Path("/Volumes/data/雅思词汇真经-彩绘版词汇表格/雅思阅读百大高频短语.pdf")
DEFAULT_READING_PDF = Path("/Volumes/data/雅思阅读真经5.pdf")
DEFAULT_OUT = Path("public/assets/english/data/reading-phrases.json")


def import_pdfplumber():
    try:
        import pdfplumber  # type: ignore
    except ImportError as exc:
        raise SystemExit("pdfplumber is required: pip install pdfplumber") from exc
    return pdfplumber


def clean(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    value = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", value)
    return value


def split_phrase_body(body: str) -> tuple[str, str]:
    body = clean(body)
    body = re.split(r"关注微信公众号|扫码关注|免费领取|持续更新", body, maxsplit=1)[0].strip()
    zh_match = re.search(r"[\u4e00-\u9fff]", body)
    if not zh_match:
        return body, ""
    english = clean(body[: zh_match.start()])
    chinese = clean(body[zh_match.start() :])
    return english, chinese


def extract_text(pdf: Path) -> str:
    pdfplumber = import_pdfplumber()
    warnings.filterwarnings("ignore")
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    with pdfplumber.open(str(pdf)) as doc:
        return "\n".join(page.extract_text(x_tolerance=1, y_tolerance=3) or "" for page in doc.pages)


def parse_phrases(text: str) -> list[dict]:
    text = clean(text)
    starts = list(re.finditer(r"(?<!\d)(\d{1,3})\.\s*", text))
    phrases = []
    for index, match in enumerate(starts):
        number = int(match.group(1))
        if not 1 <= number <= 120:
            continue
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        body = text[match.end() : end]
        english, chinese = split_phrase_body(body)
        if not english:
            continue
        phrases.append({"id": number, "phrase": english, "meaning": chinese})

    by_id = {}
    for item in phrases:
        by_id.setdefault(item["id"], item)
    return [by_id[key] for key in sorted(by_id)]


def build(args: argparse.Namespace) -> dict:
    phrases = parse_phrases(extract_text(args.phrases_pdf))
    reading_pages = 0
    try:
        import pypdf

        reading_pages = len(pypdf.PdfReader(str(args.reading_pdf)).pages)
    except Exception:
        reading_pages = 0
    return {
        "meta": {
            "title": "雅思阅读高频短语",
            "phraseCount": len(phrases),
            "source": "雅思阅读百大高频短语结构化抽取",
        },
        "phrases": phrases,
        "readingBook": {
            "title": "雅思阅读真经5",
            "pageCount": reading_pages,
            "status": "local_reference_only",
            "strategy": "仅作为本地学习资料记录；H5 不加载原文件、不展示页面图片，只使用已整理出的结构化学习内容。",
        },
    }


def validate(data: dict) -> list[str]:
    errors = []
    count = data["meta"]["phraseCount"]
    if count < 95:
        errors.append(f"expected at least 95 phrases, got {count}")
    missing = [item for item in data["phrases"] if not item["phrase"] or not item["meaning"]]
    if missing:
        errors.append(f"phrases with missing fields: {len(missing)}")
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phrases-pdf", type=Path, default=DEFAULT_PHRASES_PDF)
    parser.add_argument("--reading-pdf", type=Path, default=DEFAULT_READING_PDF)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    data = build(args)
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(data["meta"], ensure_ascii=False, indent=2))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
