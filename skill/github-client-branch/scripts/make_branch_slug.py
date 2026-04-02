#!/usr/bin/env python3
import re
import sys

BRAND_PHRASES = {
    "喵星": "miaoxing",
    "优品": "youpin",
    "宠物": "pet",
    "用品": "supplies",
    "科技": "tech",
    "集团": "group",
}

CHAR_PINYIN = {
    "喵": "miao",
    "星": "xing",
    "优": "you",
    "品": "pin",
    "宠": "chong",
    "物": "wu",
    "用": "yong",
    "科": "ke",
    "技": "ji",
    "集": "ji",
    "团": "tuan",
}

CHINESE_SUFFIXES = [
    "有限责任公司",
    "股份有限公司",
    "宠物用品有限公司",
    "科技有限公司",
    "集团有限公司",
    "有限公司",
]

ASCII_STOP_WORDS = {
    "company",
    "limited",
    "co",
    "ltd",
    "inc",
    "llc",
}


def strip_suffix(text: str) -> str:
    text = text.strip()
    for suffix in sorted(CHINESE_SUFFIXES, key=len, reverse=True):
        if text.endswith(suffix):
            return text[: -len(suffix)].strip()
    return text


def extract_brand_tokens(text: str):
    tokens = []
    i = 0
    while i < len(text):
        matched = False
        for phrase in sorted(BRAND_PHRASES.keys(), key=len, reverse=True):
            if text.startswith(phrase, i):
                tokens.append(BRAND_PHRASES[phrase])
                i += len(phrase)
                matched = True
                break
        if matched:
            continue

        ch = text[i]
        if ord(ch) < 128:
            tokens.append(ch.lower())
        elif ch in CHAR_PINYIN:
            tokens.append(CHAR_PINYIN[ch])
        else:
            tokens.append("")
        i += 1
    return [t for t in tokens if t]


def normalize_ascii_tokens(text: str):
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return [t for t in text.split("-") if t and t not in ASCII_STOP_WORDS]


def trim_generic_tail(tokens, ascii_mode=False):
    generic_tail = {"pet", "supplies", "tech", "group", "chong", "wu", "yong", "pin"}
    if ascii_mode:
        generic_tail = {"tech", "group"}
    if len(tokens) > 2:
        while tokens and tokens[-1] in generic_tail:
            tokens.pop()
    return tokens


def make_slug(text: str) -> str:
    text = strip_suffix(text)
    ascii_mode = not bool(re.search(r"[\u4e00-\u9fff]", text))
    if ascii_mode:
        tokens = normalize_ascii_tokens(text)
    else:
        tokens = extract_brand_tokens(text)

    tokens = trim_generic_tail(tokens, ascii_mode=ascii_mode)

    if not tokens:
        tokens = ["client"]

    slug = "-".join(tokens[:4])
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "client"


def main():
    if len(sys.argv) < 2:
        print("usage: make_branch_slug.py <company-name>", file=sys.stderr)
        sys.exit(1)
    company = " ".join(sys.argv[1:]).strip()
    print(f"client/{make_slug(company)}")


if __name__ == "__main__":
    main()
