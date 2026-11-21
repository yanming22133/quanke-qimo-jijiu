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


def parse_frontmatter(text: str):
    meta = {
        "id": "1",
        "title": "章节标题",
        "kicker": "第一章",
        "stars": "★★★★ 重点",
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


def compile_md_file(md_path: str):
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()

    meta, body = parse_frontmatter(raw)
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
  <link rel="stylesheet" href="../unit.css">
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

  <script src="../vendor/mermaid.min.js" onerror="var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js';s.onload=function(){{if(window.mermaid&&typeof renderVisibleMermaid==='function'){{window.mermaid.initialize({{startOnLoad:false,securityLevel:'loose',theme:'base'}});renderVisibleMermaid();}}}};document.head.appendChild(s);"></script>
  <script src="../unit.js"></script>
</body>
</html>
'''

    out_path = os.path.splitext(md_path)[0] + ".html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Compiled {md_path} -> {out_path} ({len(tabs)} tabs)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_unit.py <file.md | unit_dir>")
        sys.exit(1)
    target = sys.argv[1]
    if os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, "*.md")))
        if not files:
            print(f"No .md files found in {target}")
            sys.exit(1)
        for fp in files:
            compile_md_file(fp)
    else:
        compile_md_file(target)


if __name__ == "__main__":
    main()
