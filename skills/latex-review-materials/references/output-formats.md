# Output formats: PDF vs DOCX vs HTML Review Site

Ask the user first: **PDF / DOCX / HTML 交互复习网站 / 组合（如 PDF 刷卷 + HTML 刷背）**. Default: PDF.

## 1. PDF (preferred for printing & timed mock exams)

```bash
xelatex -interaction=nonstopmode -halt-on-error file.tex
xelatex -interaction=nonstopmode -halt-on-error file.tex
```

- Best fidelity: tcolorbox, tables, spacing, answer space all preserved.
- Check: `pdfinfo file.pdf | grep Pages`, and open one page to confirm no overfull boxes.

## 2. DOCX (best effort)

DOCX is generated from a **Markdown mirror**, not from the PDF.

1. Write `file.md` with the same content: `#`/`##` headings, `-` lists, pipe tables, `$...$` math, `**bold**`.
2. Convert:

```bash
pandoc file.md -o file.docx --from markdown+tex_math_dollars --reference-doc=reference.docx
```

3. `reference.docx` controls Chinese fonts and heading styles. Create one once:

```bash
pandoc -o reference.docx --print-default-data-file reference.docx
# open it in Word, set 正文 = 宋体/Times New Roman, headings = 黑体, save
```

If `pandoc` is missing:

- Windows: `winget install --id JohnMacFarlane.Pandoc -e`
- macOS: `brew install pandoc`
- If it cannot be installed, fall back to PDF and tell the user.

### DOCX Mapping caveats

| LaTeX element | DOCX result |
|---|---|
| tcolorbox | blockquote (no colored frame) |
| multi-column table | may reflow; check and simplify if needed |
| `\vspace` answer space | disappears — add blank paragraphs in the `.md` instead |
| TikZ / figures | converted to images only if exported first |
| Math | converted to Word equations (OMML) |

**Answer space in DOCX**: use empty paragraphs (`&nbsp;` lines) rather than `\vspace`; keep the same visual height (e.g. 12 empty lines for an essay).

## 3. Interactive Offline HTML Review Website (`HTML 交互复习网站`)

Best for **screen/mobile study, rapid star-level review, active cloze recall (`🧠 默写模式`), and browsing original courseware**. Generated from clean Markdown chapter files (`unit/*.md`) via `references/build_unit.py` + `references/templates/study-site/`.

- **Core features**:
  - Parallel tabs per chapter (`#` H1 → tab; `##` H2 → star-rated card with `★★★★★`~`★★` filter bar)
  - Offline Mermaid flowcharts & knowledge maps (local `vendor/mermaid.min.js` with CDN fallback)
  - Per-question interactive answer toggles (`:::qa ... --- ... :::`) + expand/collapse all
  - **`🧠 默写模式`**: one-click blur on all bold keywords (`**...**`), click any single term to reveal/re-hide
  - Parallel `📄 原始课件` tab for lazy-loaded PDF preview & Word download
  - Non-sticky mobile-friendly layout + `localStorage` chapter completion progress bar
- **Full specification & build steps**: see `references/web-site-builder.md`.

## 4. Verification

- **PDF**: check page count and inspect rendered pages for overfull boxes or broken figures.
- **DOCX**: open in Word/WPS; check page count, tables, Chinese rendering, and big-question writing space. If broken, deliver PDF and explain why.
- **HTML Site**: open `index.html`; verify chapter switching, parallel tabs, star filtering, Mermaid SVG rendering, per-question Q&A toggles, `🧠 默写模式`, and `0` broken courseware links.

## 5. Never

- Never convert PDF → DOCX (layout is destroyed).
- Never claim DOCX is “identical” to the PDF; say “best effort”.
