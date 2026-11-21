#!/usr/bin/env python3
"""
Course Review Site Markdown-to-HTML Compiler
===========================================
将 unit/*.md 自动编译为带平行分栏、星级考点卡片、彩色序号/列表、加粗高亮、斜体强调、
表格、离线 Mermaid 图表、单题独立答案切换、默写模式与原始课件预览的 unit/*.html。

用法：
  python build_unit.py path/to/unit/1.md          # 编译单个 md 文件 -> 1.html
  python build_unit.py path/to/unit/              # 批量编译目录下全部 *.md -> *.html

Markdown 约定：
  - 顶部 YAML Frontmatter：id, title, kicker, stars, tags, materials
  - 一级标题 `# 栏目名`        -> 平行分栏（Tab）
  - 二级标题 `## 标题 ★★★★★`   -> 卡片大标题（自动识别星级并支持顶部星级筛选）
  - 三级标题 `### 小节`        -> 金色左竖条暖底小节标题
  - 四级标题 `#### 细分`       -> 深青下划线小标题
  - `**加粗**`                -> 荧光底纹高亮（默写模式下自动打模糊滤镜、单点显示）
  - `*斜体*`                  -> 暖金衬线斜体强调
  - `1.` / `-`                -> 彩色圆形序号 / 箭头与嵌套圆点列表
  - `| 表格 |`                -> 响应式斑马纹表格
  - ```mermaid ... ```        -> 离线本地 Mermaid 图表
  - `> 引用`                  -> 自动语义识别的彩色提示框（考情/术语/避坑/提示）
  - `:::qa [题型]` ... `---` ... `:::` -> 单题独立切换答案卡片
"""

import glob
import html
import os
import re
import sys
from urllib.parse import quote


