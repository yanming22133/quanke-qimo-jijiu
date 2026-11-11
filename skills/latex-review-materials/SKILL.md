---
name: latex-review-materials
description: Use when generating Chinese LaTeX review materials from any course content (PDFs, PPTs, DOCX, lecture recordings). Extracts the real exam format, scope and emphasis first, then builds chapter summaries, exercises, and 2-3 mock papers with separate answer files, scoring rubrics, answer space for writing, and case-based questions. Includes per-type playbooks for STEM, humanities, ideology/politics, management, law and medicine.
---

# LaTeX Chinese Review Materials Generator (Universal)

> One-click: any course materials → 6--8 PDFs (summary, exercises, 2--3 exams + answers).

## Output Files

Generate 6--8 files: 2 base files + 2 per exam. Default 3 exams = 8 files; small courses (≤3 chapters) = 2 exams = 6 files.

| File | Purpose |
|------|---------|
| `知识点汇总.tex` | Per-chapter detailed review notes |
| `章节练习.tex` | Exercises with answers inline in notebox |
| `模拟卷A.tex` | Mock Exam A — questions ONLY (chapters 1st half) |
| `模拟卷A_答案.tex` | Exam A solutions with scoring rubrics |
| `模拟卷B.tex` | Mock Exam B — questions ONLY (chapters 2nd half) |
| `模拟卷B_答案.tex` | Exam B solutions with scoring rubrics |
| `模拟卷C.tex` | Mock Exam C — questions ONLY (synthesis/cross-chapter) |
| `模拟卷C_答案.tex` | Exam C solutions with scoring rubrics |

**3-exam split strategy** (maximizes topic coverage with no overlap):
- Exam A: chapters 1--N/3 (foundations)
- Exam B: chapters N/3+1 -- 2N/3 (core)
- Exam C: chapters 2N/3+1 -- N + cross-chapter synthesis (advanced/integration)

For small courses (≤3 chapters): fall back to 2 exams (A: Ch1-2, B: Ch2-3 with overlap allowed).

Each exam uses the format extracted in Step 0. Fallback only if nothing is known: 20 MC (×1) + 10 multi (×2) + 10 T/F (×1) + 5 essay/calc (×10) = 100 pts, 120 min. Keep question topics NON-OVERLAPPING across exams: an exam topic appearing in Exam A should NOT appear in Exam B or C.

**Critical rules**:
- `模拟卷*.tex` = questions ONLY + scratch paper. NEVER put answers in exam files.
- `模拟卷*_答案.tex` = separate answer files with scoring rubrics.
- Use Chinese filenames as shown above. For English-only courses, use English filenames instead: `chapter_summary.tex`, `chapter_exercises.tex`, `mock_exam_A/B/C.tex`, `mock_exam_A/B/C_answers.tex`.

- User asks to generate "复习资料", "考点总结", "模拟卷", "练习题"
- User provides course materials (PDF/PPT/DOCX) and wants PDF output
- Any course type, any language mix (Chinese, English, bilingual)

**Skip when**: only 1-2 pages of material; user needs single file only; pure English without CJK.

---

## Step 0: Extract Exam Intelligence (BEFORE writing anything)

The biggest failure mode is generating a generic paper that does not match the real exam. Extract and write down this table first; put a one-paragraph "exam brief" on page 1 of the summary and in the delivery README.

| Item | Where to find it | Example |
|------|------------------|---------|
| Date / duration | syllabus, last lecture | [date], [duration] |
| Question types & points | recording, syllabus | [e.g.] 20 MC×1 + 4 short×10 + 2 essay×20 |
| Scope in / out | teacher's explicit statements | Ch1--6; **Ch7 excluded** |
| **Authoritative source** | teacher's rule | **textbook / PPT / both / past papers** |
| Emphasis / weighting | recording, repeated topics | Ch3 = core; later chapters = basics only |
| Terminology variants | textbook vs slides | textbook "Term A" = slides "Term B" |
| Aids allowed | syllabus | closed book |

