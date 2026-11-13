#!/usr/bin/env python3
r"""Exam linter: duplicate stems across papers + item count + difficulty tags.

Usage:
    python exam_lint.py 模拟卷*.tex

Convention: put a comment tag before each item in exam files:
    % D:easy
    \item ...
Allowed tags: easy / medium / hard. Target distribution: 40/40/20 (±10).
"""
import sys
import os
import re
from difflib import SequenceMatcher


def is_answer_file(path):
    name = os.path.basename(path).lower()
    return ("答案" in name) or ("answer" in name) or ("_ans" in name)


def strip_tex(s):
    s = re.sub(r"(?<!\\)%.*", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", s)
    s = re.sub(r"[{}$\\_^&]", " ", s)
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "", s)
    return s


def split_items(text):
    parts = re.split(r"\\item\b", text)
    return parts[1:]


def main():
    files = [f for f in sys.argv[1:] if f.endswith(".tex") and not is_answer_file(f)]
    if not files:
        print("No exam .tex files given (answer files are skipped).")
        return 1

    all_items = []  # (file, index, normalized, tag)
    problems = 0

    for path in files:
        text = open(path, encoding="utf-8").read()
        raw_items = split_items(text)
        tags = {"easy": 0, "medium": 0, "hard": 0, "untagged": 0}
        for i, raw in enumerate(raw_items, 1):
            m = re.search(r"%\s*D:(easy|medium|hard)", raw)
            tag = m.group(1) if m else "untagged"
            tags[tag] += 1
            norm = strip_tex(raw)
            if len(norm) >= 20:
                all_items.append((path, i, norm, tag))
        total = len(raw_items)
        if total == 0:
            print(f"[WARN] {path}: 0 items found")
            problems += 1
            continue
        pct = ", ".join(f"{k}={tags[k]}" for k in ("easy", "medium", "hard", "untagged"))
        print(f"[OK] {os.path.basename(path)}: {total} items ({pct})")
        if tags["untagged"] > 0:
            print(f"       [WARN] {tags['untagged']} items lack a % D: tag")
        for k in ("easy", "medium", "hard"):
            if tags[k] and abs(tags[k] / total - {"easy": .4, "medium": .4, "hard": .2}[k]) > 0.15:
                print(f"       [WARN] difficulty skew: {k} = {tags[k] / total:.0%}")

    dup = 0
    for i in range(len(all_items)):
        for j in range(i + 1, len(all_items)):
            f1, n1, t1, _ = all_items[i]
            f2, n2, t2, _ = all_items[j]
            if f1 == f2:
                continue
            ratio = SequenceMatcher(None, t1, t2).ratio()
            if ratio >= 0.85:
                dup += 1
                print(f"[DUP] {os.path.basename(f1)}#{n1} ~ {os.path.basename(f2)}#{n2}  {ratio:.2f}")
    if dup == 0:
        print("[OK] No cross-paper duplicate stems (>=0.85).")
    else:
        print(f"[WARN] {dup} duplicate pair(s) found — rewrite or change the angle.")
        problems += 1

    return 0 if problems == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
