# Exam Blueprint (Chinese courses)

Reusable blueprint for mock papers. Copy the blocks below and fill in the Step 0 values.

## 0. Intake card (ask before generating)

Copy this card into the chat when the materials do not answer these questions. Ask at most 6 at a time.

```markdown
为了生成对味的资料，先确认 6 件事（不确定就写“不知道”，我按默认来）：

1. 题型与分值：选择__道×__分；简答__道×__分；计算__道×__分；
   编程__道×__分；案例__道×__分；考试时长__分钟
2. 范围：考第__章到第__章；不考第__章
3. 命题依据：教材 / PPT / 两者 / 往年题
4. 你哪几章最弱：______（会多出题、多解释）
5. 还剩几天：__ 天；每天大概 __ 小时
6. 想要几套卷：3 套 / 5 套（后两套提高+挑战）；答案要多细：只给答案 / 给步骤 / 评分点+易错点

默认：3 套、评分点+关键步骤、中文、不做 OCR。
```

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
| 计算 | 8--12 cm | `\vspace{10cm}` |
| 证明 | 10--12 cm | `\vspace{11cm}` |
| 画图/设计 | 半页（坐标/图框） | `\vspace{12cm}` |
| 编程 | 20--30 行 + 复杂度 | `\vspace{14cm}` |
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

难度只能来自“信息完整前提下的思考更深”，不能靠删条件、制造矛盾或模糊设问。

先分清三类：

| 类型 | 特征 | 例子 |
|---|---|---|
| 基础题 | 单一概念、一步到位 | 写出波特的三种基本战略 |
| 难题 | 多概念联动、多步推理、跨章整合 | 用五力 + 价值链判断该不该进入某行业 |
| 易错题 | 信息完整，但含常见误区或边界条件 | 给两项业务占比，判断相关约束型还是主导业务型 |

难度阶梯（题干始终完整可解）：

| 维度 | A/B/C 基础 | D 提高 | E 挑战 |
|---|---|---|---|
| 知识跨度 | 单点 | 2–3 个概念联动 | 跨章整合 |
| 推理步数 | 1–2 步 | 3–4 步 | 多步 + 需说明决策规则 |
| 设问动词 | 说明/分析 | 比较/应用 | 评价/决策/预测 |
| 干扰强度 | 无 | 选项或数据里有相似概念（仍可解） | 两个框架都说得通，需论证取舍 |
| 易错点 | 无 | 1 个经典误区 | 2–3 个边界条件 |

题型对应：

| 题型 | A/B/C | D | E |
|---|---|---|---|
| 单选 | 识记 | 辨析易混 | 情境判断（两个选项都像） |
| 简答 | 复述 | 比较 + 条件 | 开放整合，无唯一答案 |
| 论述 | 单框架 | 双框架 + 证据 | 立论 + 反驳 + 边界 |
| 案例 | 信息完整，3 小问 | 信息完整 + 一个干扰数据 | 信息完整 + 约束下决策 + 风险 |
| 计算 | 单步代入 | 多步/多期（条件给全） | 自己选模型 + 讨论假设 |
| 编程 | 直接实现 | 加约束/优化 | 边界 + 复杂度 + 证明 |

规则：
- 题干必须自足，条件、数据、约束齐全；不删条件、不制造矛盾、不模糊设问。
- 难度来自概念联动、推理链、跨章整合、评价决策、易错点。
- D/E 不得超出考试范围；易错 ≠ 超纲 ≠ 缺条件。

## 9. Delivery checklist

- [ ] 每道大题后有 `\vspace`（论述/计算/编程/案例），且大小与题型匹配
- [ ] 大题板块各自 `\newpage` 起页，案例框与问题不分页
- [ ] 卷面无“参考答案/评分标准”字样
- [ ] 答案文件逐问给分点，而非整段范文
- [ ] 前三套考点不重叠；D/E 同范围提难度；案例可复用但角度不同，并在 README 列表
- [ ] 考试范围排除章节写在首页
- [ ] 命题依据（教材/PPT/两者/往年题）写在首页，不把某门课的规则当成通用规则
- [ ] 术语以命题依据为准，另一说法括号互注
- [ ] 目录结构：`01_知识点汇总` … `NN_模拟卷`、`课本OCR`、`_tex源文件`、`00_说明.md`
