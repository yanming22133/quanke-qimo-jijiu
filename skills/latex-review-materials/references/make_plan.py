# -*- coding: utf-8 -*-
"""Countdown study-plan generator for exam review.

Usage:
    python make_plan.py --input plan.json --out 复习计划
    python make_plan.py --input plan.json --out 复习计划 --today 2026-11-18

Input JSON:
{
  "course": "管理系统工程",
  "exam_date": "2026-11-22",
  "hours_per_day": 6,
  "target_score": 85,
  "topics": [
    {"name": "ISM 规范方法", "weight": 5, "level": "red", "type": "calc",
     "materials": "知识点汇总 ch3；全真卷 3 综合题"}
  ]
}

Outputs:
    复习计划.md
    复习计划.tex
    plan.json   (normalized input + computed schedule)
"""
import argparse
import json
import math
import os
import sys
from datetime import date, datetime, timedelta

LEVEL_MULT = {"red": 1.6, "yellow": 1.2, "green": 0.7}
LEVEL_CN = {"red": "红", "yellow": "黄", "green": "绿"}
WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def esc_tex(s: str) -> str:
    """Escape plain text for LaTeX (no math expected)."""
    s = str(s)
    for a, b in [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
    ]:
        s = s.replace(a, b)
    return s


def fmt_date(d: date) -> str:
    return "%d-%02d" % (d.month, d.day)


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def normalize_topics(raw):
    topics = []
    for t in raw:
        name = str(t.get("name", "")).strip()
        if not name:
            continue
        weight = float(t.get("weight", 3))
        level = str(t.get("level", "yellow")).lower()
        if level not in LEVEL_MULT:
            level = "yellow"
        topics.append({
            "name": name,
            "weight": max(0.1, weight),
            "level": level,
            "type": str(t.get("type", "mixed")),
            "materials": str(t.get("materials", "")).strip(),
            "score": max(0.1, weight) * LEVEL_MULT[level],
        })
    if not topics:
        topics = [{
            "name": "核心考点", "weight": 3, "level": "yellow",
            "type": "mixed", "materials": "知识点汇总 + 章节练习",
            "score": 3 * LEVEL_MULT["yellow"],
        }]
    total = sum(t["score"] for t in topics)
    for t in topics:
        t["share"] = t["score"] / total
    return topics


def build_session_plan(topics, content_days, hours_per_day):
    """Return a list of day dicts for the content phase.

    Each day: {am, pm, eve} where each is a dict {text, minutes, kind}.
    Guarantees every topic appears at least once when there are enough slots;
    low-weight topics that do not fit are merged into one "概念速过" session.
    """
    total_hours = content_days * hours_per_day * 0.85
    for t in topics:
        t["hours"] = max(0.8, total_hours * t["share"])

    slots = content_days * (2 if hours_per_day > 3 else 1)
    ranked = sorted(topics, key=lambda x: -x["score"])
    primary = []
    deferred = []

    if len(ranked) > slots:
        keep = ranked[:slots]
        deferred = ranked[slots:]
        for t in keep:
            primary.append({"topic": t, "kind": "learn" if t["level"] != "green" else "practice"})
    else:
        for t in ranked:
            primary.append({"topic": t, "kind": "learn" if t["level"] != "green" else "practice"})

    # Extra practice slots: red topics first, max 3 sessions per topic.
    counts = {}
    for s in primary:
        counts[s["topic"]["name"]] = counts.get(s["topic"]["name"], 0) + 1
    extra = []
    remaining = max(0, slots - len(primary))
    i = 0
    guard = 0
    while remaining > 0 and guard < 100:
        guard += 1
        t = ranked[i % len(ranked)]
        i += 1
        if counts.get(t["name"], 0) >= 3:
            continue
        kind = "timed" if t["level"] == "red" and counts.get(t["name"], 0) >= 1 else "practice"
        extra.append({"topic": t, "kind": kind})
        counts[t["name"]] = counts.get(t["name"], 0) + 1
        remaining -= 1
    if remaining > 0:
        # Fallback: fill with a mixed review/error-fix block.
        for _ in range(remaining):
            extra.append({"topic": ranked[0], "kind": "review"})

    ordered = primary + extra
    # Interleave so the same topic does not run 3 times in a row.
    final, pool = [], ordered[:]
    last, run = None, 0
    while pool:
        pick = None
        for j, s in enumerate(pool):
            if s["topic"]["name"] != last or run < 2:
                pick = j
                break
        if pick is None:
            pick = 0
        s = pool.pop(pick)
        if s["topic"]["name"] == last:
            run += 1
        else:
            last, run = s["topic"]["name"], 1
        final.append(s)

    # Assign to days: AM + PM (or only AM if hours <= 3).
    per_day = 2 if hours_per_day > 3 else 1
    days = []
    idx = 0
    for d in range(content_days):
        chunk = final[idx:idx + per_day]
        idx += per_day
        if not chunk:
            chunk = [{"topic": ranked[0], "kind": "review"}]
        days.append({
            "am": chunk[0],
            "pm": chunk[1] if len(chunk) > 1 else None,
            "eve": None,
        })
    return days, deferred