Rules:
- **Never** default to 20 MC + 10 multi + 10 T/F + 5 essay unless nothing else is available. That format is a fallback, not the default.
- If the exam has no multiple-choice, do not invent MC. If it has one 30-point case, build the paper around cases.
- If a recording exists, transcribe it first. The last lecture almost always contains format, scope and emphasis.
- Exclusions are exam content too: "Ch4 and Ch9 are NOT in scope" must appear on page 1.

### 0.1 Intel inventory: what you can get varies by course

Different courses give you different amounts of information. Record which tier you are in, and never silently upgrade an assumption into a fact.

| Available material | What you can extract | What to do about the rest |
|---|---|---|
| Full recording / transcript | format, scope, exclusions, emphasis, terminology | best case — quote it as the exam brief |
| Syllabus / 教学大纲 | chapters, weights, sometimes format | structure from syllabus; emphasis still unknown |
| Past exams (past 3--5 years) | question types, style, repeated topics | infer format from them; say "inferred from past papers" |
| Slides only | topics, terminology, "重点/考点" markers | scope = slides; exam may be PPT-based — ask |
| Textbook only | chapter structure and depth | assume full coverage, no format info |
| Nothing | — | **ask the user** (format + scope are the two questions worth asking); if impossible, state assumptions on page 1 |

**Authoritative-source rule**: write down which of `textbook / PPT / both / past papers` the exam follows. If unknown, ask before generating. Do not assume the textbook wins — many courses examine the slides.

### 0.2 Terminology handling depends on the authoritative source

| Authoritative source | Which term to use |
|---|---|
| textbook | textbook term primary, slide term in parentheses on first use |
| PPT | slide term primary, textbook term in parentheses |
| both / mixed | use the term that appears in the exam stem or past papers; list both in a "术语对照" box |
| unknown | use the term most frequent in the instructor's materials and flag it |

Always add one line: "两种表述均有效" only if the teacher actually said so; otherwise do not invent leniency.

---

## Step 1: Read ALL Materials

**PDF — ALWAYS use `pdftotext` first** (the `Read` tool falsely reports "password-protected" on many unencrypted PDFs):

```bash
pdftotext -layout "file.pdf" - 2>/dev/null | head -N   # N = pages needed
# For specific pages: pdftotext -layout -f 1 -l 30 "file.pdf" -
```

Only if `pdftotext` produces garbled output: try `Read` as fallback. If both fail, use `python -c "import PyPDF2; ..."` to attempt extraction.

**DOCX/PPTX — Python `zipfile` + `xml.etree.ElementTree`** (see reference for template). Always use `glob.glob()` to avoid Windows Chinese path bugs.

**Scanned textbook (no text layer) — OCR pipeline:**
1. Check: `pdftotext -f 1 -l 3 book.pdf -` prints nothing → it is a scanned PDF.
2. Use GPU OCR (PaddleOCR models via `rapidocr_onnxruntime` + `onnxruntime-gpu`, `use_cuda: true`): ~1.5 s/page at 200 dpi on an RTX 4070; CPU is ~30 s/page, so GPU matters.
3. Get chapter page ranges from the scanned TOC (OCR the first ~10 pages) or PDF bookmarks: `PDF page = printed page + offset`.
4. OCR chapter by chapter, one `chN.txt` per chapter, each page prefixed with `【第 N 页】` for later citation.
5. Skip chapters the teacher explicitly excluded — do not waste GPU time on them.
6. Tell the user the OCR error rate (~3%) and that numbers/punctuation must be checked against the paper book.

**Lecture recordings**: transcribe first (whisper / funasr / provided transcript). The last lecture usually states exam format, scope, exclusions and emphasis — this is Step 0 input, not optional background.

**After reading, extract and record:**
- Chapter count, structure, which chapters have/don't have materials
- Course name, instructor, textbook, exam format, grading weights (from syllabus/Ch0)
- Instructor's emphasis: "重点"/"考点" labels, repeated topics, past exam topic lists
- Language: all-Chinese / all-English / bilingual → determines output language
- Any user-provided priority list or constraints (target score, study time)

## Step 2: Detect Course Type

