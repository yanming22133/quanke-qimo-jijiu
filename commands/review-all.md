---
name: review-all
description: 一键生成全套期末复习资料（知识点汇总 + 章节练习 + 模拟卷与答案 + 考前速查卡 + 倒计时复习计划 + 离线交互复习网站）
argument-hint: "<课程材料目录> [考试日期] [模拟卷套数: 默认5]"
---

# `/review-all` · 全套期末复习资料一键生成

按顺序协同调用 `skills/latex-review-materials/SKILL.md` 与 `skills/course-review-template/SKILL.md`，基于同一份 Step 0 考试情报，交付**打印刷卷 + 电子屏刷背**全套资料。

## 执行步骤

1. **Step 0 考试情报提取**：先读取课程目录中的录音/纪要、大纲、往年题与课件，补齐缺失的关键项（题型分值、范围与排除章节、命题依据、考试日期），一次性向用户确认。
2. **全量资料精读**：读取所有有效章节资料（PDF 优先 `pdftotext`，扫描版按需 OCR，跳过明确不考的章节）。
3. **LaTeX 打印套件**（按 `skills/latex-review-materials/SKILL.md`）：
   - `01_知识点汇总.pdf`（含 TikZ 图、对比表、易错点）
   - `02_章节练习.pdf`
   - `03–12_模拟卷A–E.pdf` 及独立评分点答案册（留足答题空间，跑 `quality_check.py` 与 `exam_lint.py`）
   - `13_考前速查卡.pdf`（一页纸）
   - `14_复习计划.pdf` + `.md` + `.plan.json`（若提供考试日期，跑 `references/make_plan.py`）
4. **离线交互复习网站**（按 `skills/course-review-template/SKILL.md`）：
   - 在目标目录生成 `index.html`、`site.js`、`unit/*.md` 并通过 `build_unit.py` 编译为 `unit/*.html`
   - 包含平行分栏、星级筛选、离线 Mermaid 图、单题独立切换答案、`🧠 默写模式` 与 `📄 原始课件` 栏。
5. **统一验收交付**：汇报全部生成文件路径、未确认的默认假设及待核对项。
