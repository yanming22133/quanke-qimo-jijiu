# Exam Blueprint (Chinese courses)

Reusable blueprint for mock papers. Copy the blocks below and fill in the Step 0 values.

## 1. Exam brief (page 1 of summary + README)

```markdown
| 项目 | 内容 |
|---|---|
| 考试时间 | [日期]，[时长] |
| 题型分值 | [题型 × 数量 × 分值] |
| 考试范围 | [章节范围]；[排除章节] 不考 |
| 命题依据 | 教材 / PPT / 两者 / 往年题（按本课实际填写） |
| 情报等级 | 有录音 / 只有大纲 / 只有往年题 / 只有 PPT / 无（影响可信度） |
| 重点 | [重点章节]；[次重点] 考基础 |
| 术语 | [教材说法]＝[课件说法]，括号互注 |
```

## 2. Paper skeleton

```latex
\begin{center}
{\LARGE\bfseries 《课程名》期末模拟试卷 X}\\[6pt]
{\small 考试时间：[时长]\qquad 满分：[满分]\qquad [开卷/闭卷]}\\[2pt]
{\footnotesize 覆盖[章节范围]}
\end{center}
\hrule
\vspace{6pt}
姓名：\underline{\hspace{3cm}}\quad 学号：\underline{\hspace{3.5cm}}\quad 得分：\underline{\hspace{2cm}}
```

## 3. Answer-space table

| 题型 | 留白 | 写法 |
|---|---|---|
| 单选/判断 | 无 | 选项 `A. …\quad B. …` |
| 名词解释 | 3 cm | `\vspace{3cm}` |
| 简答 10 分 | 3--4 cm | `\vspace{3.2cm}` |
| 计算/证明 | 6--8 cm | `\vspace{7cm}` |
| 论述 25 分 | 9--12 cm | `\vspace{10cm}` |
| 案例 30 分（3 小问） | 每问 3--4 cm | `\vspace{3.2cm}` ×3 |

## 4. Case question template

```latex
\newpage
\section*{四、案例分析题（30 分）}
\begin{infobox}[案例：一句话标题]
（500--900 字，自包含：背景、关键事实与数字、当前困境。学生不需要教材。）
\end{infobox}

请回答：
\begin{enumerate}
\item （10 分）用〔框架 A〕分析……
\vspace{3.2cm}
\item （10 分）用〔框架 B〕说明……
\vspace{3.2cm}
\item （10 分）给出两条建议并说明依据。
\vspace{3.2cm}
\end{enumerate}
```

## 5. Calculation question template

```latex
\section*{三、计算题（共 30 分）}
\begin{enumerate}
\item （15 分）某项目初始投资 1000 万元，未来三年每年末现金流 400 万元，
折现率 10\%。求净现值，并判断是否可行。
\vspace{12cm}
\end{enumerate}
```

Answer file: 公式 30% / 代入 30% / 结果 30% / 单位与结论 10%。

## 6. Programming question template

```latex
\section*{四、编程题（共 20 分）}
\textbf{题目}：实现函数 \texttt{solve(nums, target)}，返回两数之和的下标。
\textbf{输入}：nums = [2,7,11,15], target = 9
\textbf{输出}：[0,1]
\textbf{约束}：2 ≤ len(nums) ≤ 10^4；只存在一个答案；不得重复使用同一元素。
\textbf{要求}：写出完整函数，并说明时间复杂度。
\vspace{1cm}
% 答题区：20--30 行；若需代码框，用 \begin{verbatim} 或带行号的 lstlisting
\vspace{8cm}
```

评分：正确性 50%（含边界）/ 复杂度 20% / 结构 20% / 清晰 10%。

## 7. Answer template

```latex
\subsection*{1. 第一问（10 分）}
\begin{notebox}[评分点]
结论 2 分；框架要点 4 分（每点 1 分）；结合案例 3 分；表述 1 分。
\end{notebox}
```

## 8. Difficulty ladder (optional D/E)

| 维度 | A/B/C 基础 | D 提高 | E 挑战 |
|---|---|---|---|
| 题干信息 | 完整 | 有干扰项 | 冲突或缺失，要自己假设 |
| 使用框架 | 1 个 | 2 个，需比较 | 3 个，需说明适用边界 |
| 设问动词 | 说明/分析 | 比较/应用 | 评价/决策/预测 |
| 答案要求 | 要点 | 论证 | 反方 + 取舍 + 落地 |

题型对应：

| 题型 | A/B/C | D | E |
|---|---|---|---|
| 单选 | 识记 | 辨析易混 | 情境判断（两个选项都像） |
| 简答 | 复述 | 比较 + 条件 | 开放整合，无唯一答案 |
| 论述 | 单框架 | 双框架 + 证据 | 立论 + 反驳 + 边界 |
| 案例 | 信息完整，3 小问 | 信息冲突，要判断 | 信息缺失，要假设 + 决策 + 风险 |

规则：D/E 不得超出考试范围；难度来自“整合与判断”，不是来自偏题、怪题或模糊表述。

## 9. Delivery checklist

- [ ] 每道大题后有 `\vspace`，且大小与题型匹配
- [ ] 论述/案例各自 `\newpage` 起页，案例框与问题不分页
- [ ] 卷面无“参考答案/评分标准”字样
- [ ] 答案文件逐问给分点，而非整段范文
- [ ] 三套卷考点不重叠；案例可复用但角度不同，并在 README 列表
- [ ] 考试范围排除章节写在首页
- [ ] 命题依据（教材/PPT/两者/往年题）写在首页，不把某门课的规则当成通用规则
- [ ] 术语以命题依据为准，另一说法括号互注
- [ ] 目录结构：`01_知识点汇总` … `NN_模拟卷`、`课本OCR`、`_tex源文件`、`00_说明.md`
