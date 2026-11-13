---
name: latex-review-materials
description: Use when generating Chinese LaTeX review materials from any course content (PDFs, PPTs, DOCX, lecture recordings). Extracts the real exam format, scope and emphasis first, then builds chapter summaries, exercises, and 3-5 mock papers with separate answer files, scoring rubrics, answer space for writing, and six big-question types (calculation, proof, diagram, programming, case, material analysis). Includes per-type playbooks for STEM, humanities, ideology/politics, management, law and medicine.
---

# LaTeX Chinese Review Materials Generator (Universal)

> One-click: any course materials → 6--12 PDFs (summary, exercises, 3--5 exams + answers).

## Output Files

Generate 2 + 2N files: 2 base files + one paper and one answer file per exam. Default N = 5 (12 files: A--C plus D 提高 and E 挑战); small courses (≤3 chapters) N = 2 (6 files); if the user is time-constrained or asks for fewer, N = 3 (8 files).

| File | Purpose |
|------|---------|
| `知识点汇总.tex` | Per-chapter detailed review notes |
| `章节练习.tex` | Exercises with answers inline in notebox |
| `模拟卷A.tex` / `_答案.tex` | Foundations — questions only / solutions with rubrics |
| `模拟卷B.tex` / `_答案.tex` | Core chapters |
| `模拟卷C.tex` / `_答案.tex` | Synthesis across chapters |
| `模拟卷D.tex` / `_答案.tex` | 提高卷 (default in the 5-set output) |
| `模拟卷E.tex` / `_答案.tex` | 挑战卷 (default in the 5-set output) |

**Review mode (Mode B) adds**: `复盘报告.pdf`, `补弱卷.pdf` + `补弱卷_答案.pdf`, and optionally `知识点补丁.pdf`. See Mode B below.

### Output format (ask first)

Ask: **PDF / DOCX / both** (default PDF).

- **PDF**: `xelatex` — best fidelity, preferred for printing.
- **DOCX**: write a Markdown mirror (`*.md`) and run `pandoc` — best effort; tcolorbox boxes become blockquotes, complex tables may shift.
- If `pandoc` is missing: `winget install --id JohnMacFarlane.Pandoc -e` (Windows) or `brew install pandoc` (macOS). If it cannot be installed, fall back to PDF and say so.
- Never convert DOCX→PDF; always generate from source.

### Optional artifacts

Ask whether to include (default: yes in the last week):

- `考前速查卡.pdf` — one A4 page: formulas, pitfalls, answer templates, top-10 errors.
- `复习计划.pdf` — 1/3/7-day schedule with spaced repetition.
- `错题本.pdf` — accumulated wrong questions from review mode.

**Chapter split for N exams** (maximizes coverage, no overlap):
- A: first third — foundations
- B: second third — core
- C: last third + cross-chapter synthesis
- D/E (optional): do NOT add new chapters. They re-test the same scope at higher difficulty (see §3.6).

For small courses (≤3 chapters): fall back to 2 exams (A: Ch1-2, B: Ch2-3 with overlap allowed).

Each exam uses the format extracted in Step 0. Fallback only if nothing is known: 20 MC (×1) + 10 multi (×2) + 10 T/F (×1) + 5 essay/calc (×10) = 100 pts, 120 min. Keep question topics NON-OVERLAPPING across the first three exams: a topic in Exam A should NOT appear in B or C. D/E may revisit topics but must change the angle and raise the cognitive level.

**Critical rules**:
- `模拟卷*.tex` = questions ONLY + scratch paper. NEVER put answers in exam files.
- `模拟卷*_答案.tex` = separate answer files with scoring rubrics.
- Use Chinese filenames as shown above. For English-only courses, use English filenames instead: `chapter_summary.tex`, `chapter_exercises.tex`, `mock_exam_A...E.tex`, `mock_exam_A...E_answers.tex`.

## Use when