```
Signals in materials:
  Formulas, derivations, "证明", Greek letters, numbers to compute   → QUANTITATIVE (math/physics/econ-theory)
  Code, architecture, circuits, protocols, "设计/实现"               → ENGINEERING
  Events, dates, concepts, policies, ideology, legal articles        → QUALITATIVE (humanities/social science)
  Official documents, "精神/意义/新时代", value judgments, 时政        → IDEOLOGICAL (思政/政治理论)
  Mixed formulas + cases (management, finance, law)                  → MIXED
```

**Templates:**

- **Quantitative**: Background → Core Models → Assumptions → Derivations → Properties → Testing → Mistakes
- **Engineering**: Principles → Architecture/Design → Key Mechanisms → Formulas/Calculations → Examples → Trade-offs → Mistakes
- **Qualitative (humanities)**: Background → Core Concepts → Framework → Key Arguments → Comparisons → Significance → Confusions
- **Ideological (思政)**: 背景与定位 → 核心概念/原文表述 → 逻辑框架（为什么/是什么/怎么做）→ 联系实际 → 常见表述错误
- **Mixed (management/law/medicine)**: Concepts → Frameworks → Case Application → Decision Rules → Mistakes

Pick the template that fits. For mixed courses, vary per chapter. See `references/course-types.md` for the per-type playbook (marking logic, answer space, fatal mistakes).

### 2.1 Exam design differs sharply by course type

A paper that works for management will fail for 思政 and for engineering. Set these before writing questions.

| Course type | Typical question types | Answer space | Marking logic | Fatal mistakes |
|---|---|---|---|---|
| **Engineering** | 选择、填空、简答、计算、画图、设计 | 计算 8--12 cm；画图半页（给坐标/网格）；证明 10 cm | 步骤分：公式→代入→结果→单位；画图看规范 | 只写结果无过程；单位/量纲错；图无标注 |
| **Humanities** | 名词解释、简答、材料分析、论述 | 名词 4 cm；简答 8 cm；论述 1.5 页 | 观点 + 论据 + 结构 + 表达；允许多元答案但要论证 | 只罗列不论证；无文本/史料证据；时代错置 |
| **Ideological (思政)** | 单选、多选、判断、简答、材料分析、论述 | 简答 8--10 cm；材料分析 12--15 cm；论述整页 | **踩点给分**，关键词必须是官方表述；多选按“少选得部分分、错选不得分” | 口语化、自由发挥、引用错、观点偏差；用旧表述 |
| **Quantitative** | 选择、填空、计算、证明 | 计算 8--10 cm；证明 10--12 cm | 步骤分 + 结果分；有效数字/近似条件 | 跳步；条件写错；结论与假设不符 |
| **Mixed (mgmt/law/med)** | 选择、简答、案例分析、论述 | 每小问 3--4 cm；论述整页 | 框架 + 案例事实 + 结论；法学按“结论—依据—涵摄” | 只背理论不结合案例；结论无依据 |

**Type-specific rules:**

- **Engineering**: provide a formula sheet / constants table at the front; require units in answers; leave grid space for graphs; state whether calculators are allowed.
- **Humanities**: the answer file gives "要点 + 可接受的其他观点", not a single model answer; quote primary texts where the course does.
- **Ideological**: every answer must anchor to the textbook/official document wording; add a "表述对照" box (口语说法 → 规范说法); never invent policy quotes; check the latest 会议精神/时政 within 12 months; flag any uncertain quote as "以教材原文为准".
- **Quantitative**: state assumptions and significance level; answers show the full derivation chain.

## Step 3: Plan Content with Priority Weighting

**Chapter priority logic** (use the first that applies):
1. User explicitly says "Chapter X is most important" or provides a priority topic list → weight heavily
2. Instructor's materials mark topics as "重点"/"考点" → weight accordingly
3. Past exam questions cluster on certain chapters → weight accordingly
4. Default: equal weight across all chapters

