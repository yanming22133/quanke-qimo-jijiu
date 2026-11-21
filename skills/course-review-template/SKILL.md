---
name: course-review-template
description: 使用配套 Markdown 驱动静态网站模板，将课程资料制作成带侧栏导航、平行板块分栏、星级考点筛选、离线 Mermaid 流程图、单题答案切换、默写模式与原始课件预览的复习网站；适用于需要复用该模板的新课程或修改基于该模板的网站。
---

# 课程复习网站模板（Markdown 驱动版）

使用 `assets/study-site/` 的可运行离线静态模板与 `scripts/build_unit.py` 编译器，将用户提供的课程资料整理为按章节与板块浏览的复习网站。模板采用「现代财经智库 / 战略蓝图」风（深黛青主色、暖象牙纸面、琥珀金与朱砂红星级强调色），所有配色、章节、栏目与内容均可按课程主题自由替换。

## 一、创建或修改网站流程

1. **初始化站点目录**：确认目标目录与现有课程资料，保留用户已有文件。将 `assets/study-site/` 的**全部内容**（含 `vendor/mermaid.min.js`）复制到新站点目录，不要在 skill 目录内直接编辑。
2. **配置首页与导航**：修改 `index.html` 中的课程名称、总览卡片与题型分值；在 `site.js` 的 `units` 数组中配置唯一 `id`、标题、图标、星级与相对路径 `unit/<id>.html`。保持界面简洁，不保留多余的英文副标题或分组装饰字样。
3. **用 Markdown 编写各章内容**：在站点 `unit/` 目录下按规范编写 `1.md`、`2.md`……（参考 `assets/study-site/unit/1.md`），然后运行编译脚本批量生成 HTML：
   ```bash
   python "<skill_dir>/scripts/build_unit.py" "<site_dir>/unit"
   ```
4. **内置 10 套差异化布局与创意排版模板**：`assets/study-site/unit/` 内置 10 套在**页眉结构、导航形态、网格布局、表格规范与排版气质**上截然不同的 HTML 模板，编译时可通过 Frontmatter `theme: <名称>` 或命令行 `--theme <名称>` 一键切换：
   - `editorial`（默认，[unit/1.html](./assets/study-site/unit/1.html)）：**现代财经智库风** — 满宽渐变横幅 + 单栏左彩条星级卡片 + 暖象牙纸面
   - `academic-book`（[unit/theme-academic-book.html](./assets/study-site/unit/theme-academic-book.html)）：**学术专著讲义风** — 双细线居中扉页头 + 书签下划线分栏 + 学术三线表 + 宽屏双栏列表 + 全衬线排版
   - `bento-tech`（[unit/theme-bento-tech.html](./assets/study-site/unit/theme-bento-tech.html)）：**极简 Bento 科技看板风** — 圆角悬浮顶栏 + 胶囊分段控制器 + 宽屏双列 Bento 便当网格 + 顶彩条卡片与等宽方块编号
   - `notion-minimal`（[unit/theme-notion-minimal.html](./assets/study-site/unit/theme-notion-minimal.html)）：**极简 Notion 笔记流风** — 彻底去外框卡片，780px 黄金列宽纯白文档流 + 手账荧光笔划重点
   - `night-terminal`（[unit/theme-night-terminal.html](./assets/study-site/unit/theme-night-terminal.html)）：**暗夜终端专注风** — 深海暗色仪表盘 + 发光胶囊导航 + 霓虹光晕卡片与深夜护眼配色
   - `swiss-poster`（[unit/theme-swiss-poster.html](./assets/study-site/unit/theme-swiss-poster.html)）：**瑞士国际主义海报风** — 零圆角 2px 纯黑结构网格 + 瑞士红黑撞色块 + 反白条形小标
   - `cornell-notes`（[unit/theme-cornell-notes.html](./assets/study-site/unit/theme-cornell-notes.html)）：**康奈尔活页笔记风** — 方格纸底纹 + 红色装订双竖线 + 宽屏左线索区/右笔记区双栏结构
   - `newspaper-broadsheet`（[unit/theme-newspaper-broadsheet.html](./assets/study-site/unit/theme-newspaper-broadsheet.html)）：**经典财经大报风** — FT 鲑鱼粉暖报纸底色 + 刊头双线 + 社论分割版面 + 首字下沉
   - `neobrutalism`（[unit/theme-neobrutalism.html](./assets/study-site/unit/theme-neobrutalism.html)）：**新粗野主义卡牌风** — 点阵底纹 + 2.5px 粗黑框 + 实心硬投影 + 撞色弹跳学习卡牌
   - `chinese-ink`（[unit/theme-chinese-ink.html](./assets/study-site/unit/theme-chinese-ink.html)）：**东方宋韵水墨书院风** — 宣纸留白 + 朱砂方印星标 + 双细内框书院卡片 + 竹青浓墨全宋体
   - `header` 与 `.nav-bar-wrap` 默认不吸顶（非 sticky），保障手机端阅读视野。全部功能均 100% 本地离线可用。