- User asks to generate "复习资料", "考点总结", "模拟卷", "练习题"
- User uploads a finished paper / wrong questions / names a weak topic and wants targeted practice ("复盘", "错题", "补弱")
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
- Exclusions are exam content too: "Ch7 is NOT in scope" must appear on page 1.

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

### 0.3 Ask before generating (format + personalization)

Never start writing on assumptions. If the materials don't answer the questions below, ask the user — **in one batch, not one by one**.

**Must know (blocking):**
1. 题型与分值：选择/简答/计算/证明/画图/编程/案例各几道、多少分、多长时间。
2. 考试范围与排除章节。
3. 命题依据：教材 / PPT / 两者 / 往年题。

**Personalization (ask once, then apply):**
4. 还剩几天、每天能投入几小时（决定资料厚度与套数）。
5. 哪几章最弱（加权：多出题、多解释、多对比）。
6. 目标分数（及格线 / 中上 / 冲高分 → 决定深度与是否加挑战题）。
7. 想要几套卷（默认 5：A–C + D 提高 + E 挑战；时间紧可只要 3 套，或 2 套）。
8. 答案要多细（只给答案 / 给步骤 / 给评分点 + 易错点）。
9. 是否需要 OCR 扫描教材、是否需要双语。
10. 输出格式：PDF / DOCX / 两者（默认 PDF）。
11. 要不要附加：考前速查卡 / 复习计划 / 错题本（默认考前一周加）。

**Defaults if the user does not answer** (print them on page 1 so the user can correct):
- 默认 5 套（A–C + D 提高 + E 挑战）；时间紧才降到 3 套；答案给评分点 + 关键步骤；不 OCR；中文；PDF。
- 范围 = 所提供材料覆盖的章节；命题依据 = 材料中出现最多的那套，并标注“未确认”。

**How to ask**: paste one compact card (template in `references/exam-blueprint.md §1`), at most 6 questions at a time. If the user says "你看着办", state the defaults and proceed.

### 0.4 Source conflicts

When textbook / PPT / recording / past papers disagree, resolve in this order and record it:

1. 老师在录音或最后一节课的明确说法（最新优先）
2. 考试通知 / 教学大纲
3. Step 0 确定的命题依据
4. 其他材料

Make a conflict table: 知识点 | 说法 A（来源） | 说法 B（来源） | 采用 | 理由。Never silently pick one; if it affects a graded answer, tell the user.

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
  Formulas, derivations, "证明", Greek letters, numbers to compute   → QUANTITATIVE (math/physics/investment/finance)
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
| **Engineering** | 选择、填空、简答、计算、画图、设计、编程 | 计算 8--12 cm；画图半页（给坐标/网格）；代码 20--30 行 | 步骤分：公式→代入→结果→单位；代码看正确性/边界/复杂度 | 只写结果无过程；单位/量纲错；代码只过样例 |
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
0. User says a chapter is **weak** ("我第 4 章最虚") → weight it heaviest: more questions, more explanation, more comparisons.
1. User explicitly says "Chapter X is most important" or provides a priority topic list → weight heavily
2. Instructor's materials mark topics as "重点"/"考点" → weight accordingly
3. Past exam questions cluster on certain chapters → weight accordingly
4. Default: equal weight across all chapters

**Apply personalization after Step 0.3:**
- Time budget: ≤3 days → summary + 1–2 sets; ≥1 week → summary + exercises + 3–5 sets.
- Target score: pass → key points and basics; high score → add comparisons, edge cases, challenge questions.
- Answer detail: "points only" / "steps" / "rubric + common mistakes" (default: rubric + key steps).
- Weak chapters: add one extra worked example and one extra question per weak chapter.

### 3.7 Study plan (spaced repetition)

When the exam is within 14 days, generate `复习计划.pdf`:

| 时间 | 内容 |
|---|---|
| Day 1 | 红点知识点补丁 + 基础题 |
| Day 2 | 同知识点练习（变式） |
| Day 3 | 复习 + 错题重做 |
| Day 5 | 混合卷（限时） |
| Day 7 | 错题本 + 综合题 |
| 考前 1 天 | 速查卡 + 一套限时卷 |

Table columns: 日期 | 时段 | 内容 | 资料页码 | 完成（□）。If <3 days left, collapse to “补丁 + 1 套卷 + 错题本”。

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
| 计算 | 8--12 cm | `\vspace{10cm}` |
| 证明 / 推导 | 10--12 cm | `\vspace{11cm}` |
| 画图 / 设计 | half a page with grid or frame | `\vspace{12cm}` + grid |
| 编程 | 20--30 lines + complexity note | `\vspace{14cm}` |
| 论述 (25 pts) | 9--12 cm, or a full page | `\vspace{10cm}` |
| 案例分析 (30 pts, 3 小问) | 3--4 cm after EACH sub-question | `\vspace{3.2cm}` ×3 |

Rules:
- Put `\vspace{...}` immediately after the sub-question it belongs to, never after the section heading.
- If the paper would overflow, insert `\newpage` before the next big question instead of shrinking the space.
- End every paper with a scratch area: `\newpage\section*{草稿区}\mbox{}\newpage\mbox{}\newpage`.
- Verify: every big-question sub-question (论述/计算/编程/案例) has a following `\vspace` in the source (the quality checker enforces at least 3 per exam file).
- Exam files must stand alone: no "见教材第 X 页" / "见课件"; every condition, number and case fact is printed in the paper.

### 3.5.2 Big-question templates (six types — not only cases)

A paper's big questions must match the discipline. Pick from these six; a paper may mix two or three. **Do not default to essay/case for a quantitative or engineering course.**

#### A. Calculation (investment, finance, accounting, engineering, physics)

- Structure: 已知 → 求 → 公式 → 代入 → 结果 → 单位/结论.
- Space: 8--12 cm per sub-question; multi-period problems may need a full page.
- Rubric: formula 30%, substitution 30%, result 30%, unit/significance 10%.
- Must give: discounting convention, tax rate, units, rounding rule, and whether a formula sheet is allowed.
- Typical mistakes: skipping steps, mixing nominal/real rates, unit mismatch, wrong sign.

#### B. Proof / derivation (math, theory, algorithms)

- Structure: 已知 / 求证 → 证明（关键步骤）→ 结论.
- Space: 10--12 cm.
- Rubric: approach 40%, key steps 40%, conclusion 20%.

#### C. Diagram / design (electronics, mechanical, civil, networks)

- Structure: 给定条件 → 画图/设计 → 标注 → 说明.
- Space: half a page with grid or a blank frame (never a 3 cm strip).
- Rubric: topology 40%, parameters/labels 30%, standard compliance 30%.
- Provide the axes, units and required symbols; state whether drafts are allowed.

#### D. Programming (CS, data science, AI)

- Structure: 题目描述 + 输入/输出示例 + 数据范围与约束 + 要求（语言、复杂度、是否允许伪代码）.
- Space: 20--30 lines on paper, or a code box; leave room for complexity analysis.
- Rubric: correctness 50% (including edge cases), complexity 20%, structure/style 20%, clarity 10%.
- Include at least one edge case in the sample; say explicitly if only pseudocode is accepted.
- Typical mistakes: happy path only, ignoring constraints, no complexity statement.

#### E. Case analysis (management, law, medicine)

- Structure: case box (breakable `infobox`, 500--900 字, self-contained) → "请回答：" → 3 sub-questions with explicit points.
- Each sub-question maps to a course framework (five forces / value chain / strategy / entry mode / 涵摄 / 鉴别诊断), not general knowledge.
- Rubric: framework 40%, case facts 30%, conclusion/recommendation 30%.
- If the folder has N cases and you need 2N questions, reuse cases with DIFFERENT angles and document the mapping.
- Never split a case box from its questions (see 3.5.3).