**Per-chapter minimums:**
- Summary: 150+ lines, 5+ subsections, 1+ comparison table/timeline, [CORE]/[KEY]/[NOTE] labels
- Exercises: 10+ questions (4-5 MC, 2-3 multi, 2-3 fill-blank, 2 short, 1 essay). Answers in `notebox`.
- Exam: use the format from Step 0 and the type-specific table in §2.1 (the 20+10+10+5 / 100 pts / 120 min shape is a fallback only)
- Exam answers: separate file, scoring rubrics with explicit point breakdowns per question

**Missing chapters**: reconstruct from other materials. If nothing available, flag in output and use standard textbook knowledge for that topic.

**Language output**: Match the EXAM language. If English exam → English questions + bilingual explanations. If Chinese exam → all Chinese. Let source materials determine this.

**Terminology alignment**: apply the table in §0.2 — the primary term depends on whether the exam follows the textbook, the PPT, both, or past papers. Put the other name in parentheses on first use and never mix them silently.

## Step 3.5: Design the Paper (answer space, cases, page breaks)

### 3.5.1 Answer space (MANDATORY)

A mock exam without writing space is a question list, not an exam. Every question that requires writing must be followed by blank space sized to the expected answer.

| Question type | Blank space | LaTeX |
|---|---|---|
| 单选 / 判断 | none (options inline) | — |
| 填空 | 0.8--1.2 cm per blank | `\vspace{1cm}` |
| 名词解释 | 3 cm | `\vspace{3cm}` |
| 简答 (10 pts) | 3--4 cm | `\vspace{3.2cm}` |
| 计算 / 证明 | 6--8 cm | `\vspace{7cm}` |
| 论述 (25 pts) | 9--12 cm, or a full page | `\vspace{10cm}` |
| 案例分析 (30 pts, 3 小问) | 3--4 cm after EACH sub-question | `\vspace{3.2cm}` ×3 |

Rules:
- Put `\vspace{...}` immediately after the sub-question it belongs to, never after the section heading.
- If the paper would overflow, insert `\newpage` before the next big question instead of shrinking the space.
- End every paper with a scratch area: `\newpage\section*{草稿区}\mbox{}\newpage\mbox{}\newpage`.
- Verify: each 论述/案例 sub-question has a following `\vspace` in the source (the quality checker enforces at least 3 per exam file).

### 3.5.2 Case-based questions (when the course supplies cases)

- Put the case in a breakable `infobox`, 500--900 Chinese characters, **self-contained**: students must not need the textbook or original PDF.
- Structure: case box → "请回答：" → 3 sub-questions with explicit points (e.g. 9+8+8).
- Each sub-question must map to a course framework (five forces / value chain / generic strategy / diversification / entry mode), not general knowledge.
- Answer file: scoring points per sub-question plus a short "参考思路" box — not a full model essay.
- If the folder has N cases and you need 2N big questions, reuse cases with DIFFERENT angles (same case for "five forces" in one paper, "value chain" in another) and document the mapping in the README.
- Never split a case box from its questions (see 3.5.3).

### 3.5.3 Page layout for exams

- `\newpage` before 论述题 and 案例分析题 so each case starts on a fresh page.
- Case box + "请回答" + first sub-question should fit on one page.
- Per-paper header: `\fancyhead[R]{Mock Exam A}` (English only).
- Paper title block: course, "期末模拟试卷 X", time, full marks, closed-book, and the chapter coverage line.

## Step 4: Dispatch Agents (6-8 Parallel)

Always generate ALL files simultaneously as background agents:
1. `知识点汇总.tex` (or `chapter_summary.tex` for English courses)
2. `章节练习.tex` (or `chapter_exercises.tex`)
3. `模拟卷A.tex` — Exam A (1st chunk of chapters)
4. `模拟卷A_答案.tex` — Exam A solutions
5. `模拟卷B.tex` — Exam B (2nd chunk)
6. `模拟卷B_答案.tex` — Exam B solutions
7. `模拟卷C.tex` — Exam C (3rd chunk + cross-chapter synthesis)
8. `模拟卷C_答案.tex` — Exam C solutions