def session_text(s, phase="content"):
    t = s["topic"]
    kind = s["kind"]
    name = t["name"]
    mat = t["materials"] or "对应章节 + 练习"
    if kind == "learn":
        return "主攻「%s」：看知识点汇总 → 画 A4 结构图 → 做 3 道例题 + 5 道基础题。资料：%s" % (name, mat)
    if kind == "practice":
        return "练「%s」：章节练习/变式题 15–20 道，红笔标错因。资料：%s" % (name, mat)
    if kind == "timed":
        return "限时「%s」：60–90 分钟做一组综合题/半套卷，做完立刻订正；剩余时间重做错题。资料：%s" % (name, mat)
    if kind == "review":
        return "回顾「%s」：遮住答案复述结构图/公式，只看错题。资料：%s" % (name, mat)
    return "复习「%s」。资料：%s" % (name, mat)


def make_normal_plan(course, today, exam, days_left, hours, target, topics):
    """Build the full plan for days_left >= 2."""
    # The day before the exam is review-only.
    review_day = exam - timedelta(days=1)
    study_dates = [today + timedelta(days=i) for i in range((review_day - today).days)]
    n_study = len(study_dates)
    if n_study < 1:
        study_dates = [today]
        n_study = 1

    # Reserve the last study day(s) for timed mock + correction.
    if n_study >= 8:
        mock_days = 2
    elif n_study >= 2:
        mock_days = 1
    else:
        mock_days = 0
    content_days = max(1, n_study - mock_days)

    content, deferred = build_session_plan(topics, content_days, hours)

    # Assemble day records.
    days = []
    for i, d in enumerate(study_dates):
        rec = {"date": d, "countdown": (exam - d).days, "am": None, "pm": None,
               "eve": None, "kind": "content", "note": ""}
        if i < len(content):
            am = content[i]["am"]
            pm = content[i]["pm"]
            rec["am"] = session_text(am)
            rec["topics"] = [am["topic"]["name"]]
            if pm:
                rec["pm"] = session_text(pm)
                rec["topics"].append(pm["topic"]["name"])
            rec["eve"] = "间隔复习：今天的主攻点，各 10 分钟遮住答案复述；错题本补 3 条。"
        else:
            rec["kind"] = "mock"
        days.append(rec)

    # Mark the last `mock_days` study days as mock days, but keep content on earlier days.
    for k in range(mock_days):
        idx = n_study - 1 - k
        if idx < 0:
            continue
        days[idx]["kind"] = "mock"
        days[idx]["am"] = "全真卷限时：按考试时间 120 分钟做一套；时间不够做半套 90 分钟，中途不看答案。"
        days[idx]["pm"] = "对答案 + 订正：每道错题写「错因 / 正确思路 / 下次怎么避免」。"
        days[idx]["eve"] = "错题本整理：只留最高频的 5 条；间隔复习今天错的知识点。"

    # Review day.
    days.append({
        "date": review_day, "countdown": (exam - review_day).days,
        "am": "速查卡：公式、答题模板、易错点，遮住自己复述一遍。",
        "pm": "错题本：只看错题，不做新题；把反复错的 3 条抄到一张纸上。",
        "eve": "半套卷（只做基础题）保持手感；23:00 前睡。",
        "kind": "review", "note": "不开新章",
    })

    # 2 days left (only one study day): content in the morning + timed mock in the afternoon.
    if n_study == 1:
        rec = days[0]
        names = "、".join(t["name"] for t in sorted(topics, key=lambda x: -x["score"]))
        rec["kind"] = "mixed"
        rec["am"] = "速过高频点：%s；每个点看定义/公式 + 1 道例题，只抓最可能考的。" % names
        rec["pm"] = "全真卷限时：整套约 120 分钟（时间不够做半套 90 分钟），中途不看答案。"
        rec["eve"] = "对答案 + 订正：每道错题写「错因 / 正确思路」；错题本只留 5 条。"

    # Add spaced review to EVE blocks for earlier topics.
    # Simple: EVE already says review; add the specific topic names of the last 1-2 days.
    for i, rec in enumerate(days):
        if rec["kind"] != "content":
            continue
        prev = list(rec.get("topics", []))
        for off in (1, 3, 7):
            j = i - off
            if 0 <= j < len(days) and days[j]["kind"] == "content":
                prev.extend(days[j].get("topics", []))
        if not prev:
            prev = rec.get("topics", [])
        # de-duplicate while keeping order
        seen = set()
        uniq = []
        for x in prev:
            if x not in seen:
                seen.add(x)
                uniq.append(x)
        if uniq:
            rec["eve"] = "间隔复习：%s；各 10 分钟遮住答案复述；错题本补 3 条。" % "、".join(uniq)

    if deferred:
        names = "、".join(t["name"] for t in deferred)
        for t in deferred:
            t["deferred"] = True
        if days and days[0].get("eve"):
            days[0]["eve"] += " 其余：%s 只看速查卡/定义，各 10 分钟。" % names

    # Allocate minutes per block.
    total_min = int(hours * 60)
    if total_min <= 180:
        am_min, pm_min, eve_min = int(total_min * 0.6), 0, int(total_min * 0.4)
    else:
        am_min = int(total_min * 0.4)
        pm_min = int(total_min * 0.35)
        eve_min = total_min - am_min - pm_min
    for rec in days:
        rec["minutes"] = {"am": am_min, "pm": pm_min, "eve": eve_min}

    return days