#### F. Material analysis / essay (humanities, ideology/politics)

- Structure: 材料/引文 → 设问（是什么/为什么/怎么做）→ 论述.
- Space: 12--15 cm (material analysis) or a full page (essay).
- Rubric: 观点 30%, 依据/原文 40%, 结构 20%, 表达 10%; 思政按踩点给分.
- For 思政: every key point must use the official formulation; add a 表述对照表 (口语 → 规范).

### 3.5.3 Page layout for exams

- `\newpage` before the big-question sections (论述/计算/编程/案例/材料) so each block starts on a fresh page.
- Case box + "请回答" + first sub-question should fit on one page.
- Per-paper header: `\fancyhead[R]{Mock Exam A}` (English only).
- Paper title block: course, "期末模拟试卷 X", time, full marks, closed-book, and the chapter coverage line.

### 3.5.4 Delivery numbering

Number the PDFs in reading order: `01_知识点汇总`, `02_章节练习`, `03_模拟卷A`, `04_模拟卷A_答案`, `05_模拟卷B` … Keep the `.tex` sources in a `_tex源文件/` subfolder and the OCR text in `NN_课本OCR_考点章节/`. Put the exam brief in `00_说明.md`.

### 3.6 Difficulty ladder (D/E papers, default)

Difficulty must come from **deeper thinking on complete information**, never from withholding data or making the stem ambiguous. A student must always be able to solve the question from what is printed.

**Three levels — defined by cognitive demand, not by missing facts:**

| Level | What changes | Example |
|---|---|---|
| 基础题 | one concept, one step, direct recall/application | 写出波特的三种基本战略 |
| 难题 | several concepts linked, multi-step, cross-chapter, requires judgment | 用五力 + 价值链判断某企业该不该进入某行业 |
| 易错题 | information complete, but contains a common misconception or a boundary condition | 给出两项业务收入占比，判断是相关约束型还是主导业务型（阈值易混） |

**Ladder design (information stays complete and solvable):**

| Axis | A/B/C | D 提高 | E 挑战 |
|---|---|---|---|
| Knowledge span | single point | 2--3 linked concepts | cross-chapter integration |
| Reasoning steps | 1--2 | 3--4 | multi-step with a stated decision rule |
| Task verb | describe / explain | compare / analyze | evaluate / decide / predict |
| Distractors | none | similar concepts in options or data (still solvable) | two defensible frameworks, student must justify the choice |
| Common-error density | none | 1 classic pitfall | 2--3 boundary conditions |

Per-section design:

| Section | A/B/C | D 提高 | E 挑战 |
|---|---|---|---|
| 单选 | recall | discriminate confusable concepts | scenario judgment with two plausible options |
| 简答 | restate | compare + conditions | open synthesis, no single textbook answer |
| 论述 | one framework | two frameworks + evidence | thesis + counter-thesis + rebuttal + boundary |
| 案例 | complete data, 3 sub-questions | complete data + one distractor figure | complete data + a decision under constraints + risks |
| 计算 | single-step substitution | multi-step / multi-period (all given) | requires choosing a model + discussing assumptions |
| 编程 | direct implementation | added constraints / optimization | edge cases + complexity analysis + proof |

Type-specific ladder notes:
- **Calculation**: the harder version changes the *setup* (multi-period, taxes, inflation, embedded options), not the amount of given data. All rates and conventions must be stated.
- **Programming**: the harder version adds constraints (time/memory), adversarial inputs, or a required complexity bound. Sample I/O and edge cases are always provided.
- **Proof**: D adds an intermediate lemma; E requires constructing the argument from the full set of givens.

Marking shifts:
- D/E add points for **argument quality** and **trade-off justification**, not for more content.
- Still provide a reference answer, but label it "参考思路，不唯一".

