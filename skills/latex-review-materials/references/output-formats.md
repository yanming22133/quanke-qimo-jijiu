# Output formats: PDF vs DOCX

Ask the user first: **PDF / DOCX / both**. Default: PDF.

## 1. PDF (preferred)

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

## 3. Mapping caveats

| LaTeX element | DOCX result |
|---|---|
| tcolorbox | blockquote (no colored frame) |
| multi-column table | may reflow; check and simplify if needed |
| `\vspace` answer space | disappears — add blank paragraphs in the `.md` instead |
| TikZ / figures | converted to images only if exported first |
| Math | converted to Word equations (OMML) |

**Answer space in DOCX**: use empty paragraphs (`&nbsp;` lines) rather than `\vspace`; keep the same visual height (e.g. 12 empty lines for an essay).

## 4. Verification

- Open the DOCX in Word/WPS; check page count, tables, and that Chinese renders (no boxes).
- Check that each big question still has writing space.
- If the DOCX looks broken, deliver the PDF and say why.

## 5. Never

- Never convert PDF → DOCX (layout is destroyed).
- Never claim DOCX is “identical” to the PDF; say “best effort”.
