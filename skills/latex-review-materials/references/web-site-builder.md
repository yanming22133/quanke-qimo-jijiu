# Interactive Offline Review Website (`HTML`)

Turn Step 0 exam intelligence + chapter summaries + exercises + original courseware into a **Markdown-driven static review website** that runs directly in any desktop or mobile browser (zero backend, zero framework build step, 100% offline-capable).

## When to Use

- The user wants a **review website / interactive HTML study site** (alone or paired with printable PDF mock exams: **HTML for daily review & cloze recall + PDF for timed mock exams**).
- Ideal for mobile reading, rapid pre-exam star-level sprinting, active recall (`🧠 默写模式`), and side-by-side browsing of original PDF/Word slides.

---

## 1. Quick Build Workflow

1. **Copy the static shell** from `references/templates/study-site/` into the user's target site directory (keep existing user files intact):
   - `index.html`, `index.css`, `site.js` (dashboard, collapsible sidebar, `localStorage` review progress tracker)
   - `unit.css`, `unit.js` (parallel tabs, star filter, memory typography, per-question Q&A toggles, `🧠 默写模式`, lazy PDF preview, Mermaid rendering)
2. **Optional offline Mermaid bundle** (recommended so Mermaid charts render with zero internet):
   ```bash
   mkdir -p <site_dir>/vendor
   curl -L https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js -o <site_dir>/vendor/mermaid.min.js
   ```
   *(If `vendor/mermaid.min.js` is omitted, compiled pages automatically fall back to jsDelivr CDN when online.)*
3. **Configure `index.html` & `site.js`**:
   - Update course name, exam date, and the 100-point question-type breakdown from Step 0.
   - Populate `units` in `site.js` with each chapter's unique `id`, `badge`, `title`, `file` (`unit/<id>.html`), `icon`, `stars`, and `desc`.
   - Keep UI copy crisp; remove redundant English subtitles, group divider fluff, and meta-hints.
4. **Author each chapter in Markdown (`unit/<id>.md`)** following the syntax below, then compile all chapters in one command:
   ```bash
   python references/build_unit.py "<site_dir>/unit"
   ```
5. **Organize original courseware** (optional): put raw `.pdf` / `.doc` / `.docx` files into a clean folder (e.g. `课件原件/`) and list them in each chapter's frontmatter `materials:` so every unit gets a parallel `📄 原始课件` tab.

---

## 2. Markdown Syntax Specification (`unit/*.md` → `unit/*.html`)

See `references/templates/study-site/unit/1.md` for a full working example.

| Markdown Syntax | Rendered Layout & Interactive Behavior |
| :--- | :--- |
| Top `---` YAML Frontmatter | `id`, `title`, `kicker`, `stars`, `tags`, `materials` (`path \| label` list → auto-generates parallel `📄 原始课件` tab with lazy PDF iframe / Word download card) |
| `# Tab Name` (H1) | **Parallel top-level tab** (e.g. `# 📋 核心考点总览`, `# 🌐 板块一`, `# ✏️ 模拟自测题`). Never dump all content into one giant tab. |
| `## Card Title ★★★★★` (H2) | **Star-rated knowledge point card**. Automatically parses `★★★★★` / `★★★★` / `★★★` / `★★` to render colored left border, star badge, and enable the top **star filter bar** (`全部考点` / `★★★★+` / `★★★★★`). |
| `### Sub-section` (H3) | Gold left-bar + warm tinted section heading |
| `#### Detail` (H4) | Teal underlined sub-heading |
| `**Bold**` | Highlighted memory keyword; automatically blurred in **`🧠 默写模式`** (click any single blurred term to reveal/re-hide independently) |
| `*Italic*` | Warm serif italic emphasis for terms, examples, and notes |
| `1.` / `-` lists | Colored circular numbered badges / accent triangles (`▸`) & nested bullets (`•`) |
| `\| Pipe Table \|` | Striped responsive table with horizontal scroll on mobile |
| ```` ```mermaid ```` | Local offline Mermaid diagram (`flowchart LR/TD`, etc.), rendered on demand when switching tabs |
| `> Blockquote` | Semantic callout box: `易错/避坑/注意/陷阱` → amber; `术语/对照` → blue; `必考/考情/高分` → crimson; default → green |
| `:::qa [Type]` ... `---` ... `:::` | **Per-question interactive self-test card** with individual `查看参考答案与采分点 ▼` toggle button + tab-top `全部展开答案` button |

---

## 3. Mobile & Customization Rules

- **Non-sticky navigation**: `.nav-bar-wrap` and mobile `.header` are intentionally non-sticky so they never block half the screen on phones.
- **Custom color themes**: adjust `--theme`, `--theme-dark`, `--gold`, `--red`, `--green` CSS variables at the top of `index.css` and `unit.css` in sync (do not lock every course to the same palette if the user asks for a different aesthetic).
- **Verification**: check that every `unit/*.html` exists, all relative `materials:` links resolve on disk (`0` missing), all Mermaid blocks render cleanly without syntax errors, and per-question Q&A toggles & `🧠 默写模式` work smoothly.