THEMES = {
    "editorial": {
        "label": "现代财经智库风（默认 · 单栏渐变卡片）",
        "css": "",
    },
    "academic-book": {
        "label": "学术专著讲义风（双线扉页 + 三线表 + 书签栏 + 双栏网格）",
        "css": """
/* === 学术专著讲义风：扉页排版 + 三线表 + 书签分栏 + 双栏网格 === */
:root {
  --theme: #1a3c63; --theme-dark: #0f2540; --theme-mid: #28568a;
  --theme-light: #edf3f9; --theme-soft: #f5f8fc;
  --gold: #8c6500; --gold-bright: #b08200; --gold-light: #fdf9ec; --gold-border: #d9be6c;
  --red: #a8231a; --red-light: #fbf0ef; --red-border: #dfa39e;
  --green: #1d5b3b; --green-light: #eef7f2; --green-border: #8dc5a8;
  --paper: #fbf9f4; --surface: #fffefb; --surface-alt: #f6f2ea;
  --ink: #1d1a16; --ink-muted: #524b42; --border: #d8cfc0; --border-strong: #bfb29d;
}
body {
  font-family: "Noto Serif SC", "Songti SC", "STSong", Georgia, serif;
  background: var(--paper);
  line-height: 1.85;
}
/* 摒弃大色块横幅：改为学术专著双横线居中扉页头 */
.chapter-hero {
  background: var(--surface);
  color: var(--ink);
  padding: 36px 28px 26px;
  border-top: 5px solid var(--theme-dark);
  border-bottom: 3px double var(--border-strong);
  text-align: center;
}
.hero-top-row { justify-content: center; gap: 14px; margin-bottom: 14px; }
.chapter-kicker {
  background: transparent;
  color: var(--theme);
  border: 1px solid var(--theme);
  border-radius: 2px;
  letter-spacing: 0.18em;
  padding: 2px 12px;
}
.hero-star-pill, .hero-star-pill.s5 {
  background: transparent;
  color: var(--red);
  border: 1.5px solid var(--red);
  border-radius: 2px;
  font-weight: 700;
}
.chapter-hero h1 { font-size: 2rem; letter-spacing: 0.06em; color: var(--theme-dark); }
.hero-tags { justify-content: center; }
.hero-tag {
  background: var(--surface-alt);
  color: var(--ink-muted);
  border: 1px solid var(--border);
  border-radius: 2px;
}
/* 书签下划线式分栏 */
.nav-bar-wrap { background: var(--paper); border-bottom: 1px solid var(--border-strong); box-shadow: none; }
.nav-tabs { gap: 0; border-bottom: none; }
.nav-tab {
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  border-radius: 0;
  padding: 10px 16px;
  font-family: var(--font-sans);
  color: var(--ink-muted);
}
.nav-tab:hover { color: var(--theme-dark); background: rgba(26,60,99,0.04); }
.nav-tab.active {
  background: transparent;
  color: var(--theme-dark);
  border-bottom-color: var(--red);
  font-weight: 700;
}
/* 宽版讲义容器 + 卡片直角印章感 */
.page-wrap { max-width: 1080px; }
.card {
  border-radius: 3px;
  border: 1px solid var(--border);
  box-shadow: none;
  padding: 24px 28px;
}
.card.kp-card { border-left: 3px solid var(--theme); }
.card.kp-card[data-stars="5"] { border-left: 4px solid var(--red); background: var(--surface); }
.card-header { border-bottom: 2px solid var(--theme-dark); padding-bottom: 8px; }
.star-badge { border-radius: 2px; font-family: var(--font-sans); }
/* 学术规范三线表（顶粗线、表头细线、底粗线，去竖线与灰底） */
.table-wrap { border: none; border-radius: 0; }
table { border-top: 2px solid var(--ink); border-bottom: 2px solid var(--ink); background: transparent; }
th { background: transparent; color: var(--theme-dark); border-bottom: 1px solid var(--ink); font-family: var(--font-sans); }
td { border-bottom: 1px dotted var(--border); background: transparent !important; }
/* 宽屏列表双栏讲义排版 */
@media (min-width: 860px) {
  .card > ul { columns: 2; column-gap: 32px; }
  .card > ul > li { break-inside: avoid; }
}
.card ol > li::before { border-radius: 3px; font-family: Georgia, serif; }
.card h4 { background: transparent; border-left: 3px solid var(--theme); border-bottom: 1px dashed var(--border); border-radius: 0; padding: 3px 10px; }
.callout { border-radius: 2px; border-width: 0 0 0 4px; }
""",
    },
    "bento-tech": {
        "label": "极简 Bento 科技看板风（左侧导航 + 便当盒多列网格 + 分段控制器）",
        "css": """
/* === 极简 Bento 科技看板风：现代双列网格 + 胶囊分段器 + 代码方块编号 === */
:root {
  --theme: #2563eb; --theme-dark: #0f172a; --theme-mid: #3b82f6;
  --theme-light: #eff6ff; --theme-soft: #f8fafc;
  --gold: #0284c7; --gold-bright: #0ea5e9; --gold-light: #e0f2fe; --gold-border: #7dd3fc;
  --red: #e11d48; --red-light: #fff1f2; --red-border: #fda4af;
  --green: #059669; --green-light: #ecfdf5; --green-border: #6ee7b7;
  --paper: #eef2f6; --surface: #ffffff; --surface-alt: #f8fafc;
  --ink: #0f172a; --ink-muted: #475569; --border: #e2e8f0; --border-strong: #cbd5e1;
  --font-serif: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
body { background: radial-gradient(circle at 12% 0%, #e0e7ff 0%, #eef2f6 38%); }
/* 卡片式悬浮顶栏而非满宽横幅 */
.chapter-hero {
  max-width: 1120px;
  margin: 20px auto 0;
  border-radius: 20px;
  background: linear-gradient(120deg, #0f172a 0%, #1e293b 58%, #1d4ed8 100%);
  border: 1px solid rgba(148,163,184,0.22);
  border-bottom: none;
  padding: 26px 32px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.14);
}
.chapter-kicker { color: #7dd3fc; border-color: rgba(125,211,252,0.35); background: rgba(56,189,248,0.12); }
/* Apple/Linear 风格胶囊分段控制器（Segmented Control） */
.nav-bar-wrap { background: transparent; border: none; box-shadow: none; margin-top: 14px; }
.nav-bar-inner {
  max-width: 1120px;
  background: rgba(255,255,255,0.88);
  border: 1px solid #dbe2ec;
  border-radius: 16px;
  padding: 8px 14px;
  box-shadow: 0 4px 14px rgba(15,23,42,0.04);
}
.nav-tabs { background: #f1f5f9; padding: 4px; border-radius: 11px; gap: 4px; }
.nav-tab { border: none; background: transparent; border-radius: 8px; padding: 7px 14px; color: #475569; }
.nav-tab.active { background: #ffffff; color: #0f172a; box-shadow: 0 1px 4px rgba(15,23,42,0.12); }
/* Bento 便当盒网格：宽屏自动双列拼排，含图/表/QA的卡片横跨整行 */
.page-wrap { max-width: 1120px; margin-top: 18px; }
.section.active {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
}
.section.active > .quiz-toolbar,
.section.active > .qa-section-title,
.section.active > .qa-item,
.section.active > .pdf-block,
.section.active > .dl-only,
.section.active > .empty-filter-msg,
.section.active > .card:first-child,
.section.active > .card:has(.mermaid-wrap),
.section.active > .card:has(table) {
  grid-column: 1 / -1;
}
@media (max-width: 820px) {
  .chapter-hero { margin: 12px 12px 0; border-radius: 16px; }
  .nav-bar-inner { margin: 0 12px; }
  .section.active { grid-template-columns: 1fr; }
}
.card {
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 10px rgba(15,23,42,0.04);
  padding: 22px 24px;
}
.card.kp-card, .card.kp-card[data-stars="5"], .card.kp-card[data-stars="4"] {
  border-left: 1px solid #e2e8f0;
  border-top: 4px solid var(--theme);
}
.card.kp-card[data-stars="5"] { border-top-color: #e11d48; background: #ffffff; }
.card.kp-card[data-stars="4"] { border-top-color: #0ea5e9; }
/* 代码块风格方块编号与科技感标签 */
.card ol > li::before {
  border-radius: 6px;
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 0.72rem;
  background: #0f172a;
}
.card.kp-card[data-stars="5"] ol > li::before { background: #e11d48; }
.card h4 { border-left: none; background: #f1f5f9; border-radius: 8px; padding: 6px 12px; color: #0f172a; }
.card p strong, .card li strong, .card td strong {
  color: #1d4ed8;
  background: #dbeafe;
  padding: 1px 5px;
  border-radius: 5px;
}
.card.kp-card[data-stars="5"] p strong, .card.kp-card[data-stars="5"] li strong {
  color: #be123c;
  background: #ffe4e6;
}
""",
    },
    "notion-minimal": {
        "label": "极简 Notion 笔记流风（无外框纯白文档 + 荧光手账划重点）",
        "css": """
/* === 极简 Notion 笔记文档流风：无卡片边框 + 780px 黄金列宽 + 荧光手账笔 === */
:root {
  --theme: #2f3437; --theme-dark: #191919; --theme-mid: #55595c;
  --theme-light: #f1f1ef; --theme-soft: #f7f7f5;
  --gold: #9a6700; --gold-bright: #d97706; --gold-light: #fbf3db; --gold-border: #ead79c;
  --red: #d44c47; --red-light: #fdebec; --red-border: #f3c2c0;
  --green: #2b7a4b; --green-light: #edf7f1; --green-border: #b6dec5;
  --paper: #ffffff; --surface: #ffffff; --surface-alt: #f7f6f3;
  --ink: #37352f; --ink-muted: #6b6a65; --border: #e9e9e7; --border-strong: #d3d3cf;
  --font-serif: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
}
body { background: #ffffff; color: #37352f; font-size: 15.5px; line-height: 1.78; }
/* 极简文档页眉（无深色大横幅，模拟 Notion Page Header） */
.chapter-hero {
  background: #ffffff;
  color: #37352f;
  border-bottom: 1px solid #e9e9e7;
  padding: 36px 24px 18px;
}
.chapter-hero-inner { max-width: 780px; }
.chapter-hero h1 { font-size: 2.1rem; font-weight: 800; color: #191919; letter-spacing: -0.02em; }
.chapter-kicker { background: #f1f1ef; color: #6b6a65; border: none; border-radius: 5px; }
.hero-star-pill, .hero-star-pill.s5 { background: #fdebec; color: #d44c47; border-radius: 5px; }
.hero-tag { background: #f7f6f3; color: #55544f; border: 1px solid #e9e9e7; }
/* 极简文字底线导航 */
.nav-bar-wrap { background: #ffffff; border-bottom: 1px solid #e9e9e7; box-shadow: none; }
.nav-bar-inner { max-width: 780px; padding: 6px 24px; }
.nav-tab { border: none; background: transparent; border-radius: 6px; padding: 6px 10px; color: #787774; font-weight: 500; }
.nav-tab:hover { background: #f1f1ef; color: #37352f; }
.nav-tab.active { background: #efefec; color: #191919; font-weight: 700; }
/* 彻底去除外框卡片，改为流畅的笔记文档流 */
.page-wrap, .chapter-footer { max-width: 780px; }
.card, .card.kp-card, .card.kp-card[data-stars="5"], .card.kp-card[data-stars="4"], .card.kp-card[data-stars="3"] {
  border: none;
  border-left: none;
  border-bottom: 1px solid #efefec;
  border-radius: 0;
  box-shadow: none;
  background: transparent;
  padding: 18px 0 24px;
}
.card-header { border-bottom: none; padding-bottom: 4px; margin-bottom: 10px; }
.card-header h2, .card-header h3 { font-size: 1.32rem; font-weight: 700; color: #191919; }
/* 手账荧光笔重点高亮 */
.card p strong, .card li strong, .card td strong {
  color: #191919;
  background: linear-gradient(180deg, transparent 45%, #fef08a 45%);
  padding: 0 3px;
  border-radius: 2px;
}
.card.kp-card[data-stars="5"] p strong, .card.kp-card[data-stars="5"] li strong {
  color: #991b1b;
  background: linear-gradient(180deg, transparent 45%, #fecdd3 45%);
}
.card h4 { background: transparent; border-left: 3px solid #d3d3cf; border-radius: 0; padding: 2px 10px; color: #37352f; }
.card ol > li::before { background: #f1f1ef; color: #37352f; border: 1px solid #d3d3cf; }
.callout { background: #f7f6f3 !important; border: none; border-radius: 8px; padding: 14px 16px; color: #37352f !important; }
.qa-item { border: 1px solid #e9e9e7; border-left: 1px solid #e9e9e7; border-radius: 8px; box-shadow: none; background: #fbfbfa; }
.review-bar { border: none; border-top: 1px solid #e9e9e7; border-radius: 0; box-shadow: none; padding: 18px 0; }
""",
    },
    "night-terminal": {
        "label": "暗夜终端专注风（深海暗色仪表盘 + 霓虹光晕卡片 + 深夜护眼）",
        "css": """
/* === 暗夜终端专注风：深色护眼仪表盘 + 发光左轨 + 终端质感 === */
:root {
  --theme: #38bdf8; --theme-dark: #f1f5f9; --theme-mid: #0ea5e9;
  --theme-light: #1e293b; --theme-soft: #131c2e;
  --gold: #fbbf24; --gold-bright: #f59e0b; --gold-light: rgba(245,158,11,0.16); --gold-border: rgba(251,191,36,0.45);
  --red: #fb7185; --red-light: rgba(244,63,94,0.16); --red-border: rgba(251,113,133,0.45);
  --green: #34d399; --green-light: rgba(16,185,129,0.14); --green-border: rgba(52,211,153,0.4);
  --blue: #60a5fa; --blue-light: rgba(59,130,246,0.15); --blue-border: rgba(96,165,250,0.4);
  --paper: #070b14; --surface: #0f1624; --surface-alt: #162033;
  --ink: #e2e8f0; --ink-muted: #94a3b8; --ink-subtle: #64748b;
  --border: #1e2c44; --border-strong: #2d3f5e;
}
body {
  background:
    radial-gradient(circle at 85% 0%, rgba(56,189,248,0.1), transparent 36%),
    radial-gradient(circle at 10% 80%, rgba(244,63,94,0.07), transparent 38%),
    #070b14;
  color: #e2e8f0;
}
.chapter-hero {
  background: linear-gradient(135deg, #090e1a 0%, #111c33 65%, #132842 100%);
  border-bottom: 2px solid #38bdf8;
  box-shadow: 0 8px 28px rgba(0,0,0,0.45);
}
.chapter-kicker { color: #38bdf8; border-color: rgba(56,189,248,0.4); background: rgba(56,189,248,0.1); font-family: Consolas, monospace; }
.nav-bar-wrap { background: #0c1220; border-bottom: 1px solid #1e2c44; }
.nav-tab { background: #131c2e; color: #94a3b8; border-color: #24344f; border-radius: 999px; padding: 6px 15px; }
.nav-tab:hover { border-color: #38bdf8; color: #e2e8f0; }
.nav-tab.active { background: rgba(56,189,248,0.18); border-color: #38bdf8; color: #7dd3fc; box-shadow: 0 0 12px rgba(56,189,248,0.22); }
.filter-btn, .recite-btn, .btn-outline, .review-btn { background: #131c2e; color: #e2e8f0; border-color: #2d3f5e; }
.filter-btn.active { background: rgba(251,191,36,0.2); color: #fde68a; border-color: #fbbf24; }
.recite-btn.active { background: #0284c7; color: #ffffff; border-color: #38bdf8; }
.card {
  background: rgba(15, 22, 36, 0.92);
  border: 1px solid #1e2c44;
  border-radius: 14px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.32);
}
.card.kp-card[data-stars="5"] {
  border-left: 4px solid #fb7185;
  background: linear-gradient(135deg, rgba(244,63,94,0.08) 0%, #0f1624 42%);
}
.card.kp-card[data-stars="4"] { border-left: 4px solid #fbbf24; }
.card-header { border-bottom-color: #1e2c44; }
.card-header h2, .card-header h3, .card h4 { color: #f8fafc; }
.card h4 { background: rgba(56,189,248,0.08); border-left-color: #38bdf8; }
.card p strong, .card li strong, .card td strong { color: #fde68a; background: rgba(251,191,36,0.14); }
.card.kp-card[data-stars="5"] p strong, .card.kp-card[data-stars="5"] li strong { color: #fda4af; background: rgba(244,63,94,0.18); }
.card em, .qa-item em { color: #7dd3fc; background: rgba(56,189,248,0.12); }
.card ul ul > li { color: #cbd5e1; }
.card ol > li::before { background: #0284c7; font-family: Consolas, monospace; border-radius: 6px; }
table { background: #0f1624; }
th { background: #162033; color: #7dd3fc; }
tr:nth-child(even) td { background: #131c2e; }
.callout.exam { color: #fecdd3; }
.callout.warn { color: #fde68a; }
.callout.term { color: #bfdbfe; }
.callout.tip { color: #a7f3d0; }
.mermaid-wrap { background: #f8fafc; border-color: #334155; }
.qa-item { background: #0f1624; border-color: #1e2c44; }
.qa-question ul > li { background: #162033; border-color: #24344f; color: #e2e8f0; }
.qa-toggle { background: rgba(251,191,36,0.15); color: #fde68a; border-color: rgba(251,191,36,0.45); }
.qa-answer { color: #d1fae5; }
.qa-answer strong { color: #6ee7b7; background: rgba(16,185,129,0.2); }
.inline-code { background: #1e293b; color: #38bdf8; }
.math-inline { background: #162033; border-color: #2d3f5e; color: #fde68a; }
.pdf-btn { background: #162033; color: #e2e8f0; border-color: #2d3f5e; }
.pdf-btn.primary { background: #0284c7; border-color: #38bdf8; color: #ffffff; }
""",
    },
    "swiss-poster": {
        "label": "瑞士国际主义海报风（零圆角粗黑网格 + 红黑撞色 + 非对称标题栏）",
        "css": """
/* === 瑞士国际主义海报网格风：零圆角 + 2px 纯黑结构线 + 瑞士红 === */
:root {
  --theme: #111111; --theme-dark: #000000; --theme-mid: #333333;
  --theme-light: #f4f4f4; --theme-soft: #fafafa;
  --gold: #111111; --gold-bright: #e60012; --gold-light: #fff0f0; --gold-border: #111111;
  --red: #e60012; --red-light: #ffe6e8; --red-border: #e60012;
  --green: #007a3d; --green-light: #e8f7ef; --green-border: #007a3d;
  --paper: #f5f5f3; --surface: #ffffff; --surface-alt: #f0f0ec;
  --ink: #111111; --ink-muted: #444444; --border: #111111; --border-strong: #111111;
  --font-serif: "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
}
body { background: #f5f5f3; color: #111111; }
/* 非对称海报式大页眉：左侧黑底红块 + 超粗无衬线大字 */
.chapter-hero {
  background: #ffffff;
  color: #111111;
  padding: 0;
  border-top: 10px solid #e60012;
  border-bottom: 3px solid #111111;
}
.chapter-hero-inner {
  max-width: 1080px;
  padding: 32px 28px 26px;
  border-left: 3px solid #111111;
  border-right: 3px solid #111111;
}
.chapter-kicker {
  background: #111111; color: #ffffff; border: none; border-radius: 0;
  text-transform: uppercase; letter-spacing: 0.14em; font-weight: 800;
}
.hero-star-pill, .hero-star-pill.s5 { background: #e60012; color: #ffffff; border-radius: 0; font-weight: 800; }
.chapter-hero h1 { font-size: 2.25rem; font-weight: 900; letter-spacing: -0.02em; text-transform: uppercase; }
.hero-tag { background: #ffffff; color: #111111; border: 1.5px solid #111111; border-radius: 0; font-weight: 700; }
/* 网格分割式标签栏 */
.nav-bar-wrap { background: #ffffff; border-bottom: 3px solid #111111; box-shadow: none; }
.nav-bar-inner { max-width: 1080px; padding: 0 28px; border-left: 3px solid #111111; border-right: 3px solid #111111; }
.nav-tabs { gap: 0; }
.nav-tab {
  border: none; border-right: 2px solid #111111; border-radius: 0;
  background: #ffffff; color: #111111; padding: 12px 16px; font-weight: 700;
}
.nav-tab.active { background: #111111; color: #ffffff; }
.filter-btn, .recite-btn, .btn-outline, .review-btn { border-radius: 0; border: 2px solid #111111; font-weight: 700; }
.filter-btn.active { background: #e60012; color: #ffffff; border-color: #111111; }
.recite-btn.active { background: #111111; color: #ffffff; }
/* 零圆角网格卡片 */
.page-wrap, .chapter-footer { max-width: 1080px; }
.card, .card.kp-card, .qa-item {
  border-radius: 0; border: 2px solid #111111; box-shadow: none; padding: 24px 26px;
}
.card.kp-card[data-stars="5"] { border-left: 10px solid #e60012; background: #ffffff; }
.card.kp-card[data-stars="4"] { border-left: 10px solid #111111; }
.card-header { border-bottom: 2px solid #111111; }
.star-badge { border-radius: 0; border: 1.5px solid #111111; font-weight: 800; }
.card h4 { background: #111111; color: #ffffff; border-left: 6px solid #e60012; border-radius: 0; padding: 6px 12px; display: inline-block; }
.card ol > li::before { border-radius: 0; background: #111111; font-weight: 900; }
.card.kp-card[data-stars="5"] ol > li::before { background: #e60012; }
.card p strong, .card li strong { color: #111111; background: transparent; border-bottom: 2.5px solid #e60012; padding: 0 1px; border-radius: 0; }
.table-wrap { border-radius: 0; border: 2px solid #111111; }
th { background: #111111; color: #ffffff; }
.callout { border-radius: 0; border: 2px solid #111111; border-left: 8px solid #e60012; }
""",
    },
    "cornell-notes": {
        "label": "康奈尔活页笔记风（网格纸底纹 + 红色装订竖线 + 左线索右笔记双区）",
        "css": """
/* === 康奈尔活页笔记风：方格纸 + 红色装订双竖线 + 左线索/右正文分栏 === */
:root {
  --theme: #1e40af; --theme-dark: #1e3a8a; --theme-mid: #3b82f6;
  --theme-light: #eff6ff; --theme-soft: #f8fafc;
  --gold: #b45309; --gold-bright: #d97706; --gold-light: #fef9c3; --gold-border: #eab308;
  --red: #dc2626; --red-light: #fee2e2; --red-border: #f87171;
  --green: #15803d; --green-light: #dcfce7; --green-border: #4ade80;
  --paper: #fdfdf8; --surface: #ffffff; --surface-alt: #fafaf2;
  --ink: #1f2937; --ink-muted: #4b5563; --border: #cbd5e1; --border-strong: #94a3b8;
}
body {
  background-color: #f8f7f1;
  background-image:
    linear-gradient(to right, rgba(148,163,184,0.14) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148,163,184,0.14) 1px, transparent 1px);
  background-size: 24px 24px;
}
/* 活页笔记本顶部抬头（带红色双栏横线） */
.chapter-hero {
  background: #ffffff;
  color: #1e3a8a;
  border-bottom: 3px double #ef4444;
  padding: 28px 32px 22px;
  position: relative;
}
.chapter-hero::before {
  content: "";
  position: absolute; left: 26px; top: 0; bottom: 0;
  width: 4px; border-left: 1px solid rgba(239,68,68,0.45); border-right: 1px solid rgba(239,68,68,0.45);
}
.chapter-kicker { background: #eff6ff; color: #1d4ed8; border: 1px dashed #93c5fd; }
.hero-star-pill, .hero-star-pill.s5 { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
.chapter-hero h1 { color: #1e3a8a; }
.hero-tag { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
/* 活页索引贴标签栏 */
.nav-bar-wrap { background: rgba(255,255,255,0.92); border-bottom: 1.5px dashed #94a3b8; box-shadow: none; }
.nav-tab {
  background: #fefce8; color: #713f12; border: 1px solid #fde047;
  border-radius: 8px 8px 0 0; border-bottom: none; padding: 7px 14px;
}
.nav-tab.active { background: #1e40af; color: #ffffff; border-color: #1e40af; }
/* 宽屏康奈尔双区卡片：左栏线索标题(26%) + 红竖线 + 右栏笔记正文(74%) */
.page-wrap { max-width: 1060px; }
.card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  box-shadow: 0 3px 0 rgba(148,163,184,0.25);
  position: relative;
}
@media (min-width: 820px) {
  .card.kp-card {
    display: grid;
    grid-template-columns: 230px minmax(0, 1fr);
    column-gap: 28px;
    padding: 20px 26px;
  }
  .card.kp-card .card-header {
    grid-column: 1;
    grid-row: 1 / span 20;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    border-bottom: none;
    border-right: 2px solid rgba(239, 68, 68, 0.45);
    padding-right: 18px;
    padding-bottom: 0;
    margin-bottom: 0;
  }
  .card.kp-card > *:not(.card-header) {
    grid-column: 2;
  }
}
.card p strong, .card li strong {
  color: #1e3a8a;
  background: linear-gradient(180deg, transparent 52%, #fef08a 52%);
}
.card.kp-card[data-stars="5"] p strong, .card.kp-card[data-stars="5"] li strong {
  color: #b91c1c;
  background: linear-gradient(180deg, transparent 52%, #fecaca 52%);
}
.card h4 { background: transparent; border-left: 3px solid #2563eb; border-bottom: 1px dotted #93c5fd; border-radius: 0; }
""",
    },
    "newspaper-broadsheet": {
        "label": "经典财经大报风（鲑鱼粉报纸底 + 刊头双线 + 报刊社论首字下沉）",
        "css": """
/* === 经典财经大报风（FT 鲑鱼粉暖纸 + 刊头双线 + 首字下沉） === */
:root {
  --theme: #0d7680; --theme-dark: #084c53; --theme-mid: #1496a3;
  --theme-light: #e6f2f3; --theme-soft: #f5ebe1;
  --gold: #990f3d; --gold-bright: #990f3d; --gold-light: #fce9ef; --gold-border: #d9829d;
  --red: #990f3d; --red-light: #fce9ef; --red-border: #d9829d;
  --green: #0d7680; --green-light: #e6f4f5; --green-border: #7ec4cb;
  --paper: #fff1e5; --surface: #fff7f0; --surface-alt: #f6e7da;
  --ink: #262a33; --ink-muted: #5b5750; --border: #d8c8b8; --border-strong: #9e8f80;
}
body {
  font-family: "Noto Serif SC", "Songti SC", Georgia, "Times New Roman", serif;
  background: #fff1e5;
  color: #262a33;
}
/* 报刊刊头（Masthead）：居中大报标题 + 顶部粗线与底部双细线 */
.chapter-hero {
  background: #fff1e5;
  color: #262a33;
  text-align: center;
  padding: 28px 24px 20px;
  border-top: 6px solid #262a33;
  border-bottom: 4px double #262a33;
}
.hero-top-row { justify-content: center; border-bottom: 1px solid #d8c8b8; padding-bottom: 10px; margin-bottom: 14px; }
.chapter-kicker { background: transparent; color: #990f3d; border: none; font-weight: 800; letter-spacing: 0.2em; }
.hero-star-pill, .hero-star-pill.s5 { background: #990f3d; color: #fff1e5; border-radius: 2px; }
.chapter-hero h1 { font-size: 2.3rem; font-weight: 900; letter-spacing: 0.04em; color: #1a1d24; }
.hero-tags { justify-content: center; }
.hero-tag { background: transparent; color: #5b5750; border: 1px solid #c5b4a3; border-radius: 0; }
/* 报刊版面索引条 */
.nav-bar-wrap { background: #f6e7da; border-bottom: 1.5px solid #262a33; box-shadow: none; }
.nav-tab {
  background: transparent; border: none; border-right: 1px solid #d2c1b0; border-radius: 0;
  color: #3e3a35; padding: 8px 15px; font-weight: 600;
}
.nav-tab.active { background: #262a33; color: #fff1e5; }
/* 社论专栏式无阴影分割版面 */
.page-wrap { max-width: 1040px; }
.card, .card.kp-card, .card.kp-card[data-stars="5"], .card.kp-card[data-stars="4"] {
  background: transparent;
  border: none;
  border-left: none;
  border-top: 2px solid #262a33;
  border-bottom: 1px solid #d8c8b8;
  border-radius: 0;
  box-shadow: none;
  padding: 20px 6px 24px;
}
.card.kp-card[data-stars="5"] { border-top: 4px solid #990f3d; }
.card-header { border-bottom: 1px solid #d8c8b8; }
.card-header h2, .card-header h3 { font-size: 1.38rem; color: #1a1d24; }
/* 经典首字下沉（Drop Cap）用于每张考点卡首段 */
.card > p:first-of-type::first-letter {
  float: left;
  font-size: 2.6rem;
  line-height: 0.9;
  padding: 4px 8px 0 0;
  font-weight: 800;
  color: #990f3d;
}
.card h4 { background: transparent; border-left: 4px solid #990f3d; border-radius: 0; color: #990f3d; }
.card p strong, .card li strong { color: #990f3d; background: rgba(153,15,61,0.08); }
.table-wrap { border: none; border-radius: 0; }
table { background: #fff7f0; border-top: 2px solid #262a33; border-bottom: 2px solid #262a33; }
th { background: #f2dfd0; color: #262a33; }
.callout { background: #f6e7da !important; border: 1px solid #c5b4a3; border-left: 4px solid #0d7680; border-radius: 0; color: #262a33 !important; }
.qa-item { background: #fff7f0; border: 1px solid #c5b4a3; border-left: 4px solid #990f3d; border-radius: 0; }
""",
    },
    "neobrutalism": {
        "label": "新粗野主义潮酷卡牌风（粗黑边框 + 实心硬投影 + 撞色弹跳卡片）",
        "css": """
/* === 新粗野主义 Neo-Brutalism：2.5px 粗黑框 + 硬偏移投影 + 活力撞色 === */
:root {
  --theme: #18181b; --theme-dark: #09090b; --theme-mid: #27272a;
  --theme-light: #fef08a; --theme-soft: #fffbeb;
  --gold: #18181b; --gold-bright: #f59e0b; --gold-light: #fde047; --gold-border: #18181b;
  --red: #e11d48; --red-light: #fda4af; --red-border: #18181b;
  --green: #059669; --green-light: #86efac; --green-border: #18181b;
  --paper: #fffbeb; --surface: #ffffff; --surface-alt: #fef9c3;
  --ink: #18181b; --ink-muted: #3f3f46; --border: #18181b; --border-strong: #18181b;
  --font-serif: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
}
body {
  background-color: #fffbeb;
  background-image: radial-gradient(#18181b 0.8px, transparent 0.8px);
  background-size: 20px 20px;
}
/* 撞色粗框大顶卡 */
.chapter-hero {
  max-width: 1020px;
  margin: 22px auto 0;
  background: #fde047;
  color: #18181b;
  border: 3px solid #18181b;
  border-radius: 16px;
  box-shadow: 7px 7px 0 #18181b;
  padding: 26px 30px;
}
.chapter-kicker { background: #ffffff; color: #18181b; border: 2px solid #18181b; box-shadow: 2px 2px 0 #18181b; }
.hero-star-pill, .hero-star-pill.s5 { background: #fb7185; color: #18181b; border: 2px solid #18181b; box-shadow: 2px 2px 0 #18181b; font-weight: 800; }
.chapter-hero h1 { font-size: 1.95rem; font-weight: 900; color: #18181b; }
.hero-tag { background: #67e8f9; color: #18181b; border: 2px solid #18181b; font-weight: 700; }
/* 弹跳按钮式分栏 */
.nav-bar-wrap { background: transparent; border: none; box-shadow: none; margin-top: 16px; }
.nav-bar-inner { max-width: 1020px; padding: 6px 0; }
.nav-tab {
  background: #ffffff; color: #18181b; border: 2.5px solid #18181b; border-radius: 10px;
  box-shadow: 3px 3px 0 #18181b; font-weight: 800; transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.nav-tab:hover { transform: translate(-2px, -2px); box-shadow: 5px 5px 0 #18181b; color: #18181b; }
.nav-tab.active { background: #a7f3d0; color: #18181b; border-color: #18181b; transform: translate(1px, 1px); box-shadow: 2px 2px 0 #18181b; }
.filter-btn, .recite-btn, .btn-outline, .review-btn, .qa-toggle {
  border: 2px solid #18181b !important; box-shadow: 3px 3px 0 #18181b; font-weight: 800; color: #18181b;
}
.filter-btn.active { background: #fde047; }
.recite-btn.active { background: #c084fc; color: #18181b; }
/* 硬投影撞色卡牌 */
.card, .card.kp-card, .qa-item {
  background: #ffffff;
  border: 2.5px solid #18181b !important;
  border-radius: 14px;
  box-shadow: 6px 6px 0 #18181b;
}
.card.kp-card[data-stars="5"] { background: #fff1f2; }
.card.kp-card[data-stars="4"] { background: #fefce8; }
.card-header { border-bottom: 2.5px solid #18181b; }
.star-badge { border: 2px solid #18181b !important; box-shadow: 2px 2px 0 #18181b; font-weight: 800; color: #18181b !important; }
.star-badge.s5 { background: #fb7185; }
.star-badge.s4 { background: #fde047; }
.star-badge.s3 { background: #67e8f9; }
.card h4 { background: #67e8f9; border: 2px solid #18181b; border-left: 2px solid #18181b; border-radius: 8px; box-shadow: 3px 3px 0 #18181b; display: inline-block; padding: 4px 12px; }
.card ol > li::before { border: 2px solid #18181b; background: #fde047; color: #18181b; box-shadow: 2px 2px 0 #18181b; }
.card.kp-card[data-stars="5"] ol > li::before { background: #fb7185; color: #18181b; }
.card p strong, .card li strong { background: #fde047; color: #18181b; padding: 1px 4px; border-radius: 4px; }
.table-wrap { border: 2.5px solid #18181b; box-shadow: 4px 4px 0 #18181b; }
th { background: #18181b; color: #fde047; }
.callout { border: 2px solid #18181b !important; box-shadow: 4px 4px 0 #18181b; color: #18181b !important; }
.callout.warn { background: #fde047; }
.callout.exam { background: #fda4af; }
.callout.term { background: #bae6fd; }
.callout.tip { background: #bbf7d0; }
@media (max-width: 760px) {
  .chapter-hero { margin: 12px 14px 0; }
  .nav-bar-inner { padding: 6px 14px; }
}
""",
    },
    "chinese-ink": {
        "label": "东方宋韵水墨书院风（宣纸留白 + 朱砂方印 + 卷轴双框 + 全宋体）",
        "css": """
/* === 东方宋韵水墨书院风：宣纸留白 + 朱砂印章 + 卷轴居中标题 + 竹青浓墨 === */
:root {
  --theme: #2d4c43; --theme-dark: #1d332c; --theme-mid: #3f6a5e;
  --theme-light: #e8efec; --theme-soft: #f2f5f3;
  --gold: #8c6239; --gold-bright: #a67848; --gold-light: #f7efe5; --gold-border: #cfa980;
  --red: #9e2a2b; --red-light: #f9ecec; --red-border: #d89696;
  --green: #2d4c43; --green-light: #ebf3f0; --green-border: #8eb3a7;
  --paper: #f3efe6; --surface: #faf8f2; --surface-alt: #f0ebe0;
  --ink: #232320; --ink-muted: #5a574f; --border: #d6cebe; --border-strong: #b8ad98;
}
body {
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", "FangSong", serif;
  background:
    radial-gradient(ellipse at 100% 0%, rgba(45,76,67,0.08), transparent 45%),
    radial-gradient(ellipse at 0% 100%, rgba(158,42,43,0.05), transparent 42%),
    #f3efe6;
  color: #232320;
  letter-spacing: 0.02em;
}
/* 卷轴式水墨留白页眉 + 朱砂方印 */
.chapter-hero {
  background: linear-gradient(180deg, #eae4d7 0%, #f3efe6 100%);
  color: #232320;
  text-align: center;
  padding: 36px 24px 26px;
  border-bottom: 1px solid #c9bfa9;
  position: relative;
}
.hero-top-row { justify-content: center; gap: 12px; }
.chapter-kicker {
  background: transparent; color: #2d4c43; border: 1px solid #2d4c43;
  border-radius: 2px; padding: 3px 14px; letter-spacing: 0.25em;
}
/* 朱砂方印样式 */
.hero-star-pill, .hero-star-pill.s5 {
  background: #9e2a2b; color: #faf8f2; border: 2px solid #9e2a2b;
  outline: 1px solid #9e2a2b; outline-offset: 2px;
  border-radius: 2px; padding: 2px 10px; font-weight: 700;
}
.chapter-hero h1 { font-size: 2.15rem; font-weight: 700; color: #1d332c; letter-spacing: 0.1em; margin: 12px 0; }
.hero-tags { justify-content: center; }
.hero-tag { background: #faf8f2; color: #5a574f; border: 1px solid #c9bfa9; border-radius: 2px; }
/* 典雅居中分栏 */
.nav-bar-wrap { background: #f7f4ec; border-bottom: 1px solid #d6cebe; box-shadow: none; }
.nav-bar-inner { justify-content: center; gap: 14px; }
.nav-tab {
  background: transparent; border: 1px solid transparent; border-radius: 2px;
  color: #5a574f; padding: 7px 14px; letter-spacing: 0.06em;
}
.nav-tab.active {
  background: #2d4c43; color: #faf8f2; border-color: #2d4c43;
}
/* 宣纸双细框书院卡片 */
.page-wrap { max-width: 960px; }
.card {
  background: #faf8f2;
  border: 1px solid #c9bfa9;
  outline: 1px solid #e3dccd;
  outline-offset: -5px;
  border-radius: 3px;
  box-shadow: 0 2px 12px rgba(35,35,32,0.04);
  padding: 26px 32px;
}
.card.kp-card[data-stars="5"] { border-left: 4px solid #9e2a2b; background: #fcfaf5; }
.card.kp-card[data-stars="4"] { border-left: 4px solid #8c6239; }
.card-header { border-bottom: 1px solid #d6cebe; padding-bottom: 10px; }
.card-header h2, .card-header h3 { color: #1d332c; letter-spacing: 0.06em; }
.star-badge.s5 { background: #9e2a2b; color: #faf8f2; border-color: #9e2a2b; border-radius: 2px; }
.star-badge.s4 { background: #f7efe5; color: #8c6239; border-color: #cfa980; border-radius: 2px; }
.star-badge.s3 { background: #e8efec; color: #2d4c43; border-color: #8eb3a7; border-radius: 2px; }
.card h4 {
  background: transparent; border-left: none; text-align: left;
  border-bottom: 1px solid #d6cebe; color: #2d4c43; padding: 4px 0; border-radius: 0;
}
.card h4::before { content: "❖ "; color: #9e2a2b; }
.card p strong, .card li strong { color: #9e2a2b; background: rgba(158,42,43,0.07); }
.card ol > li::before { background: #2d4c43; border-radius: 2px; font-family: Georgia, serif; }
.card.kp-card[data-stars="5"] ol > li::before { background: #9e2a2b; }
.callout { border-radius: 2px; border: 1px solid #d6cebe; border-left: 3px solid #2d4c43; background: #f4efe4; }
.callout.exam { border-left-color: #9e2a2b; background: #f9f0ee; }
""",
    },
}


