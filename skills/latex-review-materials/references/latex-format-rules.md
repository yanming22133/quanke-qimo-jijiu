# LaTeX Formatting Rules for Chinese Review Materials

## 0. Reading Source Materials

### PDF — use `pdftotext` FIRST (NOT the Read tool)

The `Read` tool has a known bug where it falsely reports many PDFs as "password-protected". Always extract PDF text via:

```bash
pdftotext -layout "file.pdf" - 2>/dev/null | head -N
pdftotext -layout -f 1 -l 30 "file.pdf" -   # specific pages
```

Only use `Read` as fallback if pdftotext output is garbled. If both fail, try PyPDF2.

### DOCX extraction template

```python
import zipfile, xml.etree.ElementTree as ET, glob

def extract_docx(filepath):
    with zipfile.ZipFile(filepath) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    return '\n'.join(''.join(t.text or '' for t in p.iter(f'{{{ns}}}t'))
                     for p in tree.iter(f'{{{ns}}}p'))

for f in glob.glob('*.docx'):
    print(f'===== {f} =====\n{extract_docx(f)}\n')
```

### PPTX extraction template

```python
import zipfile, xml.etree.ElementTree as ET, glob

def extract_pptx(filepath):
    with zipfile.ZipFile(filepath) as z:
        slides = sorted(n for n in z.namelist()
                       if n.startswith('ppt/slides/slide') and n.endswith('.xml'))
        result = []
        for s in slides:
            result.append(f'--- {s.replace("ppt/slides/slide","").replace(".xml","")} ---')
            xml = z.read(s)
            for t in ET.fromstring(xml).iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
                if t.text: result.append(t.text)
        return '\n'.join(result)

for f in glob.glob('*.pptx'):
    print(f'===== {f} =====\n{extract_pptx(f)}\n')
```

## 1. Document Class (MANDATORY — non-negotiable)

```latex
\documentclass[12pt,a4paper,fontset=fandol]{ctexart}
```

- `fontset=fandol` is REQUIRED for Windows + TeX Live without fontconfig
- Fandol is the only fontset that works reliably without fontconfig on Windows
- Do NOT use `fontset=windows` or `fontset=ubuntu` — they require fontconfig at runtime
- The harmless `Fontconfig error: Cannot load default config file` warning is expected and ignorable

## 2. Required Packages (battle-tested combination)

```latex
\usepackage{amsmath,amssymb,amsthm}        % Math — load BEFORE hyperref
\usepackage[colorlinks=true,linkcolor=blue,CJKbookmarks=true]{hyperref}  % Links — load AFTER amsmath
\usepackage{geometry}                       % Page layout
\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}
\usepackage{fancyhdr}                       % Headers/footers
\usepackage{tcolorbox}                      % Colored boxes
\tcbuselibrary{skins,breakable}             % breakable = boxes can span pages
\usepackage{xcolor}                         % Colors (loaded by tcolorbox too, explicit is safe)
\usepackage{graphicx}                       % Images (if needed)
\usepackage{array,multirow,booktabs}        % Tables
\usepackage{enumitem}                       % Custom lists with [nosep], [leftmargin=*]
\usepackage[normalem]{ulem}                 % Underlining for fill-in-blank (\uline{})
\usepackage{titlesec}                       % Section formatting (optional)
```

## 3. Critical Preamble Fixes

### 3.1 Math Operators (MUST include — these are NOT built-in LaTeX commands)

```latex
% === Math Operators ===
\DeclareMathOperator{\cov}{Cov}              % Covariance operator
\newcommand{\plim}{\operatorname{plim}}       % Probability limit
% DO NOT define \E — it conflicts with amsmath or other packages
% Use \mathbb{E} directly or define as \newcommand{\Exp}{\mathbb{E}}
% DO NOT define \var — conflicts with amsmath
% Use \Var or \operatorname{Var} instead
```

### 3.2 Headheight Fix (eliminates fancyhdr warnings on every page)

```latex
% === Fix fancyhdr headheight warning ===
\setlength{\headheight}{14.5pt}
```

Without this, fancyhdr emits a warning on EVERY page output, making logs unreadable.

## 4. Color Definitions (ALL colors must be defined in preamble)