**Hard rules:**
- 题干必须自足：条件、数据、约束齐全；不得删条件、不得制造矛盾、不得用模糊设问。
- 难度靠：概念联动、推理链长度、跨章整合、评价与决策、易错点（阈值、边界、易混概念）。
- D/E 仍不得超出考试范围；易错 ≠ 超纲 ≠ 缺条件。

## Step 4: Dispatch Agents (up to 12 Parallel)

Always generate ALL files simultaneously as background agents:
1. `知识点汇总.tex` (or `chapter_summary.tex` for English courses)
2. `章节练习.tex` (or `chapter_exercises.tex`)
3. `模拟卷A.tex` — Exam A (1st chunk of chapters)
4. `模拟卷A_答案.tex` — Exam A solutions
5. `模拟卷B.tex` — Exam B (2nd chunk)
6. `模拟卷B_答案.tex` — Exam B solutions
7. `模拟卷C.tex` — Exam C (3rd chunk + cross-chapter synthesis)
8. `模拟卷C_答案.tex` — Exam C solutions
9. `模拟卷D.tex` — 提高卷 (same scope, higher difficulty per §3.6)
10. `模拟卷D_答案.tex`
11. `模拟卷E.tex` — 挑战卷 (highest difficulty per §3.6)
12. `模拟卷E_答案.tex`

D/E are part of the default 5-set output; drop them (N = 3) when the user is time-constrained or asks for fewer. For ≤3 chapters: use 2 exams (6 files: summary + exercises + 2 papers + 2 answers). Each exam covers DIFFERENT chapter groups to maximize topic coverage with zero overlap.

If the host agent has no parallel sub-agents, generate the files sequentially in the same order — the parallel step is an optimization, not a requirement.

**Batching and resume (for 5 sets):** generate in 3 batches — (summary + exercises + A + B), (C + D), (E + 速查卡 + 计划). Keep a `progress.md` with `[x]`/`[ ]` per file; on restart, skip files that exist and are non-empty, and never silently overwrite a good file.