def parse_frontmatter(text: str):
    meta = {
        "id": "1",
        "title": "章节标题",
        "kicker": "第一章",
        "stars": "★★★★ 重点",
        "theme": "editorial",
        "tags": [],
        "materials": [],
    }
    if not text.startswith("---"):
        return meta, text

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, flags=re.S)
    if not m:
        return meta, text

    fm_text = m.group(1)
    body = text[m.end():]
    cur_list_key = None

    for raw in fm_text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^\s*-\s+", line) and cur_list_key in ("tags", "materials"):
            val = re.sub(r"^\s*-\s+", "", line).strip().strip('"').strip("'")
            meta[cur_list_key].append(val)
            continue
        m_kv = re.match(r"^([A-Za-z_]+)\s*:\s*(.*)$", line)
        if m_kv:
            k = m_kv.group(1).strip().lower()
            v = m_kv.group(2).strip().strip('"').strip("'")
            if k in ("tags", "materials"):
                cur_list_key = k
                if v:
                    meta[k].append(v)
            else:
                cur_list_key = None
                meta[k] = v

    return meta, body


def clean_math(expr: str) -> str:
    s = expr.strip()
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1) ÷ (\2)", s)
    replacements = [
        (r"\Longleftrightarrow", "⟺"), (r"\Leftrightarrow", "⇔"),
        (r"\leftrightarrow", "↔"), (r"\Rightarrow", "⇒"),
        (r"\longrightarrow", "→"), (r"\rightarrow", "→"), (r"\to", "→"),
        (r"\cdots", "⋯"), (r"\ldots", "…"), (r"\dots", "…"),
        (r"\times", "×"), (r"\cdot", "·"), (r"\le", "≤"), (r"\ge", "≥"),
        (r"\neq", "≠"), (r"\approx", "≈"),
        (r"\sum", "Σ"), (r"\Delta", "Δ"), (r"\alpha", "α"), (r"\beta", "β"),
        (r"\gt", ">"), (r"\lt", "<"),
    ]
    for k, v in replacements:
        s = s.replace(k, v)
    s = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"_([A-Za-z0-9]+)", r"<sub>\1</sub>", s)
    s = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"\^([0-9]+)", r"<sup>\1</sup>", s)
    return s