For ≤3 chapters: use 4 agents (summary + exercises + 2 exams). Each exam covers DIFFERENT chapter groups to maximize topic coverage with zero overlap.

```
## AGENT PROMPT TEMPLATE

Write LaTeX file at [ABSOLUTE PATH].

Course: [NAME], [INSTITUTION], [INSTRUCTOR]
Textbook: [TITLE, EDITION]
Exam language: [EN/CN/BILINGUAL]

### Preamble (copy exactly):
[PASTE FULL PREAMBLE FROM references/latex-format-rules.md §15]

### CHAPTER-BY-CHAPTER CONTENT:

Ch N: [TITLE] — MUST cover:
- Topic 1: [specific concept/formula/event]
- Topic 2: [specific concept/formula/event]
- ... (5-8 specific topics per chapter)
- [EXAM] questions on: [specific calculation/essay types]
- Key terms to include: [list 5-10 English+Chinese terms]

[... repeat for all chapters ...]

### Mandatory Rules:
1-9 [paste the 9 rules from Step 5 below]

### Post-write checklist (run yourself):
- [ ] `grep -c '\\begin{enumerate}' file.tex` == `grep -c '\\end{enumerate}' file.tex` ?
- [ ] `grep '\\usepackage{ulem}' file.tex` returns match?
- [ ] `grep -P '[\\x{1F300}-\\x{1F9FF}]' file.tex` returns empty?
- [ ] All tcolorbox titles are English or simple Chinese without [ inside?
- [ ] (exam files) every 论述/案例 sub-question followed by `\vspace`?
- [ ] No 参考答案/评分标准 in exam files?
- [ ] Format matches Step 0 (not the 20+10+10+5 fallback)?

Target: [N] lines. Write file now.
```

**The per-chapter content list is the most important part.** Don't write "summarize Ch1" — enumerate every specific concept, formula, event, and term that must appear. The quality of this list determines the quality of the output.

## Step 5: Quality Check (BEFORE compiling)

```bash
python references/quality_check.py *.tex
```

If any check FAILS → fix with Edit, re-run check, THEN compile. The checker validates: enumerate balance, required packages, no `[` in tcolorbox titles, no emoji, no table floats inside tcolorbox, English-only headers.

## Step 6: Compile and Verify

```bash
# compile every .tex in the working dir (handles Chinese filenames + \input{preamble})
for f in *.tex; do
  base="${f%.tex}"
  xelatex -interaction=nonstopmode -halt-on-error "$f" >/dev/null 2>&1
  xelatex -interaction=nonstopmode -halt-on-error "$f" >/dev/null 2>&1
  if [ $? -ne 0 ]; then echo "FAILED: $f"; fi
done
# Verify: no LaTeX errors
grep -l '^!' *.log || echo "no errors"
# Check pages
for p in *.pdf; do echo "$p: $(pdfinfo "$p" | awk '/Pages/{print $2}')"; done
```

Notes:
- If the project uses `\input{preamble.tex}`, keep all files in one directory and compile from there.
- Compile twice for TOC and cross-references; long documents (30+ pages) may need a third pass.
- Do not delete `.log` before running `grep '^!'`.

## Step 7: Error Recovery

If compilation fails:
1. `grep '^!' *.log | head -5` — find first error
2. Common fixes: missing `\usepackage[normalem]{ulem}` → add to preamble; enumerate mismatch → remove stray `\end{enumerate}`; undefined command → add `\DeclareMathOperator` or `\newcommand`
3. Fix with Edit, re-run Step 5, re-compile
4. If an agent is still writing: `TaskStop` it first, then fix

---

## 9 Mandatory Rules (in EVERY agent prompt)

```
1. \documentclass[12pt,a4paper,fontset=fandol]{ctexart}
2. ZERO emoji — use [CORE][KEY][NOTE][EXAM][TIP] labels
3. Tables: \medskip\begin{center}\begin{tabular}... — NEVER \begin{table}[h] inside tcolorbox
4. Headers: ENGLISH ONLY in fancyhdr
5. Colors: ALL \definecolor{}{RGB}{...} in preamble
6. Compile: xelatex twice; clean aux
7. tcolorbox titles: English or SHORT Chinese. NEVER put [ inside [...] title
8. \uline{} → MUST have \usepackage[normalem]{ulem} in preamble
9. \begin{enumerate} count MUST equal \end{enumerate} count — COUNT THEM after writing
10. Exam files: leave \vspace after every big question (论述 9--12 cm, 案例每小问 3--4 cm); never put 参考答案 inside exam files
```