```latex
\definecolor{boxorange}{RGB}{255,165,0}
\definecolor{bgorange}{RGB}{255,245,230}
\definecolor{boxblue}{RGB}{0,102,204}
\definecolor{bgblue}{RGB}{230,242,255}
\definecolor{boxgreen}{RGB}{0,128,0}
\definecolor{bggreen}{RGB}{230,255,230}
\definecolor{boxred}{RGB}{204,0,0}
\definecolor{bgred}{RGB}{255,230,230}
\definecolor{boxpurple}{RGB}{128,0,128}
\definecolor{bgpurple}{RGB}{245,230,255}
\definecolor{boxgray}{RGB}{100,100,100}
\definecolor{bggray}{RGB}{245,245,245}
\definecolor{noteyellow}{RGB}{255,255,220}
\definecolor{notebg}{RGB}{255,255,220}
```

Use minimum 12 distinct colors. Undefined colors cause silent fallback to black.

## 5. tcolorbox Style Definitions

```latex
\newtcolorbox{keybox}[1][]{
  colback=bgorange, colframe=boxorange,
  fonttitle=\bfseries, title=#1,
  breakable, enhanced,
  before skip=8pt, after skip=8pt
}

\newtcolorbox{defbox}[1][]{
  colback=bgblue, colframe=boxblue,
  fonttitle=\bfseries, title=#1,
  breakable, enhanced,
  before skip=8pt, after skip=8pt
}

\newtcolorbox{warnbox}[1][]{
  colback=bgred, colframe=boxred,
  fonttitle=\bfseries, title=#1,
  breakable, enhanced,
  before skip=8pt, after skip=8pt
}

\newtcolorbox{formulabox}[1][]{
  colback=bggray, colframe=boxgray,
  fonttitle=\bfseries, title=#1,
  breakable, enhanced,
  before skip=8pt, after skip=8pt
}

\newtcolorbox{infobox}[1][]{
  colback=bgpurple, colframe=boxpurple,
  fonttitle=\bfseries, title=#1,
  breakable, enhanced,
  before skip=8pt, after skip=8pt
}

\newtcolorbox{notebox}[1][]{
  colback=noteyellow, colframe=boxorange,
  fonttitle=\bfseries, title=#1,
  breakable, enhanced,
  before skip=8pt, after skip=8pt
}
```

[注意] `breakable` is critical — without it, long boxes overflow pages.

## 6. Header/Footer (MUST use English only)

```latex
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{Course Review}
\fancyhead[R]{Ch.\thesection}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
```

**WRONG**: `\fancyhead[L]{课程复习}` — Chinese in headers causes font warnings  
**RIGHT**: `\fancyhead[L]{Course Review}` (adapt to actual course name in English)

## 7. Table Format (NO `\begin{table}[h]` floating environment)

**WRONG (will cause errors inside tcolorbox):**
```latex
\begin{tcolorbox}
\begin{table}[h]
\centering
\begin{tabular}{...}
...
\end{tabular}
\end{table}
\end{tcolorbox}
```

**RIGHT:**
```latex
\begin{tcolorbox}
\medskip
\begin{center}
\begin{tabular}{...}
\hline
...
\hline
\end{tabular}
\end{center}
\medskip
\end{tcolorbox}
```

Rule: tables in non-floating contexts (tcolorbox, exam answers) MUST use `center` + `tabular`. Reserve `\begin{table}[h]` only for standalone floating tables outside boxes.

## 8. tcolorbox Title Rules (CRITICAL — causes `Missing $ inserted` errors)

**The problem**: `[...]` in LaTeX has dual meaning — optional arguments AND math brackets. When you write:
```latex
\begin{formulabox}[$\sigma^2/[S_{11}(1-r^2)]$ 的推导]
```
The first `[` starts the optional argument; the `]` after `r^2)]` closes BOTH the math bracket AND the optional argument — but in the wrong order, breaking LaTeX's parser.

**Solutions (pick one):**
1. **Use English titles** (simplest, safest):
   ```latex
   \begin{formulabox}[Variance Formula Derivation]
   ```
2. **Escape brackets with braces**:
   ```latex
   \begin{formulabox}[$\sigma^2/{[S_{11}(1-r^2)]}$ derivation]
   ```