def make_one_day_plan(course, today, exam, hours):
    total = int(hours * 60)
    return [{
        "date": today, "countdown": (exam - today).days,
        "am": "速查卡 + 错题本：只看最高频的公式、模板、易错点（%d 分钟）。" % int(total * 0.4),
        "pm": "半套卷或 1 套基础卷：计时，做完立刻订正（%d 分钟）。" % int(total * 0.4),
        "eve": "只看错题 + 公式；不做新题；早睡（%d 分钟）。" % int(total * 0.2),
        "kind": "review", "note": "最后一天，不开新章",
        "minutes": {"am": int(total * 0.4), "pm": int(total * 0.4), "eve": int(total * 0.2)},
    }]


def render_markdown(course, today, exam, days_left, hours, target, topics, days):
    L = []
    L.append("# %s · 复习计划" % course)
    L.append("")
    L.append("- 考试：%s（%s）" % (exam.isoformat(), WEEKDAY_CN[exam.weekday()]))
    L.append("- 今天：%s" % today.isoformat())
    L.append("- 还剩：**%d 天**" % days_left)
    L.append("- 每天可用：**%g 小时**" % hours)
    if target:
        L.append("- 目标分：**%g**" % target)
    L.append("")
    L.append("## 红黄绿清单")
    L.append("")
    L.append("| 知识点 | 权重 | 掌握度 | 目标 h | 资料 |")
    L.append("|---|---:|---|---:|---|")
    for t in sorted(topics, key=lambda x: -x["score"]):
        mat = t["materials"] + ("（只进速查）" if t.get("deferred") else "")
        L.append("| %s | %g | %s | %.1f | %s |" % (
            t["name"], t["weight"], LEVEL_CN[t["level"]], t.get("hours", 0), mat))
    L.append("")
    L.append("> 目标 h 是按权重分的目标总量；实际以每日 block 为准，红点优先。")
    L.append("## 每日清单")
    L.append("")
    for i, rec in enumerate(days):
        L.append("### Day %d · %s（还剩 %d 天）" % (i + 1, fmt_date(rec["date"]), rec["countdown"]))
        L.append("")
        for key, label in (("am", "上午"), ("pm", "下午"), ("eve", "晚上")):
            if rec.get(key):
                m = rec.get("minutes", {}).get(key, 0)
                L.append("- [ ] %s %dmin｜%s" % (label, m, rec[key]))
        if rec.get("note"):
            L.append("- 注：%s" % rec["note"])
        L.append("")
    L.append("## 执行规则")
    L.append("")
    L.append("1. 每天结束前 10 分钟做 3 问自测：能画结构图吗？错因是什么？明天 3 个问题？")
    L.append("2. 某天没完成，不要第二天双倍补；删掉优先级最低的 1 个 block。")
    L.append("3. 模拟卷低于 70%：第二天插入 2 个红点补弱，不要立刻再刷一套。")
    L.append("4. 最后一天不开新章，只看速查卡和错题。")
    L.append("")
    return "\n".join(L)