def inline_md(text: str) -> str:
    text = text.replace("<br>", "§§BR§§").replace("<br/>", "§§BR§§").replace("<br />", "§§BR§§")
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r'<code class="inline-code">\1</code>', text)
    text = re.sub(r"\$\$([^$]+)\$\$", lambda m: f'<span class="math-inline">{clean_math(m.group(1))}</span>', text)
    text = re.sub(r"\$([^$\n]+)\$", lambda m: f'<span class="math-inline">{clean_math(m.group(1))}</span>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = text.replace("§§BR§§", "<br>")
    return text


def detect_stars(text: str):
    if "★★★★★" in text:
        return 5, "★★★★★ 必考核心"
    if "★★★★☆" in text:
        return 4, "★★★★☆ 高频重点"
    if "★★★★" in text:
        return 4, "★★★★ 高频重点"
    if "★★★☆" in text:
        return 3, "★★★☆ 重点掌握"
    if "★★★" in text:
        return 3, "★★★ 基础掌握"
    if "★★" in text:
        return 2, "★★ 了解/拓展"
    return 0, ""


def strip_stars(title: str) -> str:
    t = re.sub(r"[★☆]+", "", title)
    t = re.sub(r"[（(]\s*(必考核心|高频重点|基础掌握|了解/拓展|了解)?\s*[）)]", "", t)
    return re.sub(r"\s{2,}", " ", t).strip(" ：:—-") or title.strip()


def render_list(lines):
    stack = []
    parts = []
    for raw in lines:
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", raw)
        if not m:
            if parts and parts[-1].endswith("</li>"):
                parts[-1] = parts[-1][:-5] + "<br>" + inline_md(raw.strip()) + "</li>"
            continue
        indent = len(m.group(1).replace("\t", "  "))
        tag = "ol" if m.group(2).endswith(".") else "ul"
        content = inline_md(m.group(3))

        if not stack:
            stack.append((indent, tag))
            parts.append(f"<{tag}>")
        elif indent > stack[-1][0]:
            stack.append((indent, tag))
            parts.append(f"<{tag}>")
        else:
            while len(stack) > 1 and indent < stack[-1][0]:
                parts.append(f"</{stack.pop()[1]}>")
            if indent == stack[-1][0] and tag != stack[-1][1]:
                parts.append(f"</{stack.pop()[1]}>")
                stack.append((indent, tag))
                parts.append(f"<{tag}>")
        parts.append(f"<li>{content}</li>")

    while stack:
        parts.append(f"</{stack.pop()[1]}>")
    return "\n".join(parts)


def md_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped or re.match(r"^[-*_]{3,}$", stripped):
            i += 1
            continue

        # Interactive Q&A block: :::qa [标签] ... --- ... :::
        m_qa = re.match(r"^:::qa(?:\s+\[([^\]]+)\])?\s*$", stripped)
        if m_qa:
            qa_label = m_qa.group(1) or "自测题"
            i += 1
            qa_lines = []
            while i < n and lines[i].strip() != ":::":
                qa_lines.append(lines[i])
                i += 1
            i += 1  # skip :::
            qa_raw = "\n".join(qa_lines)
            if re.search(r"(?m)^---\s*$", qa_raw):
                q_part, a_part = re.split(r"(?m)^---\s*$", qa_raw, maxsplit=1)
            else:
                q_part, a_part = qa_raw, ""
            cls = "mcq" if "单选" in qa_label or "选择" in qa_label else ("essay" if "论述" in qa_label or "案例" in qa_label else "short")
            out.append(f'''<article class="qa-item {cls}">
  <div class="qa-meta"><span class="qa-type">{html.escape(qa_label)}</span></div>
  <div class="qa-question">{md_to_html(q_part.strip())}</div>
  <button class="qa-toggle" type="button">查看参考答案与采分点 ▼</button>
  <div class="qa-answer">{md_to_html(a_part.strip())}</div>
</article>''')
            continue

        # Fenced code block (Mermaid or code/diagram)
        if stripped.startswith("```"):
            lang = stripped[3:].strip().lower()
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code_body = "\n".join(code_lines)
            if lang == "mermaid":
                out.append(f'<div class="mermaid-wrap"><div class="mermaid">{html.escape(code_body)}</div></div>')
            else:
                out.append(f'<pre class="ascii-diagram">{html.escape(code_body)}</pre>')
            continue

        # Display math $$ ... $$
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            out.append(f'<div class="formula-box">{clean_math(stripped[2:-2])}</div>')
            i += 1
            continue
        if stripped == "$$":
            i += 1
            mlines = []
            while i < n and lines[i].strip() != "$$":
                mlines.append(lines[i])
                i += 1
            i += 1
            out.append(f'<div class="formula-box">{clean_math(" ".join(mlines))}</div>')
            continue

        # Sub-headings inside cards
        m_h = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m_h:
            lvl = len(m_h.group(1))
            htext = inline_md(m_h.group(2))
            if lvl <= 3:
                out.append(f"<h4>{htext}</h4>")
            else:
                out.append(f'<h4 class="kp-sub-heading">{htext}</h4>')
            i += 1
            continue

        # Blockquote -> Semantic Callout
        if stripped.startswith(">"):
            bq = []
            while i < n and lines[i].strip().startswith(">"):
                bq.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            bq_text = "\n".join(bq)
            cls = "tip"
            if any(k in bq_text for k in ["易错", "避坑", "警示", "注意", "陷阱", "不考"]):
                cls = "warn"
            elif any(k in bq_text for k in ["术语", "对照", "口径"]):
                cls = "term"
            elif any(k in bq_text for k in ["必考", "考情", "高分", "原题", "重点"]):
                cls = "exam"
            out.append(f'<div class="callout {cls}">{md_to_html(bq_text)}</div>')
            continue

        # Markdown Table
        if "|" in stripped and i + 1 < n and re.match(r"^\|?[\s:\-]+\|[\s:\-|]+$", lines[i + 1].strip()):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ['<div class="table-wrap"><table><thead><tr>']
            t.extend(f"<th>{inline_md(h)}</th>" for h in headers)
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>")
                for ci in range(len(headers)):
                    t.append(f"<td>{inline_md(r[ci] if ci < len(r) else '')}</td>")
                t.append("</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue

        # Ordered / Unordered Lists
        if re.match(r"^(\s*)([-*+]|\d+\.)\s+", line):
            llines = []
            while i < n:
                cur = lines[i]
                if not cur.strip():
                    if i + 1 < n and re.match(r"^(\s*)([-*+]|\d+\.)\s+", lines[i + 1]):
                        i += 1
                        continue
                    break
                if re.match(r"^(\s*)([-*+]|\d+\.)\s+", cur) or (cur.startswith("  ") and not cur.strip().startswith("|") and not cur.strip().startswith("```")):
                    llines.append(cur)
                    i += 1
                else:
                    break
            out.append(render_list(llines))
            continue

        # Paragraph
        plines = []
        while i < n:
            cur = lines[i].strip()
            if (
                not cur
                or cur.startswith("#")
                or cur.startswith(">")
                or cur.startswith("```")
                or cur.startswith(":::")
                or re.match(r"^[-*_]{3,}$", cur)
                or re.match(r"^([-*+]|\d+\.)\s+", cur)
                or ("|" in cur and i + 1 < n and re.match(r"^\|?[\s:\-]+\|[\s:\-|]+$", lines[i + 1].strip()))
            ):
                break
            plines.append(cur)
            i += 1
        if not plines:
            plines.append(stripped)
            i += 1
        out.append(f"<p>{inline_md(' '.join(plines))}</p>")

    return "\n".join(out)


def render_tab_content(tab_md: str):
    """Split a tab's markdown by `## ` into cards (with star badges if present) and standalone QA blocks."""
    has_qa = ":::qa" in tab_md
    blocks = []
    if has_qa:
        blocks.append('''<div class="quiz-toolbar">
  <span>点击每题下方按钮显示或收起答案</span>
  <button class="btn-outline" id="toggleAllAnswers" type="button">全部展开答案</button>
</div>''')

    parts = re.split(r"(?m)^## ", tab_md)
    lead_md = parts[0].strip()
    if lead_md:
        if ":::qa" in lead_md:
            blocks.append(md_to_html(lead_md))
        else:
            blocks.append(f'<div class="card">{md_to_html(lead_md)}</div>')

    has_star_cards = False
    for p in parts[1:]:
        plines = p.splitlines()
        h2_title = plines[0].strip()
        h2_body = "\n".join(plines[1:]).strip()
        stars, star_label = detect_stars(h2_title)

        if ":::qa" in h2_body and stars == 0:
            blocks.append(f'<div class="qa-section-title">{inline_md(h2_title)}</div>')
            blocks.append(md_to_html(h2_body))
            continue

        if stars > 0:
            has_star_cards = True
            clean_t = strip_stars(h2_title)
            blocks.append(f'''<article class="card kp-card" data-stars="{stars}">
  <div class="card-header">
    <h2>{inline_md(clean_t)}</h2>
    <span class="star-badge s{stars}">{star_label}</span>
  </div>
  {md_to_html(h2_body)}
</article>''')
        else:
            blocks.append(f'''<article class="card">
  <div class="card-header">
    <h2>{inline_md(h2_title)}</h2>
  </div>
  {md_to_html(h2_body)}
</article>''')

    if has_star_cards:
        blocks.append('<div class="empty-filter-msg">当前板块在该星级筛选条件下暂无对应考点，可点击上方“全部考点”查看。</div>')

    return "\n".join(blocks), has_star_cards


def render_materials(materials):
    blocks = []
    for entry in materials:
        if "|" in entry:
            path_part, label = [x.strip() for x in entry.split("|", 1)]
        else:
            path_part = entry.strip()
            label = os.path.basename(path_part)
        # Quote only filename segments, preserve ../
        segs = path_part.replace("\\", "/").split("/")
        href = "/".join(s if s in ("", ".", "..") else quote(s) for s in segs)
        fname = os.path.basename(path_part)
        ext = os.path.splitext(fname)[1].lower()
        if ext == ".pdf":
            blocks.append(f'''<div class="pdf-block">
  <div class="pdf-head">
    <div class="pdf-name">📄 {html.escape(label)}</div>
    <div class="pdf-actions">
      <a class="pdf-btn" href="{href}" target="_blank" rel="noopener">↗ 新窗口打开</a>
      <a class="pdf-btn primary" href="{href}" download="{html.escape(fname)}">↓ 下载 PDF</a>
    </div>
  </div>
  <iframe class="pdf-viewer" data-src="{href}" title="{html.escape(label)}"></iframe>
</div>''')
        else:
            blocks.append(f'''<div class="dl-only">
  <div>
    <div class="pdf-name">📝 {html.escape(label)}</div>
    <div class="dl-only-note">原件文件（{html.escape(fname)}）</div>
  </div>
  <div class="pdf-actions">
    <a class="pdf-btn primary" href="{href}" download="{html.escape(fname)}">↓ 下载 / 打开原件</a>
  </div>
</div>''')
    return "\n".join(blocks)


def compile_md_file(md_path: str, theme_override: str = None, out_path_override: str = None):
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()

    meta, body = parse_frontmatter(raw)
    theme_key = (theme_override or meta.get("theme") or "editorial").strip().lower()
    if theme_key not in THEMES:
        theme_key = "editorial"
    theme_css = THEMES[theme_key]["css"].strip()
    theme_style_block = f"\n  <style>\n{theme_css}\n  </style>" if theme_css else ""
    # Split top-level `# ` headings into parallel tabs
    tab_chunks = re.split(r"(?m)^# ", body.strip())
    tabs = []
    tab_bodies = {}
    any_star_cards = False

    for idx, chunk in enumerate(tab_chunks):
        c = chunk.strip()
        if not c:
            continue
        if idx == 0 and not body.strip().startswith("# "):
            tid = "tab0"
            tlabel = "核心内容"
            tmd = c
        else:
            lines = c.splitlines()
            tlabel = lines[0].strip()
            tid = f"tab{len(tabs) + 1}"
            tmd = "\n".join(lines[1:]).strip()
        rendered, has_stars = render_tab_content(tmd)
        any_star_cards = any_star_cards or has_stars
        tabs.append((tid, tlabel))
        tab_bodies[tid] = rendered

    if meta["materials"]:
        tabs.append(("raw-materials", "📄 原始课件"))
        tab_bodies["raw-materials"] = render_materials(meta["materials"])

    star_num, _ = detect_stars(meta["stars"])
    hero_star_cls = f"s{star_num}" if star_num else "s4"
    tag_html = "\n        ".join(f'<span class="hero-tag">{html.escape(t)}</span>' for t in meta["tags"])

    tab_btns = [
        f'<button class="nav-tab{" active" if i == 0 else ""}" type="button" data-target="{tid}">{html.escape(lbl)}</button>'
        for i, (tid, lbl) in enumerate(tabs)
    ]

    filter_html = ""
    if any_star_cards:
        filter_html = '''<div class="star-filter" aria-label="按重要程度筛选考点">
        <span class="star-filter-label">星级筛选：</span>
        <button class="filter-btn active" type="button" data-min="0">全部考点</button>
        <button class="filter-btn" type="button" data-min="4">★★★★+</button>
        <button class="filter-btn" type="button" data-min="5">★★★★★</button>
      </div>'''

    sections_html = [
        f'<section class="section{" active" if i == 0 else ""}" id="section-{tid}">\n{tab_bodies[tid]}\n</section>'
        for i, (tid, _) in enumerate(tabs)
    ]

    html_out = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(meta["title"])}</title>
  <link rel="stylesheet" href="../unit.css">{theme_style_block}
</head>
<body data-unit-id="{html.escape(meta["id"])}">
  <header class="chapter-hero">
    <div class="chapter-hero-inner">
      <div class="hero-top-row">
        <span class="chapter-kicker">{html.escape(meta["kicker"])}</span>
        <span class="hero-star-pill {hero_star_cls}">{html.escape(meta["stars"])}</span>
      </div>
      <h1>{html.escape(meta["title"])}</h1>
      {f'<div class="hero-tags">{tag_html}</div>' if tag_html else ''}
    </div>
  </header>

  <div class="nav-bar-wrap">
    <div class="nav-bar-inner">
      <div class="nav-tabs">
        {chr(10).join(tab_btns)}
      </div>
      {filter_html}
    </div>
  </div>

  <main class="page-wrap">
    {chr(10).join(sections_html)}
  </main>

  <footer class="chapter-footer">
    <div class="review-bar">
      <button class="review-btn" id="markReviewedBtn" type="button">☐ 标记本章已复习完成</button>
    </div>
  </footer>

  <script src="../vendor/mermaid.min.js"></script>
  <script src="../unit.js"></script>
</body>
</html>
'''

    out_path = out_path_override or (os.path.splitext(md_path)[0] + ".html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Compiled {md_path} -> {out_path} ({len(tabs)} tabs, theme={theme_key})")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python build_unit.py <file.md | unit_dir> [--theme editorial|academic|tech|literary|night] [--out file.html]")
        sys.exit(1)

    target = None
    theme_override = None
    out_override = None
    i = 0
    while i < len(args):
        if args[i] == "--theme" and i + 1 < len(args):
            theme_override = args[i + 1]
            i += 2
        elif args[i] == "--out" and i + 1 < len(args):
            out_override = args[i + 1]
            i += 2
        else:
            target = args[i]
            i += 1

    if not target:
        print("Missing target file or directory.")
        sys.exit(1)

    if os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, "*.md")))
        if not files:
            print(f"No .md files found in {target}")
            sys.exit(1)
        for fp in files:
            compile_md_file(fp, theme_override=theme_override)
    else:
        compile_md_file(target, theme_override=theme_override, out_path_override=out_override)


if __name__ == "__main__":
    main()
