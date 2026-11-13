# Layout presets (复习资料形态)

Ask the user which form they want. Default: **省墨讲义**（打印友好）。All presets use `fontset=fandol` so they compile on Windows without fontconfig.

| Preset | 适合 | 版式 | 纸张成本 |
|---|---|---|---|
| **省墨讲义** (default) | 打印、通读 | 单栏、5 号、1.5cm 边距、细线框、无填色 | 最低 |
| **彩框版** | 屏幕阅读、重点多 | 单栏、12pt、2.3cm 边距、彩色 tcolorbox | 高 |
| **双栏速查** | 考前速查、公式多 | 双栏、9pt、1.2cm 边距、紧凑列表 | 中 |
| **题目册 + 答案册** | 自测 | 两本独立文档，页眉区分，页码各自独立 | 中 |

## 1. 省墨讲义（default）

Template: `references/templates/ink-saving.tex`

```latex
\documentclass[a4paper,oneside,zihao=5,fontset=fandol]{ctexbook}
\usepackage[margin=1.5cm,headheight=1cm,footskip=0.8cm]{geometry}
\linespread{1.2}
\setlist{nosep}
\ctexset{chapter/break=\par}   % 章节连续排版，省纸
\titleformat{\section}{\normalfont\large\bfseries}{\thesection}{1em}{}[\titlerule]
\newtcolorbox{mybox}[1]{enhanced,breakable,colback=white,colframe=black!55,
  boxrule=0.3pt,leftrule=2pt,arc=0mm,fonttitle=\bfseries\small,title={#1},
  left=4pt,right=4pt,top=3pt,bottom=3pt}
```

特点：不填色、只用细线；5 号字；页边距 1.5cm；章节不强制换页。适合整本打印。

## 2. 彩框版

```latex
\documentclass[12pt,a4paper,fontset=fandol]{ctexart}
\usepackage[margin=2.3cm]{geometry}
\usepackage{tcolorbox}\tcbuselibrary{skins,breakable}
% 彩色 keybox / defbox / warnbox，见 latex-format-rules.md
```

特点：重点分层清楚，适合屏幕；黑白打印时颜色会变灰，成本高。

## 3. 双栏速查

```latex
\documentclass[9pt,a4paper,fontset=fandol]{ctexart}
\usepackage[margin=1.2cm]{geometry}
\usepackage{multicol}
\setlength{\columnsep}{6mm}
\setlength{\parindent}{0pt}
\setlist{nosep,leftmargin=1.2em}
\begin{document}
\begin{multicols}{2}
% 每个知识点用小标题 + 2--4 条要点；公式优先
\end{multicols}
\end{document}
```

特点：信息密度最高；必须控制每条长度，避免跨栏断裂。

## 4. 题目册 + 答案册

- 两个独立文档：`模拟卷A.tex` 与 `模拟卷A_答案.tex`。
- 页眉分别写 `Mock Exam A` / `Mock Exam A — Answers`。
- 答案册重新编号（`\pagenumbering{arabic}`），不要沿用题目册页码。
- 题目册只放题与留白；答案册只放解析与评分点。

## 5. 选择规则

- 只打印、预算有限 → 省墨讲义。
- 屏幕复习、重点需要颜色区分 → 彩框版。
- 考前 1–2 天、公式/定义多 → 双栏速查。
- 想反复自测 → 题目册 + 答案册。

**Do not mix presets inside one document.** Pick one per artifact; the summary can be 省墨讲义 while the mock exams use 彩框版.