3. **Avoid math in titles entirely**:
   ```latex
   \begin{formulabox}[方差公式推导]
   ```

Prefer option 1 — English titles are always safe.

## 9. Text Labels (replace emoji — LaTeX cannot render emoji)

| Instead of | Use |
|------------|-----|
| 🔥 / ⭐ / ★ | `[核心]` or `[重点]` |
| ⚠️ / ❗ | `[注意]` |
| ✅ / ✔️ | `[对]` |
| ❌ / ✖️ | `[错]` |
| 📌 | `[考点]` |
| 💡 | `[提示]` |

```latex
\newcommand{\core}[1]{\textbf{\textcolor{boxred}{[核心] #1}}}
\newcommand{\key}[1]{\textbf{\textcolor{boxorange}{[重点] #1}}}
\newcommand{\nb}[1]{\textbf{\textcolor{boxblue}{[注意] #1}}}
\newcommand{\correct}{\textbf{\textcolor{boxgreen}{[对]}}}
\newcommand{\incorrect}{\textbf{\textcolor{boxred}{[错]}}}
\newcommand{\exam}[1]{\textbf{\textcolor{boxpurple}{[考点] #1}}}
\newcommand{\tip}[1]{\textcolor{boxgreen}{[提示] #1}}
```

## 10. Math & Formulas

- Multi-line formulas: `\begin{align}...\end{align}`
- Numbered formulas: `\begin{equation}...\end{equation}`
- Inline math: `$...$`
- Greek: `\beta`, `\sigma`, `\rho`, `\varepsilon`, `\alpha`, `\gamma`, `\theta`, `\delta`
- Subscripts/superscripts: `\hat{\beta}_1`, `\bar{x}`, `\sum_{t=1}^T`, `\boldsymbol{\beta}`
- Matrix notation: `\mathbf{X}`, `\boldsymbol{\beta}`, `\mathbf{I}`
- Distribution notation: `\sim N(0,\sigma^2)`, `\sim t(T-k)`, `\sim F(k-1,T-k)`, `\sim \chi^2(m)`
- Expected value: `E(\cdot)` or `\mathbb{E}(\cdot)`
- Variance: `\text{Var}(\cdot)` or `\operatorname{Var}(\cdot)`
- Probability limit: `\plim` (defined via `\newcommand{\plim}{\operatorname{plim}}`)

## 11. Section Structure Per Chapter (adapt to course type)

**For quantitative courses (math/formula heavy):**
```latex
\section{Chapter N: English Title / 中文标题}
\subsection{Background and Motivation}       % defbox
\subsection{Core Model Specification}        % formulabox
\subsection{Key Assumptions}                 % defbox
\subsection{Derivation / Estimation}         % formulabox
\subsection{Properties and Interpretation}   % keybox
\subsection{Application / Testing}           % keybox
\subsection{Common Mistakes}                 % warnbox
\newpage
```

**For qualitative courses (text/concept heavy):**
```latex
\section{Chapter N: English Title / 中文标题}
\subsection{Background and Context}          % defbox
\subsection{Core Concepts and Definitions}   % defbox
\subsection{Theoretical Framework}           % keybox
\subsection{Key Arguments and Analysis}      % keybox
\subsection{Relationships and Comparisons}   % infobox
\subsection{Significance and Implications}   % keybox
\subsection{Common Confusions and Pitfalls}  % warnbox
\newpage
```

Select the template that matches the course type detected from source materials.
Do NOT force quantitative subsections (e.g. "Model Specification") onto qualitative courses.

## 12. Space Between Questions (Mock Exam)

```latex
\vspace{0.5cm}   % Multiple choice
\vspace{1.0cm}   % Fill-in-blank
\vspace{3-4cm}   % Short calculation
\vspace{5-6cm}   % Proof / long calculation
\vspace{6-8cm}   % Comprehensive analysis
```

Add scratch pages at end of mock exam with:
```latex
\newpage
\section*{Scratch Area / 草稿区}
\mbox{}\newpage\mbox{}\newpage\mbox{}\newpage  % repeats for N blank pages
```

## 13. Compilation

```bash
# Compile twice for TOC + cross-references
xelatex -interaction=nonstopmode file.tex
xelatex -interaction=nonstopmode file.tex

# Clean auxiliary files
rm -f file.aux file.log file.out file.toc file.synctex.gz
```

