---
name: review-plan
description: 单独生成「倒计时每日复习计划 PDF/MD/JSON」与可选「考前速查卡 PDF」
argument-hint: "<考试日期 YYYY-MM-DD> <每天可用小时> [薄弱章节] [--with-card]"
---

# `/review-plan` · 单独生成倒计时复习计划（+ 可选速查卡）

仅执行 `skills/latex-review-materials/references/study-plan.md` 与 `references/make_plan.py` 排期流程，适合临考快速制定可执行日程。

## 执行步骤

1. **收集排期参数**：确认考试日期、每天可用小时、各章考试权重、当前掌握度（红/黄/绿）与目标分数。
2. **构建配置并生成计划**：
   - 参照 `references/templates/plan.example.json` 生成课程 `plan.json`。
   - 运行 `python references/make_plan.py plan.json`，产出 `复习计划.md`、`复习计划.tex`、`复习计划.plan.json` 并编译为 `14_复习计划.pdf`（支持 14/10/7/5/3/2/1 天骨架，1 天自动切急救单，含 D+1/D+3/D+7 间隔回顾与 15% 缓冲）。
3. **可选速查卡**：若指定 `--with-card` 且提供了课程材料，额外生成 1 页 A4 `13_考前速查卡.pdf`。
