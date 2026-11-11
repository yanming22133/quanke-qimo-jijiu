#!/usr/bin/env python3
"""Post-generation quality checker for LaTeX review materials.
Usage: python quality_check.py *.tex
Checks: enumerate balance, required packages, tcolorbox title safety.
"""

import sys
import re
import os

EXIT_CODE = 0

def check_file(filepath):
    global EXIT_CODE
    print(f"\n{'='*60}")
    print(f"Checking: {filepath}")
    print(f"{'='*60}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')

    # 1. Enumerate balance
    begins = content.count(r'\begin{enumerate}')
    ends = content.count(r'\end{enumerate}')
    if begins != ends:
        print(f"  FAIL: enumerate mismatch: {begins} begins vs {ends} ends")
        # Find the first mismatch line
        depth = 0
        for i, line in enumerate(lines, 1):
            if r'\begin{enumerate}' in line:
                depth += 1
            if r'\end{enumerate}' in line:
                depth -= 1
                if depth < 0:
                    print(f"    First extra \\end{{enumerate}} at line {i}")
                    break
        EXIT_CODE = 1
    else:
        print(f"  PASS: enumerate balanced ({begins} pairs)")

    # 2. tcolorbox title safety: no [ inside [...] title
    pattern = re.compile(r'\\begin\{(?:key|def|warn|formula|info|note)box\}\[.*\[.*\]')
    matches = pattern.findall(content)
    if matches:
        print(f"  FAIL: Found {len(matches)} tcolorbox titles with nested [ ]:")
        for m in matches[:3]:
            print(f"    {m[:80]}...")
        EXIT_CODE = 1
    else:
        print(f"  PASS: No nested [ ] in tcolorbox titles")

    # 3. Required packages check
    required = {
        'ctexart': r'\\documentclass\[.*\]\{ctexart\}',
        'ulem': r'\\usepackage(\[.*?\])?\{ulem\}',
        'fancyhdr': r'\\usepackage\{fancyhdr\}',
        'tcolorbox': r'\\usepackage\{tcolorbox\}',
        'enumitem': r'\\usepackage\{enumitem\}',
    }
    has_preamble = bool(re.search(r'\\input\{[^}]*preamble', content))
    if has_preamble:
        print("  SKIP: packages live in an \\input preamble (verify the preamble file separately)")
    else:
        for pkg, pattern in required.items():
            if re.search(pattern, content):
                print(f"  PASS: {pkg} package found")
            else:
                print(f"  FAIL: {pkg} package MISSING")
                EXIT_CODE = 1
    # 3b. tcolorbox titles must not contain an ASCII comma (pgfkeys splits keys on it)
    title_comma = re.findall(r'\\begin\{(?:key|def|warn|formula|info|note|teal)box\}\[[^\]]*,[^\]]*\]', content)
    if title_comma:
        print(f"  FAIL: {len(title_comma)} tcolorbox title(s) contain an ASCII comma — remove it or wrap the title in braces:")
        for m in title_comma[:3]:
            print(f"    {m[:90]}")
        EXIT_CODE = 1
    else:
        print("  PASS: No ASCII comma inside tcolorbox titles")

    # 4. No table environment inside tcolorbox
    if re.search(r'\\begin\{tcolorbox\}.*\\begin\{table\}', content, re.DOTALL):
        print(f"  FAIL: Found \\begin{{table}} inside tcolorbox")
        EXIT_CODE = 1
    else:
        print(f"  PASS: No table float inside tcolorbox")

    # 5. Fancyhdr headers in English (warn only, not fail)
    header_pattern = re.compile(r'\\fancyhead\[.*\]\{([^}]*[一-鿿][^}]*)\}')
    chinese_headers = header_pattern.findall(content)
    if chinese_headers:
        print(f"  WARN: Chinese characters in fancyhdr: {chinese_headers[:3]}")
    else:
        print(f"  PASS: Headers appear to be English-only")

    # 6. No emoji
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF☀-➿⭐❤]')
    emoji_lines = []
    for i, line in enumerate(lines, 1):
        if emoji_pattern.search(line):
            emoji_lines.append(i)
    if emoji_lines:
        print(f"  FAIL: Emoji found at lines: {emoji_lines[:10]}")
        EXIT_CODE = 1
    else:
        print(f"  PASS: No emoji detected")

    # 7. All \begin{X} have matching \end{X} (major environments only)
    for env in ['document', 'enumerate', 'itemize', 'tcolorbox', 'keybox', 'defbox',
                 'warnbox', 'formulabox', 'infobox', 'notebox', 'center']:
        opens = content.count(f'\\begin{{{env}}}')
        closes = content.count(f'\\end{{{env}}}')
        if opens != closes:
            # tcolorbox variants are aliased via \newtcolorbox, skip those
            if env in ['keybox', 'defbox', 'warnbox', 'formulabox', 'infobox', 'notebox']:
                continue  # these close as \end{tcolorbox}
            print(f"  WARN: {env}: {opens} opens vs {closes} closes")
        # else: silent pass for brevity

    # 7b. Exam-specific checks: answer space present, no answers leaked into the paper
    fname = os.path.basename(filepath)
    lower = fname.lower()
    is_answer = ("答案" in fname) or ("answer" in lower) or ("_ans" in lower)
    is_exam = (("模拟卷" in fname) or lower.startswith("exam") or ("mock_exam" in lower)) and not is_answer
    if is_exam:
        vspaces = len(re.findall(r'\\vspace\*?\{', content))
        if vspaces < 3:
            print(f"  FAIL: exam has only {vspaces} \\vspace — add writing space after each big question (Step 3.5.1)")
            EXIT_CODE = 1
        else:
            print(f"  PASS: answer space present ({vspaces} \\vspace)")
        if "参考答案" in content or "评分标准" in content:
            print("  FAIL: exam file contains '参考答案/评分标准' — move answers to the answer file")
            EXIT_CODE = 1
        else:
            print("  PASS: no answers leaked into the paper")

    return EXIT_CODE == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python quality_check.py file1.tex [file2.tex ...]")
        sys.exit(1)

    all_pass = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_pass = False

    print(f"\n{'='*60}")
    if all_pass:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED — fix before compiling")
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
