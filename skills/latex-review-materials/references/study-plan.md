# Study plan (spaced repetition)

Generate `复习计划.pdf` when the exam is within 14 days. It turns the materials into a daily schedule.

## Inputs

- 考试日期、剩余天数、每天可用小时
- 红点知识点（来自复盘或自述）
- 已有资料：知识点汇总 / 练习 / 模拟卷 / 错题本

## Standard schedule (7+ days)

| 时间 | 内容 | 资料 |
|---|---|---|
| Day 1 | 红点 1–2 个：补丁 + 基础题 | 知识点补丁、章节练习 |
| Day 2 | 同知识点变式题 | 补弱卷 Part B |
| Day 3 | 复习 Day 1–2 + 错题重做 | 错题本 |
| Day 5 | 混合限时卷（1 套） | 模拟卷 A/B |
| Day 7 | 错题本 + 综合题 | 补弱卷 Part C |
| 考前 1 天 | 速查卡 + 一套限时卷 | 考前速查卡、模拟卷 E |
| 考前一晚 | 只看错题本与速查卡 | — |

## Compressed (≤3 days)

| 时间 | 内容 |
|---|---|
| Day 1 | 全部红点补丁 + 1 套基础卷 |
| Day 2 | 变式题 + 错题重做 |
| Day 3 | 1 套限时卷 + 速查卡 |

## Rules

- 间隔重复：同一知识点在 Day 1 / 3 / 7 出现三次，间隔逐渐拉长。
- 每天总量不超过可用小时；宁可少，不要排满。
- “时间不够”型错因 → 安排限时训练，不增加题量。
- 计划表留“完成（□）”，方便打印后打勾。

## Template

```latex
\section*{复习计划（__ 月 __ 日 — __ 月 __ 日）}
\begin{center}
\begin{tabular}{|c|c|p{7cm}|c|}
\hline
日期 & 时段 & 内容 & 完成 \\
\hline
 & & & $\square$ \\
\hline
\end{tabular}
\end{center}
```
