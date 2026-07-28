#!/usr/bin/env python3
"""Extract structured IELTS vocabulary lists from the colored PDF tables."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Any


DEFAULT_PDF = Path("/Volumes/data/雅思词汇真经-彩绘版词汇表格/合辑list1-56.pdf")
DEFAULT_AUDIO_DIR = Path("/Volumes/data/雅思词汇真经音频")
DEFAULT_OUT = Path("public/assets/english/data/vocab-jing.json")


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


def parse_title(title: str, fallback_list: int) -> dict[str, Any]:
    title = clean(title).replace("\uf0a3", "").replace("£", "")
    match = re.search(r"Chapter\s*(\d+)\s*([^\s]+)?\s+List\s*(\d+)", title, re.I)
    if not match:
        return {"chapter": None, "chapterName": "", "list": fallback_list, "title": f"List {fallback_list}"}
    chapter = int(match.group(1))
    chapter_name = match.group(2) or ""
    list_no = int(match.group(3))
    return {
        "chapter": chapter,
        "chapterName": chapter_name,
        "list": list_no,
        "title": f"Chapter {chapter} {chapter_name} List {list_no}".strip(),
    }


def split_word_pos(value: str) -> tuple[str, str]:
    value = clean(value).replace("\n", " ")
    value = value.replace("*", " *")
    value = re.sub(r"\[.*?\]", "", value).strip()
    value = value.split("[", 1)[0].strip()
    match = re.match(r"(.+?)\s+((?:n|v|adj|adv|prep|conj|pron|num|art)(?:[/.,][a-z]+)?\.?)$", value, re.I)
    if match:
        return normalize_word(match.group(1)), clean(match.group(2))
    match = re.match(r"(.+?)\s+((?:n|v|adj|adv)\b.*)$", value, re.I)
    if match and len(match.group(2)) <= 12:
        return normalize_word(match.group(1)), clean(match.group(2))
    return normalize_word(value), ""


def normalize_word(value: str) -> str:
    value = clean(value)
    value = value.replace(" -", "-").replace("- ", "-")
    parts = value.split()
    if len(parts) > 1 and all(len(part) <= 4 for part in parts):
        return "".join(parts)
    if len(parts) > 2 and any(len(part) == 1 for part in parts):
        return "".join(parts)
    return value


def parse_table_page(page, fallback_list: int) -> dict[str, Any]:
    tables = page.extract_tables()
    text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
    title_source = tables[0][0][0] if tables and tables[0] and tables[0][0] else text.splitlines()[0]
    meta = parse_title(title_source, fallback_list)
    entries = []

    if tables:
        table = tables[0]
        for row in table[2:]:
            if not row:
                continue
            bases = (0, 4, 8) if len(row) >= 12 else (0, 3, 6)
            width = 4 if len(row) >= 12 else 3
            for base in bases:
                if base + width - 1 >= len(row):
                    continue
                if width == 4:
                    number, word_raw, _, definition = row[base : base + 4]
                else:
                    number, word_raw, definition = row[base : base + 3]
                if not number or not word_raw:
                    continue
                if not str(number).strip().isdigit():
                    continue
                word, pos = split_word_pos(str(word_raw))
                if not word:
                    continue
                entries.append(
                    {
                        "no": int(str(number).strip()),
                        "word": word,
                        "pos": pos,
                        "definition": clean(str(definition or "")),
                    }
                )

    if len(entries) < 35:
        coord_entries = parse_coordinate_entries(page)
        if len(coord_entries) > len(entries):
            entries = coord_entries

    entries = [postprocess_entry(entry) for entry in entries]
    meta["entries"] = entries
    return meta


def postprocess_entry(entry: dict[str, Any]) -> dict[str, Any]:
    entry = dict(entry)
    pos = clean(entry.get("pos", ""))
    definition = clean(entry.get("definition", ""))
    zh_match = re.search(r"[\u4e00-\u9fff]", pos)
    if zh_match:
        definition = clean(f"{pos[zh_match.start():]} {definition}")
        pos = clean(pos[: zh_match.start()])
    pos_without_phonetic = re.sub(r"\[.*?\]", "", pos).strip()
    if pos_without_phonetic != pos:
        pos = pos_without_phonetic
    if pos.startswith("["):
        pos_match = re.search(r"\b(n/v|v/n|adj|adv|n|v)\.?", pos, re.I)
        pos = pos_match.group(0) if pos_match else ""
    if definition and pos and definition.startswith(pos):
        definition = clean(definition[len(pos) :])
    definition = re.sub(r"^([\u4e00-\u9fff])\1", r"\1", definition)
    entry["word"] = normalize_word(entry.get("word", ""))
    entry["pos"] = pos
    entry["definition"] = definition
    return entry


def parse_text_entries(text: str) -> list[dict[str, Any]]:
    compact = clean(text)
    pattern = re.compile(r"(\d{1,2})\s+([A-Za-z][A-Za-z *'’./-]+?)\s+((?:n|v|adj|adv|prep|conj|pron|num)[./]?[a-z/]*)?\s+")
    matches = list(pattern.finditer(compact))
    entries = []
    for index, match in enumerate(matches):
        number = int(match.group(1))
        if not 1 <= number <= 60:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(compact)
        definition = clean(compact[match.end() : end])
        word = clean(match.group(2)).replace(" *", "")
        if len(word) > 50 or not definition:
            continue
        entries.append({"no": number, "word": word, "pos": clean(match.group(3) or ""), "definition": definition})
    seen = set()
    unique = []
    for entry in entries:
        key = entry["no"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(entry)
    return unique


def parse_coordinate_entries(page) -> list[dict[str, Any]]:
    words = page.extract_words(x_tolerance=1, y_tolerance=3, keep_blank_chars=False)
    bands = [
        {"num": (25, 45), "word": (40, 126), "pos": (84, 145), "definition": (120, 280)},
        {"num": (275, 298), "word": (293, 383), "pos": (330, 398), "definition": (382, 535)},
        {"num": (535, 556), "word": (553, 643), "pos": (600, 660), "definition": (642, 830)},
    ]
    entries: list[dict[str, Any]] = []

    number_words = [
        token
        for token in words
        if token["text"].isdigit() and 1 <= int(token["text"]) <= 60 and token["top"] > 70
    ]

    for token in number_words:
        number = int(token["text"])
        band = next((item for item in bands if item["num"][0] <= token["x0"] <= item["num"][1]), None)
        if not band:
            continue
        row_tokens = [
            item
            for item in words
            if abs(item["top"] - token["top"]) <= 8 and item["x0"] >= band["word"][0] and item["x0"] <= band["definition"][1]
        ]
        word_tokens = [
            item["text"] for item in row_tokens if band["word"][0] <= item["x0"] < band["word"][1]
        ]
        word_tokens = [item for item in word_tokens if not item.startswith("[")]
        word_text = " ".join(word_tokens)
        pos_text = " ".join(
            item["text"] for item in row_tokens if band["pos"][0] <= item["x0"] < band["pos"][1]
        )
        definition = " ".join(
            item["text"] for item in row_tokens if band["definition"][0] <= item["x0"] < band["definition"][1]
        )
        word, pos_from_word = split_word_pos(word_text)
        pos = clean(pos_text or pos_from_word)
        if definition.startswith(pos):
            definition = definition[len(pos) :].strip()
        if not word:
            continue
        entries.append({"no": number, "word": word, "pos": pos, "definition": clean(definition)})

    by_no: dict[int, dict[str, Any]] = {}
    for entry in entries:
        if entry["no"] not in by_no:
            by_no[entry["no"]] = entry
    return [by_no[number] for number in sorted(by_no)]


def audio_inventory(audio_dir: Path, asset_base: str) -> list[dict[str, Any]]:
    tracks = []
    for path in sorted(audio_dir.glob("*.mp3"), key=lambda p: int(re.search(r"(\d+)", p.name).group(1))):
        match = re.search(r"(\d+)", path.name)
        if not match:
            continue
        number = int(match.group(1))
        target = f"vocab-jing-{number:02d}.mp3"
        tracks.append(
            {
                "id": number,
                "title": f"雅思词汇真经音频 {number}",
                "sourceName": path.name,
                "targetName": target,
                "url": f"{asset_base.rstrip('/')}/vocab-audio/{target}",
                "bytes": path.stat().st_size,
            }
        )
    return tracks


def build(args: argparse.Namespace) -> dict[str, Any]:
    pdfplumber = import_pdfplumber()
    warnings.filterwarnings("ignore")
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    lists = []
    with pdfplumber.open(str(args.pdf)) as doc:
        for index, page in enumerate(doc.pages[:56], start=1):
            item = parse_table_page(page, index)
            if item["entries"]:
                lists.append(item)

    all_words = []
    for item in lists:
        for entry in item["entries"]:
            all_words.append({**entry, "list": item["list"], "chapter": item["chapter"], "chapterName": item["chapterName"]})

    return {
        "meta": {
            "title": "雅思词汇真经",
            "listCount": len(lists),
            "wordCount": len(all_words),
            "audioCount": len(list(args.audio_dir.glob("*.mp3"))),
            "source": "彩绘版词汇表格结构化抽取",
        },
        "assetConfig": {
            "ossBucket": args.oss_bucket,
            "ossRegion": args.oss_region,
            "assetBase": args.asset_base,
            "audioBase": f"{args.asset_base.rstrip('/')}/vocab-audio/",
        },
        "lists": lists,
        "words": all_words,
        "audioTracks": audio_inventory(args.audio_dir, args.asset_base),
        "reading": {
            "title": "雅思阅读真经 5",
            "status": "scan_pdf_pending_ocr",
            "note": "该 PDF 为扫描版，暂不在 H5 直接展示。后续可用 OCR 拆成 Passage 训练。",
        },
    }


def validate(data: dict[str, Any]) -> list[str]:
    errors = []
    if data["meta"]["listCount"] != 56:
        errors.append(f"expected 56 lists, got {data['meta']['listCount']}")
    sparse = [item["list"] for item in data["lists"] if len(item["entries"]) < 35]
    if sparse:
        errors.append(f"sparse lists: {sparse}")
    if data["meta"]["audioCount"] < 1:
        errors.append("no vocab audio found")
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--audio-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--asset-base", default="https://engilish.oss-cn-guangzhou.aliyuncs.com/assets")
    parser.add_argument("--oss-bucket", default="engilish")
    parser.add_argument("--oss-region", default="cn-guangzhou")
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
