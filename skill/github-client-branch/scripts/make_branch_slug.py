#!/usr/bin/env python3
import re
import sys
import unicodedata

PINYIN_MAP = {
    "喵": "miao",
    "星": "xing",
    "优": "you",
    "品": "pin",
    "宠": "chong",
    "物": "wu",
    "用": "yong",
    "有": "you",
    "限": "xian",
    "公": "gong",
    "司": "si",
}

COMPANY_SUFFIXES = [
    "宠物用品有限公司",
    "有限责任公司",
    "股份有限公司",
    "集团有限公司",
    "科技有限公司",
    "有限公司",
]

ASCII_STOP_WORDS = {
    "company",
    "limited",
    "co",
    "ltd",
    "inc",
    "llc",
    "group",
}


def preprocess(text: str) -> str:
    text = text.strip()
    for suffix in sorted(COMPANY_SUFFIXES, key=len, reverse=True):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
            break
    return text.strip()


def translit_token(ch: str) -> str:
    if ch in PINYIN_MAP:
        return PINYIN_MAP[ch]
    if ord(ch) < 128:
        return ch
    _ = unicodedata.name(ch, "")
    return " "


def make_slug(text: str) -> str:
    text = preprocess(text)
    parts = []
    for ch in text:
        token = translit_token(ch)
        if token:
            parts.append(token)
    raw = " ".join(parts).lower()
    raw = raw.replace("&", " and ")
    raw = re.sub(r"[^a-z0-9]+", "-", raw)
    raw = re.sub(r"-{2,}", "-", raw).strip("-")

    tokens = [t for t in raw.split("-") if t and t not in ASCII_STOP_WORDS]
    if not tokens:
        tokens = ["client"]

    slug = "-".join(tokens[:4])
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "client"


def main():
    if len(sys.argv) < 2:
        print("usage: make_branch_slug.py <company-name>", file=sys.stderr)
        sys.exit(1)
    company = " ".join(sys.argv[1:]).strip()
    slug = make_slug(company)
    print(f"client/{slug}")


if __name__ == "__main__":
    main()
