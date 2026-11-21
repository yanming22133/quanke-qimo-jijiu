---
name: review-exams
description: 单独生成「章节练习 PDF」和/或「模拟卷 A–E + 独立评分答案册 PDF」
argument-hint: "<课程材料目录> [套数: A-C 或 A-E，默认3套] [--no-exercises]"
---

# `/review-exams` · 单独生成模拟卷与章节练习

仅执行 `skills/latex-review-materials/SKILL.md` 中的出题与模考卷模块，适合已经复习完知识点、需要高仿真限时刷题的场景。

## 执行步骤

1. **提取真实题型与分值**：先从录音/大纲/真题提取真实卷面结构（题型、题量、分值、大题形态：计算/证明/画图/编程/案例/材料分析）；缺失则先询问用户，不盲猜。
2. **生成试卷与独立答案**：
   - 除非指定 `--no-exercises`，先生成 `02_章节练习.pdf`（分章巩固，答案附后）。
   - 生成指定套数的 `模拟卷*.pdf`（**仅题目 + 规范留白 + 空白草稿/画图区，绝不混入答案**）与独立 `模拟卷*_答案.pdf`（选择题逐项解析、大题分步采分点、计算题 Python/sympy 验算、案例题 500–900 字自包含）。
3. **质量闸门**：运行 `references/quality_check.py`（检查留白与格式）和 `references/exam_lint.py`（跨卷查重 >0.85 报警与难度分布检查），编译两遍 `xelatex` 并交付。
