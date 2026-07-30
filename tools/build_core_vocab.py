#!/usr/bin/env python3
"""Build the 804 core IELTS words page data from the existing 100-sentence set."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public/assets/english/data/ielts100.json"
TARGET = ROOT / "public/assets/english/data/core-vocab.json"

THEMES = [
    ("教育", ["school", "education", "student", "teach", "learn", "academic", "university", "knowledge", "training", "curriculum", "classroom", "literacy", "pupil", "study", "学校", "教育", "学生", "学习", "知识", "课程", "培训"]),
    ("科技", ["technology", "computer", "digital", "data", "internet", "signal", "detect", "machine", "device", "software", "robot", "automation", "innovation", "scientific", "research", "科技", "技术", "数据", "信号", "探测", "机器", "创新", "研究"]),
    ("环境", ["environment", "climate", "pollution", "carbon", "species", "habitat", "forest", "planet", "ecological", "biodiversity", "waste", "sustainable", "resource", "conservation", "环境", "气候", "污染", "碳", "物种", "栖息", "森林", "生态", "资源"]),
    ("城市", ["city", "urban", "housing", "transport", "traffic", "public", "community", "infrastructure", "residential", "suburb", "metropolitan", "dweller", "城市", "都市", "住房", "交通", "公共", "社区", "基础设施", "居民"]),
    ("工作", ["work", "job", "career", "employee", "employer", "labour", "salary", "profession", "industry", "workplace", "staff", "skill", "occupation", "工作", "职业", "员工", "雇主", "劳动", "工资", "行业", "技能"]),
    ("健康", ["health", "medical", "disease", "patient", "doctor", "stress", "diet", "physical", "mental", "treatment", "exercise", "risk", "symptom", "健康", "医疗", "疾病", "病人", "医生", "压力", "饮食", "治疗", "运动", "风险"]),
    ("媒体", ["media", "advertising", "television", "newspaper", "internet", "information", "communicate", "message", "broadcast", "audience", "journalism", "媒体", "广告", "电视", "报纸", "信息", "传播", "观众"]),
    ("政府", ["government", "policy", "law", "public", "authority", "regulation", "state", "tax", "citizen", "legal", "political", "institution", "政府", "政策", "法律", "公共", "权威", "监管", "国家", "税", "公民", "政治", "机构"]),
    ("文化", ["culture", "language", "tradition", "civilisation", "history", "heritage", "art", "identity", "custom", "society", "social", "文化", "语言", "传统", "文明", "历史", "遗产", "艺术", "身份", "社会"]),
    ("全球化", ["global", "international", "migration", "foreign", "trade", "world", "cross-border", "multinational", "export", "import", "tourism", "全球", "国际", "移民", "外国", "贸易", "世界", "出口", "进口"]),
    ("消费", ["consumer", "purchase", "market", "advertise", "brand", "shop", "product", "demand", "supply", "price", "commercial", "消费", "购买", "市场", "广告", "品牌", "产品", "需求", "价格", "商业"]),
    ("犯罪", ["crime", "criminal", "prison", "punish", "law", "police", "security", "violent", "illegal", "justice", "offence", "犯罪", "罪犯", "监狱", "惩罚", "警察", "安全", "暴力", "违法", "司法"]),
    ("交通", ["transport", "vehicle", "car", "road", "traffic", "commute", "rail", "airport", "journey", "passenger", "mobility", "交通", "车辆", "汽车", "道路", "通勤", "铁路", "机场", "乘客"]),
    ("老龄化", ["elderly", "ageing", "aging", "retire", "retirement", "senior", "old", "pension", "longevity", "老龄", "老人", "退休", "年长", "养老金", "长寿"]),
    ("儿童", ["child", "children", "young", "parent", "family", "teenager", "adolescent", "infant", "youth", "generation", "儿童", "孩子", "年轻", "父母", "家庭", "青少年", "一代"]),
    ("商业", ["business", "company", "corporate", "industry", "market", "management", "profit", "enterprise", "investment", "customer", "商业", "公司", "企业", "行业", "市场", "管理", "利润", "投资", "客户"]),
    ("金融", ["finance", "financial", "money", "bank", "capital", "investment", "income", "cost", "tax", "budget", "economic", "economy", "金融", "资金", "银行", "资本", "投资", "收入", "成本", "预算", "经济", "税"]),
    ("旅游", ["tourism", "tourist", "travel", "destination", "hotel", "visitor", "journey", "heritage", "attraction", "旅游", "游客", "旅行", "目的地", "酒店", "参观", "旅程", "景点"]),
    ("能源", ["energy", "fuel", "oil", "solar", "renewable", "electricity", "power", "carbon", "emission", "resource", "能源", "燃料", "石油", "太阳能", "可再生", "电力", "排放", "资源"]),
    ("食品安全", ["food", "agriculture", "farm", "crop", "nutrition", "diet", "safety", "chemical", "organic", "supply", "食品", "农业", "农场", "作物", "营养", "饮食", "安全", "化学", "有机", "供应"]),
]

FALLBACK_THEMES = ["科技", "文化", "工作", "政府", "环境", "商业", "城市", "健康", "教育", "全球化"]


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def alpha_key(term: str) -> str:
    match = re.search(r"[A-Za-z]", term)
    return match.group(0).upper() if match else "#"


def classify(entry: dict, sentence: dict, index: int) -> str:
    haystack = " ".join(
        [
            entry.get("term", ""),
            entry.get("definition", ""),
            sentence.get("english", ""),
            sentence.get("chinese", ""),
            sentence.get("grammar", ""),
        ]
    ).lower()
    if any(keyword in haystack for keyword in ["finance", "financial", "money", "bank", "capital", "investment", "income", "cost", "budget", "economic", "economy", "金融", "资金", "银行", "资本", "投资", "收入", "成本", "预算", "经济"]):
        return "金融"
    if any(keyword in haystack for keyword in ["crime", "criminal", "prison", "punish", "police", "security", "violent", "illegal", "justice", "offence", "犯罪", "罪犯", "监狱", "惩罚", "警察", "暴力", "违法", "司法"]):
        return "犯罪"
    for theme, keywords in THEMES:
        if any(keyword in haystack for keyword in keywords):
            return theme
    return FALLBACK_THEMES[index % len(FALLBACK_THEMES)]


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    words = []
    for sentence in data["sentences"]:
        for item in sentence["words"]:
            if item.get("section") != "core":
                continue
            term = clean(item.get("term", ""))
            if not term:
                continue
            words.append(
                {
                    "id": len(words) + 1,
                    "term": term,
                    "alpha": alpha_key(term),
                    "theme": classify(item, sentence, len(words)),
                    "phonetic": clean(item.get("phonetic", "")),
                    "pos": clean(item.get("pos", "")),
                    "definition": clean(item.get("definition", "")),
                    "sentenceId": sentence["id"],
                    "sentence": sentence["english"],
                    "translation": sentence["chinese"],
                }
            )

    theme_counts = Counter(word["theme"] for word in words)
    alpha_counts = Counter(word["alpha"] for word in words)
    output = {
        "meta": {
            "title": "雅思基础通关核心词",
            "source": "从 100 句学习数据的核心词表抽取整理",
            "wordCount": len(words),
            "themeCount": len(theme_counts),
            "version": "2026-07-30",
        },
        "themes": [{"name": name, "count": theme_counts.get(name, 0)} for name, _ in THEMES if theme_counts.get(name, 0)],
        "alphas": [{"letter": letter, "count": alpha_counts.get(letter, 0)} for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if alpha_counts.get(letter, 0)],
        "words": words,
    }
    TARGET.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {TARGET} with {len(words)} words")


if __name__ == "__main__":
    main()
