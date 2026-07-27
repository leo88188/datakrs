#!/usr/bin/env python3
"""Extract the IELTS 100-sentence study data from the local PDF.

The script intentionally keeps the extracted data structured and complete:
it does not cap vocabulary entries per sentence, and it preserves the
"core vocabulary" / "theme grouping" blocks used by the book.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_DIR = Path("/Volumes/data/100句学完7000雅思单词（跟读解析版）")
DEFAULT_PDF = DEFAULT_SOURCE_DIR / "100个句子记完7000个雅思单词.pdf"
DEFAULT_AUDIO_DIR = DEFAULT_SOURCE_DIR / "100个句子配套音频"
DEFAULT_OUT = Path("public/assets/english/data/ielts100.json")

POS_PATTERN = re.compile(
    r"^(?P<pos>(?:n|v|vi|vt|adj|adv|prep|conj|pron|num|art|aux|modal|phr)"
    r"(?:\./(?:n|v|vi|vt|adj|adv|prep|conj|pron|num|art|aux|modal|phr))*\.)\s*(?P<definition>.*)$",
    re.IGNORECASE,
)
SENTENCE_TITLE_PATTERN = re.compile(r"^Sentence\s+(\d{1,3})\s*$", re.MULTILINE)
SOURCE_PATTERN = re.compile(r"（([^）]*剑桥雅思[^）]*)）")
CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")
IPA_PATTERN = re.compile(r"^/[^/]+/$")
TERM_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9'’()., /-]{1,80}$")


def import_pdfplumber():
    try:
        import pdfplumber  # type: ignore
    except ImportError as exc:
        raise SystemExit("pdfplumber is required: pip install pdfplumber") from exc
    return pdfplumber


def clean_space(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", value)
    value = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[，。；：？！、）])", "", value)
    value = re.sub(r"(?<=[（])\s+(?=[\u4e00-\u9fffA-Za-z])", "", value)
    return value


def normalize_line(line: str) -> str:
    line = line.replace("\ufeff", "").replace("\u3000", " ")
    return clean_space(line)


def extract_pages(pdf_path: Path) -> list[str]:
    pdfplumber = import_pdfplumber()
    warnings.filterwarnings("ignore")
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    pages: list[str] = []
    with pdfplumber.open(str(pdf_path)) as doc:
        for page in doc.pages:
            pages.append(page.extract_text(x_tolerance=1, y_tolerance=3) or "")
    return pages


def find_sentence_boundaries(pages: list[str], skip_pages: int = 10) -> list[tuple[int, int, int]]:
    starts: list[tuple[int, int]] = []
    seen: set[int] = set()
    for page_index, text in enumerate(pages):
        if page_index < skip_pages:
            continue
        for match in SENTENCE_TITLE_PATTERN.finditer(text):
            number = int(match.group(1))
            if 1 <= number <= 100 and number not in seen:
                starts.append((number, page_index))
                seen.add(number)

    starts.sort(key=lambda item: item[0])
    boundaries: list[tuple[int, int, int]] = []
    for index, (number, start_page) in enumerate(starts):
        end_page = starts[index + 1][1] - 1 if index + 1 < len(starts) else min(len(pages) - 1, start_page + 10)
        boundaries.append((number, start_page, end_page))
    return boundaries


def extract_intro(body: str) -> tuple[str, str, str, str]:
    source = ""
    source_match = SOURCE_PATTERN.search(body)
    if source_match:
        source = source_match.group(1).strip()
        before_source = body[: source_match.start()].strip()
    else:
        before_source = body.split("语法笔记", 1)[0].strip()

    before_source = clean_space(before_source)
    zh_match = CHINESE_PATTERN.search(before_source)
    if zh_match:
        english = before_source[: zh_match.start()].strip()
        chinese = before_source[zh_match.start() :].strip()
    else:
        english = before_source
        chinese = ""

    grammar = ""
    grammar_match = re.search(r"语法笔记(.*?)(?:核心词表|$)", body, re.DOTALL)
    if grammar_match:
        grammar = clean_space(grammar_match.group(1))

    return english, chinese, source, grammar


def is_category(line: str) -> bool:
    if line in {"核心词表", "主题归纳"}:
        return True
    if line.endswith("的词：") or line.endswith("有关的词：") or line.endswith("相关的词："):
        return True
    if line.startswith(("表示“", "与“", "和“", "有关“")) and line.endswith("："):
        return True
    return False


def is_term(line: str) -> bool:
    if CHINESE_PATTERN.search(line):
        return False
    if IPA_PATTERN.match(line):
        return False
    if POS_PATTERN.match(line):
        return False
    if line.startswith(("Sentence ", "Review ", "Day ")):
        return False
    if line in {"核心词表", "主题归纳", "语法笔记"}:
        return False
    if len(line.split()) > 6:
        return False
    return bool(TERM_PATTERN.match(line))


def append_tail(entry: dict[str, Any], line: str) -> None:
    if entry.get("notes"):
        entry["notes"][-1] = clean_space(f"{entry['notes'][-1]} {line}")
    else:
        entry["definition"] = clean_space(f"{entry.get('definition', '')} {line}")


def parse_vocab(body: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if "核心词表" not in body:
        return [], {"core": 0, "theme": 0}

    vocab_text = body.split("核心词表", 1)[1]
    lines = [normalize_line(line) for line in vocab_text.splitlines()]
    lines = [line for line in lines if line]

    words: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    section = "core"
    category = "核心词表"

    def flush() -> None:
        nonlocal current
        if not current:
            return
        term = current.get("term", "").strip()
        if term:
            current["definition"] = clean_space(current.get("definition", ""))
            current["notes"] = [clean_space(note) for note in current.get("notes", []) if clean_space(note)]
            words.append(current)
        current = None

    for raw_line in lines:
        line = raw_line.strip()
        if line == "主题归纳":
            flush()
            section = "theme"
            category = "主题归纳"
            continue
        if is_category(line):
            flush()
            if line not in {"核心词表", "主题归纳"}:
                category = line
            continue
        if is_term(line):
            flush()
            current = {
                "term": line,
                "phonetic": "",
                "pos": "",
                "definition": "",
                "section": section,
                "category": category,
                "notes": [],
            }
            continue
        if current and IPA_PATTERN.match(line):
            current["phonetic"] = line.strip("/")
            continue
        pos_match = POS_PATTERN.match(line)
        if current and pos_match:
            current["pos"] = pos_match.group("pos")
            current["definition"] = clean_space(pos_match.group("definition"))
            continue
        if current and line.startswith("【"):
            current.setdefault("notes", []).append(line)
            continue
        if current:
            append_tail(current, line)

    flush()

    seen: set[tuple[str, str]] = set()
    unique_words: list[dict[str, Any]] = []
    for word in words:
        key = (word["term"].lower(), word.get("category", ""))
        if key in seen:
            continue
        seen.add(key)
        unique_words.append(word)

    stats = {
        "core": sum(1 for item in unique_words if item.get("section") == "core"),
        "theme": sum(1 for item in unique_words if item.get("section") == "theme"),
    }
    return unique_words, stats


def parse_sentence(number: int, text: str, start_page: int, end_page: int) -> dict[str, Any]:
    marker_match = re.search(rf"Sentence\s+{number:02d}\s*", text)
    if not marker_match:
        marker_match = re.search(rf"Sentence\s+{number}\s*", text)
    body = text[marker_match.end() :].strip() if marker_match else text.strip()

    english, chinese, source, grammar = extract_intro(body)
    words, word_stats = parse_vocab(body)
    day = 1 + (number - 1) // 5 if number <= 70 else 15 + (number - 71) // 6
    audio_file = f"{number:02d}.mp3" if number < 100 else "100.mp3"

    return {
        "id": number,
        "day": day,
        "sentenceNo": f"{number:02d}",
        "english": english,
        "chinese": chinese,
        "source": source,
        "grammar": grammar,
        "audio": f"audio/{audio_file}",
        "video": f"videos/day{day:02d}.mp4",
        "pageRange": [start_page + 1, end_page + 1],
        "wordStats": word_stats,
        "words": words,
    }


def build_days(sentences: list[dict[str, Any]], videos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_day: dict[int, list[int]] = {}
    for sentence in sentences:
        by_day.setdefault(sentence["day"], []).append(sentence["id"])

    video_by_day = {video["day"]: video for video in videos}
    days = []
    for day in range(1, 20):
        items = by_day.get(day, [])
        days.append(
            {
                "day": day,
                "title": f"第{day:02d}天",
                "sentenceIds": items,
                "start": min(items) if items else None,
                "end": max(items) if items else None,
                "video": f"videos/day{day:02d}.mp4",
                "sourceVideo": video_by_day.get(day, {}).get("sourceName", ""),
            }
        )
    return days


def scan_videos(source_dir: Path) -> list[dict[str, Any]]:
    videos: list[dict[str, Any]] = []
    for path in sorted(source_dir.glob("*.mp4")):
        match = re.search(r"第(\d{2})天", path.name)
        if not match:
            continue
        day = int(match.group(1))
        videos.append(
            {
                "day": day,
                "sourceName": path.name,
                "targetName": f"day{day:02d}.mp4",
                "bytes": path.stat().st_size,
            }
        )
    videos.sort(key=lambda item: item["day"])
    return videos


def scan_audio(audio_dir: Path) -> list[dict[str, Any]]:
    files = []
    for number in range(1, 101):
        name = f"{number:02d}.mp3" if number < 100 else "100.mp3"
        path = audio_dir / name
        files.append(
            {
                "id": number,
                "sourceName": name,
                "targetName": name,
                "bytes": path.stat().st_size if path.exists() else 0,
                "exists": path.exists(),
            }
        )
    return files


def build_dataset(args: argparse.Namespace) -> dict[str, Any]:
    pages = extract_pages(args.pdf)
    boundaries = find_sentence_boundaries(pages)
    sentences: list[dict[str, Any]] = []
    for number, start_page, end_page in boundaries:
        text = "\n".join(pages[start_page : end_page + 1])
        sentences.append(parse_sentence(number, text, start_page, end_page))

    videos = scan_videos(args.source_dir)
    audio = scan_audio(args.audio_dir)
    days = build_days(sentences, videos)

    return {
        "meta": {
            "title": "100句学完7000雅思单词",
            "version": "1.0.0",
            "sourcePdf": args.pdf.name,
            "sentenceCount": len(sentences),
            "wordEntryCount": sum(len(sentence["words"]) for sentence in sentences),
            "coreWordEntryCount": sum(sentence["wordStats"]["core"] for sentence in sentences),
            "themeWordEntryCount": sum(sentence["wordStats"]["theme"] for sentence in sentences),
            "audioCount": sum(1 for item in audio if item["exists"]),
            "videoCount": len(videos),
        },
        "assetConfig": {
            "mode": "oss",
            "ossBucket": args.oss_bucket,
            "ossRegion": args.oss_region,
            "assetBase": args.asset_base,
            "audioBase": f"{args.asset_base.rstrip('/')}/audio/",
            "videoBase": f"{args.asset_base.rstrip('/')}/videos/",
        },
        "days": days,
        "sentences": sentences,
        "mediaInventory": {"audio": audio, "videos": videos},
    }


def validate_dataset(data: dict[str, Any]) -> list[str]:
    errors = []
    if data["meta"]["sentenceCount"] != 100:
        errors.append(f"expected 100 sentences, got {data['meta']['sentenceCount']}")
    if data["meta"]["audioCount"] != 100:
        errors.append(f"expected 100 audio files, got {data['meta']['audioCount']}")
    if data["meta"]["videoCount"] != 19:
        errors.append(f"expected 19 videos, got {data['meta']['videoCount']}")
    sentence_ids = [item["id"] for item in data["sentences"]]
    if sentence_ids != list(range(1, 101)):
        errors.append("sentence ids are not continuous 1..100")
    missing_text = [item["id"] for item in data["sentences"] if not item["english"] or not item["chinese"]]
    if missing_text:
        errors.append(f"sentences missing english/chinese: {missing_text}")
    sparse_words = [item["id"] for item in data["sentences"] if len(item["words"]) < 10]
    if sparse_words:
        errors.append(f"sentences with fewer than 10 word entries: {sparse_words}")
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--audio-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--asset-base", default="https://ielts-luocheng.oss-cn-shanghai.aliyuncs.com/assets")
    parser.add_argument("--oss-bucket", default="ielts-luocheng")
    parser.add_argument("--oss-region", default="cn-shanghai")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    data = build_dataset(args)
    errors = validate_dataset(data)
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