def render_latex(course, today, exam, days_left, hours, target, topics, days):
    L = []
    L.append(r"\documentclass[11pt,a4paper,fontset=fandol]{ctexart}")
    L.append(r"\usepackage[margin=1.8cm]{geometry}")
    L.append(r"\usepackage{amsmath,amssymb}")
    L.append(r"\usepackage{booktabs,longtable,array}")
    L.append(r"\usepackage[table]{xcolor}")
    L.append(r"\usepackage{tcolorbox}")
    L.append(r"\tcbuselibrary{skins,breakable}")
    L.append(r"\usepackage{enumitem}")
    L.append(r"\usepackage{fancyhdr}")
    L.append(r"\setlength{\headheight}{14pt}")
    L.append(r"\pagestyle{fancy}\fancyhf{}")
    L.append(r"\fancyhead[L]{%s}\fancyhead[R]{复习计划}" % esc_tex(course))
    L.append(r"\fancyfoot[C]{\thepage}")
    L.append(r"\renewcommand{\headrulewidth}{0.4pt}")
    L.append(r"\definecolor{ink}{RGB}{30,35,45}")
    L.append(r"\definecolor{accent}{RGB}{20,90,160}")
    L.append(r"\definecolor{warm}{RGB}{200,95,30}")
    L.append(r"\definecolor{soft}{RGB}{245,247,250}")
    L.append(r"\newtcolorbox{daybox}[1]{colback=soft,colframe=accent!70,fonttitle=\bfseries,title=#1,breakable,enhanced,boxrule=0.6pt,arc=2pt,left=6pt,right=6pt,top=4pt,bottom=4pt}")
    L.append(r"\newcommand{\done}{\raisebox{-1pt}{$\square$}}")
    L.append(r"\begin{document}")
    L.append(r"\begin{center}")
    L.append(r"{\LARGE\bfseries %s · 复习计划}\\[4pt]" % esc_tex(course))
    L.append(r"{\large 考试 %s（%s）\quad 还剩 \textbf{%d} 天\quad 每天 %g 小时%s}\\[2pt]" % (
        exam.isoformat(), WEEKDAY_CN[exam.weekday()], days_left, hours,
        (r"\quad 目标 %g 分" % target) if target else ""))
    L.append(r"{\small 生成于 %s}" % today.isoformat())
    L.append(r"\end{center}")
    L.append(r"\vspace{-2mm}")
    # Divider
    L.append(r"\vspace{1mm}\hrule\vspace{2mm}")
    # Topic table
    L.append(r"\section*{一、红黄绿清单}")
    L.append(r"\begin{center}\small\begin{tabular}{p{4.2cm}cp{1.4cm}p{1.6cm}p{7.2cm}}")
    L.append(r"\toprule 知识点 & 权重 & 掌握度 & 目标 h & 资料 \\ \midrule")
    for t in sorted(topics, key=lambda x: -x["score"]):
        color = {"red": "red!70", "yellow": "orange!80", "green": "green!55"}[t["level"]]
        mat = t["materials"] + ("（只进速查）" if t.get("deferred") else "")
        L.append(r"%s & %g & \textcolor{%s}{%s} & %.1f & %s \\" % (
            esc_tex(t["name"]), t["weight"], color, LEVEL_CN[t["level"]],
            t.get("hours", 0), esc_tex(mat)))
    L.append(r"\bottomrule\end{tabular}\end{center}")
    L.append(r"{\small\color{gray} 目标 h 是按权重分的目标总量；实际以每日 block 为准，红点优先。}")
    # Day cards
    L.append(r"\section*{二、每日清单}")
    for i, rec in enumerate(days):
        title = "Day %d · %s（还剩 %d 天）" % (i + 1, fmt_date(rec["date"]), rec["countdown"])
        L.append(r"\begin{daybox}{%s}" % title)
        for key, label in (("am", "上午"), ("pm", "下午"), ("eve", "晚上")):
            if rec.get(key):
                m = rec.get("minutes", {}).get(key, 0)
                L.append(r"\textbf{%s %dmin}\hfill\done\\[1pt]" % (label, m))
                L.append(r"%s\par\vspace{1.5mm}" % esc_tex(rec[key]))
        if rec.get("note"):
            L.append(r"{\small\color{warm}注：%s}" % esc_tex(rec["note"]))
        L.append(r"\end{daybox}")
    # Rules
    L.append(r"\section*{三、执行规则}")
    L.append(r"\begin{enumerate}[nosep]")
    L.append(r"\item 每天结束前 10 分钟做 3 问自测：能画结构图吗？错因是什么？明天 3 个问题？")
    L.append(r"\item 某天没完成，不要第二天双倍补；删掉优先级最低的 1 个 block。")
    L.append(r"\item 模拟卷低于 70\%：第二天插入 2 个红点补弱，不要立刻再刷一套。")
    L.append(r"\item 最后一天不开新章，只看速查卡和错题。")
    L.append(r"\end{enumerate}")
    L.append(r"\begin{tcolorbox}[colback=orange!6,colframe=orange!70,title=如果只剩 1 小时]")
    L.append(r"先看速查卡的公式/模板（20 min），再做 10 道错题（30 min），最后遮住答案复述 3 个必背点（10 min）。不要开新章。")
    L.append(r"\end{tcolorbox}")
    L.append(r"\end{document}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="plan.json")
    ap.add_argument("--out", default="复习计划", help="output prefix")
    ap.add_argument("--today", default="", help="override today (YYYY-MM-DD)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    today = parse_date(args.today) if args.today else date.today()
    exam = parse_date(data["exam_date"])
    days_left = (exam - today).days
    hours = float(data.get("hours_per_day", 6))
    target = data.get("target_score")
    course = data.get("course", "课程")
    topics = normalize_topics(data.get("topics", []))

    if days_left <= 0:
        print("考试已到/已过：只输出急救单，不排多天计划。")
        days = make_one_day_plan(course, today, exam, hours)
    elif days_left == 1:
        days = make_one_day_plan(course, today, exam, hours)
    else:
        days = make_normal_plan(course, today, exam, days_left, hours, target, topics)

    # Normalize hours for topic table (for one-day plans, keep 0).
    if days_left >= 2:
        # Recompute total for display consistency.
        content_days = max(1, len([d for d in days if d["kind"] == "content"]))
        for t in topics:
            t.setdefault("hours", max(0.8, content_days * hours * 0.85 * t["share"]))

    md = render_markdown(course, today, exam, days_left, hours, target, topics, days)
    tex = render_latex(course, today, exam, days_left, hours, target, topics, days)

    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write(md)
    with open(args.out + ".tex", "w", encoding="utf-8") as f:
        f.write(tex)
    with open(args.out + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({
            "course": course, "today": today.isoformat(), "exam_date": exam.isoformat(),
            "days_left": days_left, "hours_per_day": hours, "target_score": target,
            "topics": topics,
            "days": [{**d, "date": d["date"].isoformat()} for d in days],
        }, f, ensure_ascii=False, indent=2)
    print("wrote %s.md / %s.tex / %s.plan.json" % (args.out, args.out, args.out))


if __name__ == "__main__":
    main()
