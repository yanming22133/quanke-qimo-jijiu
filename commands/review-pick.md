---
name: review-pick
description: 自由组合选择任意几类学习资料（如：知识点+复习网站、模拟卷+复习计划等），共享同一份考情情报按需生成
argument-hint: "<课程材料目录> [模块组合，例如: notes,site 或 exams,plan,card]"
---

# `/review-pick` · 按需自由组合生成任意几类资料

共享同一份 Step 0 考试情报与资料精读结果，只生成用户点选的 1 类或 N 类交付物，避免重复读资料或生成不需要的文件。

## 可选模块清单（可单选、多选或全选）

| 模块代号 | 对应产物 | 适用场景 |
| :--- | :--- | :--- |
| `notes` | `01_知识点汇总.pdf`（含 TikZ 图与对比表） | 打印背诵、系统梳理 |
| `exercises` | `02_章节练习.pdf` | 学完一章立刻刷题巩固 |
| `exams` | `模拟卷 A–C / A–E.pdf` + 独立评分答案册 | 考前仿真限时模考 |
| `site` | 离线交互复习网站（`index.html` + `unit/*.md/.html`） | 手机/电脑刷背、默写模式、查阅原课件 |
| `card` | `13_考前速查卡.pdf`（1 页 A4） | 考前 1–2 天极限速记 |
| `plan` | `14_复习计划.pdf` + `.md` + `.plan.json` | 倒计时每日排期与间隔重复 |
| `fix` | `复盘报告.pdf` + `补弱卷.pdf` + `错题本.pdf` | 刷卷后查漏补缺 |

## 执行步骤

1. **确认组合**：如果用户未在参数中列出模块代号，先用简明多选清单让用户勾选本次要生成的模块组合（也可直接回复“全部”切换为 `/review-all`）。
2. **统一 Step 0 考情提取与资料精读**（只做一次，供所有选中模块复用）。
3. **按所选模块并行/分步产出**：
   - 含 `notes` / `exercises` / `exams` / `card` / `plan` / `fix` → 调用 `skills/latex-review-materials/SKILL.md` 对应章节与脚本；
   - 含 `site` → 调用 `skills/course-review-template/SKILL.md` 与 `build_unit.py`。
4. **交付清单**：汇总本次实际生成的全部文件及打开方式。