```
## AGENT PROMPT TEMPLATE

Write LaTeX file at [ABSOLUTE PATH].

Course: [NAME], [INSTITUTION], [INSTRUCTOR]
Textbook: [TITLE, EDITION]
Exam language: [EN/CN/BILINGUAL]

### Preamble:
Use `references/latex-format-rules.md §15` verbatim, either inline or as `\input{preamble.tex}` (keep it in the same folder).

### CHAPTER-BY-CHAPTER CONTENT:

Ch N: [TITLE] — MUST cover:
- Topic 1: [specific concept/formula/event]
- Topic 2: [specific concept/formula/event]
- ... (5-8 specific topics per chapter)
- [EXAM] questions on: [specific calculation/essay types]
- Key terms to include: [list 5-10 English+Chinese terms]

[... repeat for all chapters ...]

### Mandatory Rules:
1-14 [paste the 14 rules from the "Mandatory Rules" section]

### Post-write checklist (run yourself):
- [ ] `grep -c '\\begin{enumerate}' file.tex` == `grep -c '\\end{enumerate}' file.tex` ?
- [ ] `ulem` present in the file or in the `\input` preamble?
- [ ] `grep -P '[\\x{1F300}-\\x{1F9FF}]' file.tex` returns empty?
- [ ] All tcolorbox titles are English or short Chinese, with no `[` and no ASCII comma inside?
- [ ] (exam files) every big-question sub-question (论述/计算/编程/案例) followed by `\vspace`?
- [ ] Big questions match the discipline (calculation / proof / diagram / programming / case / material)?
- [ ] No 参考答案/评分标准 in exam files?
- [ ] Format matches Step 0 (not the 20+10+10+5 fallback)?

Target: [N] lines. Write file now.
```

**The per-chapter content list is the most important part.** Don't write "summarize Ch1" — enumerate every specific concept, formula, event, and term that must appear. The quality of this list determines the quality of the output.

## Step 5: Quality Check (BEFORE compiling)

```bash
python references/quality_check.py *.tex
```

If any check FAILS → fix with Edit, re-run check, THEN compile. The checker validates: enumerate balance, required packages (skipped when a `\input` preamble is used), nested `[` and ASCII commas in tcolorbox titles, table floats inside tcolorbox, Chinese in headers, emoji, answer space in exam files, and answers leaked into exam files.

## Step 5.5: Verify answers (before delivery)

Never claim an answer is correct without checking it.

- **Calculation**: recompute with Python/sympy; record `已验算 YYYY-MM-DD` in the answer file.
- **Programming**: run the sample and at least one edge case; record `已跑样例`.
- **Proof / essay**: check the logic chain and citations; mark `待人工复核` if you cannot verify.
- If verification is impossible (no runtime, no data), say so explicitly in the answer file.

## Step 5.6: Exam lint (dedupe + difficulty)

Run:

```bash
python references/exam_lint.py 模拟卷*.tex
```

It checks:
- duplicate stems across papers (similarity > 0.85)
- item count per paper
- difficulty tags `% D:easy|medium|hard` and their distribution (target 40/40/20, ±10)

Tag convention: put `% D:easy` (or `medium` / `hard`) on the line before each `\item` in exam files.

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
4. If a background agent is still writing, stop it first, then fix

---

## Mode B: Review & Remediate (复盘补弱)

Use when the student uploads a finished paper, lists wrong questions, or names a weak topic. Goal: **diagnose → map to knowledge points → generate a personalized remedial set**.

### B1. Intake (ask first)

1. **Upload**: 答卷照片 / PDF / 手写答案文本；有标准答案就一起给。
2. **Scope**: 只复盘这一套，还是指定章节 / 整套资料？
3. **Target**: 下次考试时间；想要多少题（默认每个错点 2 道变式 + 1 道综合）。
4. **Privacy**: 提醒先裁掉姓名、学号、班级再上传。

### B2. Diagnose each wrong question

For every wrong or blank question, record:

| 字段 | 说明 |
|---|---|
| 题号 / 考点 | 对应知识点汇总里的标签 |
| 你的答案 / 正确答案 | 没有标答就写“待确认” |
| 错因 | 见下表七类 |
| 置信度 | 确定 / 待确认（无标答时） |

| 错因 | 典型表现 | 补法 |
|---|---|---|
| 概念不清 | 定义、条件、适用范围混淆 | 知识点补丁 + 基础题 |
| 方法不会 | 知道考什么，但不知道从哪下手 | 例题拆步骤 + 同型题 |
| 计算失误 | 思路对，结果/单位错 | 限时计算训练 + 检查清单 |
| 审题偏差 | 答非所问、漏看条件 | 关键词训练 + 换问法变式 |
| 步骤缺失 | 结果对但丢步骤分 | 对照评分标准补步骤 |
| 时间不够 | 会做但没写完 | 分层限时卷，不加量 |
| 完全空白 | 没学过或放弃 | 从零讲解 + 最小练习 |

**No standard answer**: ask for it, or judge from the textbook and mark "待确认"。Never invent a score.

### B3. Map to knowledge points

Use the same tags as `知识点汇总`. Build a table: 知识点 → 错题数 → 掌握度（红 / 黄 / 绿）。自述薄弱点优先于统计推测。

### B4. Generate the remedial set

Structure:

- **Part A 知识点补丁**：每个红点 1 页（定义 / 公式 / 易错点 / 1 道例题）。
- **Part B 变式题**：每个红点 2 道（基础 + 变式，换数字 / 情境 / 问法，**不重复原题**）。
- **Part C 综合题**：1–2 道跨知识点。
- **答案**：步骤 + 该步对应的错因提醒。

Rules:
- 不抄原题；变式必须换情境或问法。
- 难度递进：基础 → 变式 → 综合。
- “时间不够”只做限时训练，不加题量。
- 复盘卷也要留答题空间（§3.5.1）。

### B5. 错题本 (cross-session)

Maintain `错题本.md` in the course folder:

| 日期 | 来源卷 | 题号 | 知识点 | 错因 | 次数 | 最近一次 |
|---|---|---|---|---|---|---|

- Append every review; merge rows with the same 知识点 + 错因 (increment 次数).
- Recurrent rows (次数 ≥2) become red points for the next review.
- Regenerate `错题本.pdf` on request; the 速查卡 pulls the top 10 by 次数.

### B6. Outputs

- `复盘报告.pdf`：错题表 + 错因分布 + 知识点掌握度 + 下一步建议
- `补弱卷.pdf` + `补弱卷_答案.pdf`
- `错题本.pdf`（累积）
- 可选：`知识点补丁.pdf`、`考前速查卡.pdf`

## 14 Mandatory Rules (in EVERY agent prompt)

```
1. \documentclass[12pt,a4paper,fontset=fandol]{ctexart}
2. ZERO emoji — use [CORE][KEY][NOTE][EXAM][TIP] labels
3. Tables: \medskip\begin{center}\begin{tabular}... — NEVER \begin{table}[h] inside tcolorbox
4. Headers: ENGLISH ONLY in fancyhdr
5. Colors: ALL \definecolor{}{RGB}{...} in preamble
6. Compile: xelatex twice; clean aux
7. tcolorbox titles: English or SHORT Chinese. NEVER put `[` or an ASCII comma inside the optional title
8. \uline{} → MUST have \usepackage[normalem]{ulem} in preamble
9. \begin{enumerate} count MUST equal \end{enumerate} count — COUNT THEM after writing
10. Exam files: leave \vspace after every big question (论述 9--12 cm; 计算 8--12 cm; 编程 20--30 行; 案例每小问 3--4 cm); never put 参考答案 inside exam files
11. Big questions must match the discipline: calculation / proof / diagram / programming / case / material analysis — never all essays
12. Verify calculation and programming answers before delivery (sympy / sample run); mark 已验算 or 待人工复核 in the answer file
13. Ask PDF vs DOCX before generating; DOCX is best-effort from a Markdown mirror (never convert PDF→DOCX)
14. For 5 sets, generate in batches (A–B, C–D, E + artifacts) and keep progress.md for resume
```

## Common Errors (quick reference)

| Error | Fix |
|-------|-----|
| `\uline` undefined | Add `\usepackage[normalem]{ulem}` |
| enumerate mismatch → blank PDF | Remove stray `\end{enumerate}` |
| `Missing $ inserted` from tcolorbox title | Use English title, no `[` inside `[...]` |
| `Package pgfkeys Error: I do not know the key` in a box title | Remove the ASCII comma from the title or wrap the title in braces |
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
| Making D/E harder by obscure or out-of-scope wording | Raise integration/judgment per §3.6 |
| D/E adding new chapters | D/E re-test the same scope at a higher cognitive level |
| Case box split across pages from its questions | `\newpage` before 论述/案例分析 (Step 3.5.3) |
| Exam requires the textbook / original case PDF | Rewrite the case self-contained (500--900 字) |
| Exam says "见教材第 X 页" | Print all conditions and data in the paper |
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
- `references/course-types.md` — Per-type playbook: 思政 / 工科 / 文科 / 商科 / 投资学·金融 / 计算机 / 法学 / 医学 (question types, marking, answer space, fatal mistakes)
- `references/exam-blueprint.md` — Exam brief table, answer-space table, case/answer templates, delivery checklist
- `references/review-mode.md` — 复盘补弱：intake card, diagnosis table, report outline, remedial paper skeleton
- `references/study-plan.md` — 复习计划 / 间隔重复模板
- `references/output-formats.md` — PDF vs DOCX pipeline (pandoc, reference.docx, caveats)
- `references/exam_lint.py` — 跨卷去重 / 题量 / 难度分布检查
- `references/quality_check.py` — Automated pre-compilation checker