Run compilations in parallel when there are multiple `.tex` files.

## 14. Post-Compilation Verification

```bash
# Check page count
pdfinfo file.pdf | grep Pages

# Check for undefined references
grep -c 'Undefined control sequence' file.log

# Check for missing citations
grep -c 'There were undefined' file.log

# Check for LaTeX errors
grep -c '^!' file.log
```

## 15. Full Battle-Tested Preamble

```latex
\documentclass[12pt,a4paper,fontset=fandol]{ctexart}

% === Packages ===
\usepackage{amsmath,amssymb,amsthm}
\usepackage[colorlinks=true,linkcolor=blue,CJKbookmarks=true]{hyperref}
\usepackage{geometry}
\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}
\usepackage{fancyhdr}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{array,multirow,booktabs}
\usepackage{enumitem}
\usepackage[normalem]{ulem}

% === Fix headheight warning ===
\setlength{\headheight}{14.5pt}

% === Math Operators (add course-specific ones as needed) ===
% Quantitative courses: \DeclareMathOperator{\cov}{Cov}, \newcommand{\plim}{\operatorname{plim}}
% DO NOT define \E or \var — they conflict with amsmath

% === Colors (12 required) ===
\definecolor{boxorange}{RGB}{255,165,0}
\definecolor{bgorange}{RGB}{255,245,230}
\definecolor{boxblue}{RGB}{0,102,204}
\definecolor{bgblue}{RGB}{230,242,255}
\definecolor{boxgreen}{RGB}{0,128,0}
\definecolor{bggreen}{RGB}{230,255,230}
\definecolor{boxred}{RGB}{204,0,0}
\definecolor{bgred}{RGB}{255,230,230}
\definecolor{boxpurple}{RGB}{128,0,128}
\definecolor{bgpurple}{RGB}{245,230,255}
\definecolor{boxgray}{RGB}{100,100,100}
\definecolor{bggray}{RGB}{245,245,245}
\definecolor{noteyellow}{RGB}{255,255,220}

% === tcolorbox styles ===
\newtcolorbox{keybox}[1][]{colback=bgorange,colframe=boxorange,fonttitle=\bfseries,title=#1,breakable,enhanced,before skip=8pt,after skip=8pt}
\newtcolorbox{defbox}[1][]{colback=bgblue,colframe=boxblue,fonttitle=\bfseries,title=#1,breakable,enhanced,before skip=8pt,after skip=8pt}
\newtcolorbox{warnbox}[1][]{colback=bgred,colframe=boxred,fonttitle=\bfseries,title=#1,breakable,enhanced,before skip=8pt,after skip=8pt}
\newtcolorbox{formulabox}[1][]{colback=bggray,colframe=boxgray,fonttitle=\bfseries,title=#1,breakable,enhanced,before skip=8pt,after skip=8pt}
\newtcolorbox{infobox}[1][]{colback=bgpurple,colframe=boxpurple,fonttitle=\bfseries,title=#1,breakable,enhanced,before skip=8pt,after skip=8pt}
\newtcolorbox{notebox}[1][]{colback=noteyellow,colframe=boxorange,fonttitle=\bfseries,title=#1,breakable,enhanced,before skip=8pt,after skip=8pt}

% === Text Labels (no emoji) ===
\newcommand{\core}[1]{\textbf{\textcolor{boxred}{[核心] #1}}}
\newcommand{\key}[1]{\textbf{\textcolor{boxorange}{[重点] #1}}}
\newcommand{\nb}[1]{\textbf{\textcolor{boxblue}{[注意] #1}}}
\newcommand{\correct}{\textbf{\textcolor{boxgreen}{[对]}}}
\newcommand{\incorrect}{\textbf{\textcolor{boxred}{[错]}}}
\newcommand{\exam}[1]{\textbf{\textcolor{boxpurple}{[考点] #1}}}
\newcommand{\tip}[1]{\textcolor{boxgreen}{[提示] #1}}

% === Headers (English only — adapt to course) ===
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{Course Review}
\fancyhead[R]{Ch.\thesection}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% === Metadata ===
\title{...}
\author{...}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage
% ... content ...
\end{document}
```