## Common Errors (quick reference)

| Error | Fix |
|-------|-----|
| `\uline` undefined | Add `\usepackage[normalem]{ulem}` |
| enumerate mismatch → blank PDF | Remove stray `\end{enumerate}` |
| `Missing $ inserted` from tcolorbox title | Use English title, no `[` inside `[...]` |
| `\cov`/`\plim` undefined (quant. courses) | `\DeclareMathOperator{\cov}{Cov}` / `\newcommand{\plim}{\operatorname{plim}}` |
| `\E`/`\var` already defined | Use `\mathbb{E}` or skip (amsmath conflict) |
| Read tool says "password-protected" | Use `pdftotext` instead (Read tool bug) |
| Chinese in fancyhdr | English only |

## Anti-Patterns

| Mistake | Fix |
|---------|-----|
| "summarize Ch1" as agent prompt | List every specific topic/formula/event |
| Forcing quantitative template on history | Step 2 type detection |
| Answers inside mock_exam.tex | Separate answer file always |
| Skipping quality check before compile | Step 5 on every file |
| Using Read for PDF → false encryption error | `pdftotext` first |
| No blank space under essay/case questions | Add `\vspace` per Step 3.5.1 |
| Case box split across pages from its questions | `\newpage` before 论述/案例分析 (Step 3.5.3) |
| Exam requires the textbook / original case PDF | Rewrite the case self-contained (500--900 字) |
| Using slide terminology when the textbook differs | Use the authoritative source's term + the other in parentheses (§0.2) |
| Assuming "textbook is authoritative" for every course | Record the source per course; many courses examine the PPT |
| Assuming an exam format when no intel exists | Ask the user for format + scope; state assumptions on page 1 |
| Using the humanities template for 思政 | Use the IDEOLOGICAL template: official wording + 踩点给分 (§2.1, course-types.md) |
| 思政 answers written in colloquial wording | Add a 表述对照表 (口语 → 规范) |
| Engineering paper without formula sheet / graph grid | Add them per course-types.md §2 |
| Humanities answer file with one "model answer" | Give 要点 + acceptable alternative views |
| Generating 4 PDFs for a 3-exam course | 2 base + 2 per exam = 8 files |
| Generic 20+10+10+5 format for every course | Extract real format in Step 0 first |

## Special Handling

**Bilingual courses (English exam + Chinese understanding):**
All output: Chinese explanations + English technical terms. Exam questions in English. Answers bilingual.

**User-provided priority list:**
When user gives topic list (e.g., "Topic A, Topic B, Topic C are most important"), restructure chapter weighting — priority topics get 2× the content depth, non-priority topics get minimal treatment (formula only).

**Massive courses (10+ chapters, 1000+ pages):**
Read syllabus/Ch0 first. Read Ch1-2 fully to understand course style. For remaining chapters, read first 15 pages + last 5 pages (summary/sample questions). Time-box reading to ~20% of agent generation time.

**Missing/inaccessible materials:**
- User-provided cheat sheets / topic lists → use as primary content outline
- Standard textbook knowledge → use for well-known courses with a standard textbook
- Flag uncertainty in output: "Based on standard course content; verify with your materials"

## Reference Files

- `references/latex-format-rules.md` — Full preamble, tcolorbox styles, color definitions, compilation
- `references/course-types.md` — Per-type playbook: 思政 / 工科 / 文科 / 商科 / 法学 / 医学 (question types, marking, answer space, fatal mistakes)
- `references/exam-blueprint.md` — Exam brief table, answer-space table, case/answer templates, delivery checklist
- `references/quality_check.py` — Automated pre-compilation checker