5. **验收交付**：核对每个 `units` 路径、原始课件相对路径、Mermaid 图表渲染、平行分栏切换、星级筛选、单题答案展开与默写模式。交付时说明输出目录、打开方式、配色及待核对资料。

## 二、Markdown 模板语法规范（`unit/*.md` → `unit/*.html`）

| Markdown 语法 | 自动渲染样式与交互 |
| :--- | :--- |
| 顶部 `---` YAML Frontmatter | 配置 `id`、`title`、`kicker`、`stars`、`tags`、`materials`（课件原件列表，自动生成 `📄 原始课件` 平行栏） |
| `# 栏目名称`（一级标题） | 自动生成顶部**平行分栏（Tab）**，核心框架与各知识板块平级展示 |
| `## 大标题 ★★★★★`（二级标题） | 自动生成**考点卡片**；识别 `★★★★★`/`★★★★`/`★★★`/`★★` 渲染对应左侧彩条、星级徽章并支持顶部星级筛选 |
| `### 小节标题`（三级标题） | 自动渲染金色左竖条 + 暖色底纹小节标题 |
| `#### 细分标题`（四级标题） | 自动渲染深青色下划线小标题 |
| `**加粗关键词**` | 荧光底纹高亮；点击 **`🧠 默写模式`** 后自动打模糊滤镜，单击单处独立显示/遮盖 |
| `*斜体文字*` | 暖金衬线斜体强调（适合术语、案例举证与备注） |
| `1.` / `-` 列表 | 彩色圆形序号徽章 / 金红三角箭头（`▸`）与嵌套圆点（`•`） |
| `\| 表格 \|` | 深青表头、斑马纹与移动端横向滚动表格 |
| ```` ```mermaid ```` | 离线本地 Mermaid 图表（切换分栏时按需渲染） |
| `> 引用块` | 按语义自动着色：易错/避坑→琥珀框，术语/对照→蓝框，必考/考情→红框，其余→绿框 |
| `:::qa [题型]` ... `---` ... `:::` | 单题独立卡片，带**查看参考答案与采分点 ▼**切换按钮，栏顶自动附带“全部展开答案” |

## 三、模板文件结构

- `scripts/build_unit.py`：零依赖 Python 3 编译器，支持单文件或整目录编译 `unit/*.md` → `unit/*.html`。
- `assets/study-site/index.html` / `index.css` / `site.js`：站点外壳、复习总览页、折叠侧栏与 `localStorage` 进度同步。
- `assets/study-site/unit.css` / `unit.js`：平行分栏、星级筛选、记忆排版、`🧠 默写模式`、单题自测、Mermaid 按需渲染与 PDF 懒加载。
- `assets/study-site/vendor/mermaid.min.js`：本地离线 Mermaid 渲染库。
- `assets/study-site/unit/1.md` / `1.html`：完整示例章节（可直接作为新章模板复制修改）。
