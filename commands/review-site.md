---
name: review-site
description: 单独生成 Markdown 驱动的离线交互复习网站（平行分栏、星级筛选、Mermaid 流程图、单题答案切换、默写模式、原始课件预览）
argument-hint: "<课程材料目录> [输出目录，默认当前目录]"
---

# `/review-site` · 单独生成离线交互复习网站

调用 `skills/course-review-template/SKILL.md`（或 `skills/latex-review-materials/references/web-site-builder.md`），仅产出零后端、手机与电脑均可离线打开的 HTML 静态学习网站。

## 执行步骤

1. **情报与范围确认**：提取考试范围、排除章节、命题重点与星级权重。
2. **并行章节深度总结**：按章节精读全部课程材料与案例，每章编写标准 `unit/<id>.md`：
   - `# 栏目名` 拆分平行板块（首栏为 `📋 核心考点总览`，其余按知识模块平行展开，不要堆在一个长页里）
   - `## 标题 ★★★★★` 标注考点重要星级（支持顶部 `★★★★+` / `★★★★★` 筛选）
   - 全章框架图与核心模型图使用 ```` ```mermaid ```` 绘制
   - 自测题使用 `:::qa [题型] ... --- ... :::` 生成单题独立答案切换按钮
   - Frontmatter `materials:` 挂载原始 PDF/Word 课件，自动生成平行 `📄 原始课件` 栏。
3. **一键编译与验收**：
   - 复制模板外壳（`index.html`、`index.css`、`site.js`、`unit.css`、`unit.js` 及本地 `vendor/mermaid.min.js`）。
   - 运行 `python build_unit.py "<site_dir>/unit"` 编译全部 `.md` → `.html`。
   - 核验所有相对链接、Mermaid 渲染、单题答案展开与 `🧠 默写模式`（模糊加粗关键词、单击单处显示），交付入口 `index.html`。
