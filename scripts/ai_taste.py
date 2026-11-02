# -*- coding: utf-8 -*-
"""AI 味量化指标（纯标准库，可复现）

指标口径（v2，修正旧版四处错误）：
  AI词汇密度 = AI词命中次数 / 字数 × 1000‰，短文本(<300字)标低置信度
  句长标准差 = 总体标准差 sqrt(Σ(x-μ)²/n)   —— 旧版误写成 MAD
  真人感/亲和力 = 基础分随密度下降，末尾 clamp 到 [0,100]，不再出负分
  节奏分：短文本里"句子等长"未必是 AI 味，用变异系数 CV 而非绝对标准差

用法：
  python ai_taste.py 文本.md
  python ai_taste.py --compare 原文.md 改写后.md
"""
import argparse
import math
import re
import sys

# 中文 AI 腔高频词（"首先/其次/赋能/闭环"这类国内公文与自媒体泛滥的标记）
AI_WORDS = [
    "首先", "其次", "最后", "综上所述", "总而言之", "值得注意的是", "此外", "与此同时",
    "赋能", "闭环", "抓手", "深度融合", "助力", "生态", "维度", "范式", "底层逻辑",
    "顶层设计", "组合拳", "护城河", "颗粒度", "对齐", "拉通", "沉淀",
    "显著的", "极大地", "进一步", "一定程度上", "在……方面", "发挥重要作用",
    "奠定了坚实基础", "注入了新动能", "迈上新台阶", "开启了新篇章",
]
NEG_PARALLEL = [
    r"不是[^，。；]{0,20}[，,]?而是", r"不只是[^，。；]{0,20}[，,]?更是",
    r"与其说[^，。；]{0,20}[，,]?不如说", r"不仅是[^，。；]{0,20}[，,]?也是",
    r"既是[^，。；]{0,20}[，,]?又是",
]
SENT_SPLIT = re.compile(r"[。！？!?；;\n]+")
SHORT_TEXT = 300  # 低于此字数密度统计不可靠


def word_count(text):
    return len(re.sub(r"\s+", "", text))


def ai_hits(text):
    hit = {w: text.count(w) for w in AI_WORDS if w in text}
    return hit, sum(hit.values())


def sent_stats(text):
    sents = [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]
    lens = [len(re.sub(r"\s+", "", s)) for s in sents]
    if not lens:
        return 0.0, 0.0, 0.0, 0
    mean = sum(lens) / len(lens)
    std = math.sqrt(sum((x - mean) ** 2 for x in lens) / len(lens))  # 总体标准差
    cv = std / mean if mean else 0.0
    return mean, std, cv, len(lens)


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def report(text):
    n = word_count(text)
    hit, nhit = ai_hits(text)
    density = (nhit / n * 1000) if n else 0.0
    mean, std, cv, nsent = sent_stats(text)
    neg = sum(len(re.findall(p, text)) for p in NEG_PARALLEL)

    # 密度分：0‰ -> 100, >=10‰ -> 30, 线性；末尾 clamp 防负分
    # ponytail: 短文本密度天然偏高（73 字命中 1 词就是 13.7‰），所以短文本只看"命中数"
    # 不计密度分，等用户喂长文再启用密度惩罚
    if n < SHORT_TEXT:
        density_score = clamp(100 - 25 * nhit, 30, 100)
    else:
        density_score = clamp(100 - 7 * density, 30, 100)
    # 节奏分：变异系数 CV 0.2 -> 30, 0.8 -> 100
    # ponytail: 句数 <6 时 CV 不稳（改写后常是几个等长短句，会被误判"呆板"），
    # 短文本直接给中性 60 分，别拿它当判据；只有长文才信 CV
    if nsent < 6:
        rhythm_score = 60.0
    else:
        rhythm_score = clamp(30 + (cv - 0.2) / 0.6 * 70, 30, 100)

    realistic = clamp(0.6 * density_score + 0.4 * rhythm_score - 5 * neg, 0, 100)
    affinity = clamp(0.5 * density_score + 0.5 * rhythm_score - 3 * neg, 0, 100)

    return {
        "字数": n, "AI词命中": nhit, "命中明细": hit,
        "密度‰": round(density, 2),
        "密度置信": "低（<300字，建议按每千字看长文本）" if n < SHORT_TEXT else "正常",
        "句数": nsent, "平均句长": round(mean, 1),
        "句长标准差": round(std, 2), "句长变异系数": round(cv, 2),
        "否定式排比": neg,
        "真人感": round(realistic, 1), "亲和力": round(affinity, 1),
    }


def show(name, text):
    r = report(text)
    print(f"\n== {name} ==")
    for k, v in r.items():
        print(f"  {k}: {v}")
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="AI 味量化指标")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--compare", action="store_true", help="两两对比前后变化")
    a = ap.parse_args(argv)
    texts = [open(f, encoding="utf-8").read() for f in a.files]
    if a.compare and len(texts) == 2:
        b, af = report(texts[0]), report(texts[1])
        show(a.files[0], texts[0])
        show(a.files[1], texts[1])
        print("\n== 变化 ==")
        for k in ("密度‰", "句长标准差", "句长变异系数", "真人感", "亲和力", "否定式排比"):
            print(f"  {k}: {b[k]} -> {af[k]}")
    else:
        for f, t in zip(a.files, texts):
            show(f, t)


if __name__ == "__main__":
    main()
