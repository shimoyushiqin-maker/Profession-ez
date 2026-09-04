# -*- coding: utf-8 -*-
"""
JD 关键词分析器（确定性统计，不靠 AI 心算）

用法：
    python jd_keyword_analyzer.py --input jd_texts/ --output report.md

参数说明：
    --input     JD 文本所在的文件夹（每个 .txt 文件是一个 JD）
                或者直接传单个文件路径
    --output    输出报告的文件路径（Markdown 格式）
    --top-n     输出前 N 个高频词，默认 30

说明：
    - 自动中文分词 + 停用词过滤
    - 按 4 大类统计：技能工具 / 岗位职责 / 任职要求 / 软能力
    - 生成结构化分析报告（Markdown）
    - 结果是统计辅助，最终分析需要人工校验和归类
"""
import argparse
import os
import re
from collections import Counter

# 停用词（无意义的高频词，过滤掉）
STOP_WORDS = set("""
的 了 和 是 在 有 我 也 就 都 而 及 与 等 或 对 为 以 到 被 把 从 上 下 中 内 外 前 后
你 他 她 它 我们 你们 他们 自己 什么 怎么 这样 那样 这个 那个 这些 那些 一个 一些
工作 公司 负责 岗位 职位 要求 职责 任职 资格 经验 能力 优先 熟悉 熟练 掌握 了解
具备 良好 较强 能够 可以 具有 完成 配合 参与 协助 推进 推动 执行 落实 跟进
相关 各种 各类 以上 以下 以内 以外 之间 包括 例如 以及 等等 不同 相应 相关
进行 开展 提升 优化 完善 建立 搭建 制定 设计 开发 实现 保障 支持 服务 管理
""".split())

# 技能/工具类关键词（用于分类）
SKILL_KEYWORDS = [
    # 办公工具
    "Excel", "PPT", "Word", "Office", "数据透视表", "VLOOKUP",
    # 编程/数据
    "Python", "SQL", "数据分析", "数据统计", "数据可视化", "Pandas",
    # AI工具
    "AI", "大模型", "LLM", "Prompt", "提示词", "AIGC", "ChatGPT",
    "豆包", "通义千问", "文心一言", "Kimi", "Claude",
    "Midjourney", "Stable Diffusion", "即梦", "可灵",
    "Dify", "扣子", "Coze", "RAG", "Agent", "智能体",
    # 运营工具
    "小红书", "公众号", "抖音", "视频号", "B站", "知乎",
    "剪映", "PS", "Photoshop", "Figma",
    # 投放/增长
    "投放", "信息流", "SEM", "SEO", "ROI", "CPC", "CPM", "CPA",
    "增长", "裂变", "私域", "公域",
    # 产品/项目
    "PRD", "需求分析", "原型设计", "Axure", "墨刀",
    "项目管理", "敏捷", "Scrum", "OKR", "KPI",
    # 行业术语
    "CMP", "抛光", "晶圆", "半导体", "芯片", "fab",
    "工艺", "良率", "刻蚀", "薄膜", "光刻",
]

# 岗位职责类关键词
RESPONSIBILITY_KEYWORDS = [
    "内容运营", "内容策划", "文案撰写", "内容生产", "内容创作",
    "用户运营", "用户增长", "用户留存", "用户活跃", "社群运营",
    "活动运营", "活动策划", "活动执行",
    "产品运营", "产品迭代", "需求分析", "用户研究",
    "数据分析", "数据复盘", "数据追踪", "数据监控",
    "市场调研", "竞品分析", "行业研究",
    "客户对接", "客户支持", "客户服务", "技术支持",
    "方案撰写", "方案设计", "解决方案",
    "项目推进", "项目管理", "项目落地",
    "团队协作", "跨部门", "沟通协调",
]

# 任职要求类（硬技能）
REQUIREMENT_KEYWORDS = [
    "运营经验", "内容经验", "用户经验", "产品经验",
    "数据分析能力", "文案能力", "策划能力",
    "学习能力", "抗压能力", "沟通能力", "表达能力",
    "逻辑思维", "结构化思维", "数据敏感度",
    "本科及以上", "大专及以上", "学历",
    "1-3年", "3-5年", "5年以上", "0-1年",
]

# 软能力类
SOFT_SKILL_KEYWORDS = [
    "责任心", "执行力", "学习力", "沟通力", "协调力",
    "团队合作", "团队精神", "抗压能力", "乐观", "积极",
    "认真负责", "细心", "严谨", "主动", "热情",
    "结果导向", "目标导向", "数据驱动",
]


def load_jd_texts(input_path):
    """加载 JD 文本，返回 list[(文件名, 文本)]"""
    results = []
    if os.path.isfile(input_path):
        # 单个文件
        with open(input_path, 'r', encoding='utf-8') as f:
            results.append((os.path.basename(input_path), f.read()))
    elif os.path.isdir(input_path):
        # 文件夹
        for fname in sorted(os.listdir(input_path)):
            if fname.endswith('.txt') or fname.endswith('.md'):
                fpath = os.path.join(input_path, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    results.append((fname, f.read()))
    else:
        print(f"错误：找不到 {input_path}")
        return []
    return results


def simple_tokenize(text):
    """
    简单分词（不依赖 jieba，保证脚本开箱即用）
    策略：
    1. 提取英文单词（含大小写字母、数字、连字符）
    2. 提取中文 2-6 字词组（通过关键词匹配）
    3. 用正则提取数字+单位的组合
    """
    tokens = []

    # 提取英文单词
    english_words = re.findall(r'[A-Za-z][A-Za-z0-9+\-/.#]*', text)
    tokens.extend([w for w in english_words if len(w) >= 2])

    # 匹配已知关键词（中文）
    all_keywords = (SKILL_KEYWORDS + RESPONSIBILITY_KEYWORDS +
                    REQUIREMENT_KEYWORDS + SOFT_SKILL_KEYWORDS)
    for kw in all_keywords:
        count = text.count(kw)
        if count > 0:
            tokens.extend([kw] * count)

    # 提取数字+单位组合（如"3年""10K""500强"）
    number_units = re.findall(r'\d+[年月日Kk%个家项篇条次]+', text)
    tokens.extend(number_units)

    return tokens


def filter_tokens(tokens):
    """过滤停用词和太短的词"""
    filtered = []
    for t in tokens:
        t_lower = t.lower()
        if t_lower in STOP_WORDS:
            continue
        if len(t) < 2:
            continue
        filtered.append(t)
    return filtered


def classify_keyword(word):
    """给关键词分类，返回类别名"""
    word_lower = word.lower()
    for kw in SKILL_KEYWORDS:
        if kw.lower() == word_lower or kw.lower() in word_lower:
            return "技能/工具"
    for kw in RESPONSIBILITY_KEYWORDS:
        if kw.lower() == word_lower or kw.lower() in word_lower:
            return "岗位职责"
    for kw in REQUIREMENT_KEYWORDS:
        if kw.lower() == word_lower or kw.lower() in word_lower:
            return "任职要求"
    for kw in SOFT_SKILL_KEYWORDS:
        if kw.lower() == word_lower or kw.lower() in word_lower:
            return "软能力"
    return "其他"


def analyze(jd_texts, top_n=30):
    """分析 JD，返回分析结果 dict"""
    all_tokens = []
    total_jds = len(jd_texts)

    for fname, text in jd_texts:
        tokens = simple_tokenize(text)
        tokens = filter_tokens(tokens)
        all_tokens.extend(tokens)

    # 总词频
    counter = Counter(all_tokens)

    # 分类统计
    categories = {
        "技能/工具": [],
        "岗位职责": [],
        "任职要求": [],
        "软能力": [],
        "其他": [],
    }

    for word, count in counter.most_common(top_n * 3):
        cat = classify_keyword(word)
        categories[cat].append((word, count))

    # 计算出现频率（多少个 JD 里出现了这个词）
    # 简化版：用词频 / JD 数量估算
    def calc_freq(count):
        ratio = count / total_jds
        if ratio > 2:
            ratio = 2.0
        return min(ratio * 50, 100)  # 粗略估算百分比

    # Top N 总排名
    top_words = []
    for word, count in counter.most_common(top_n):
        freq = calc_freq(count)
        cat = classify_keyword(word)
        # 重要程度分级
        if freq >= 70:
            level = "必学"
        elif freq >= 50:
            level = "重点学"
        elif freq >= 30:
            level = "选学"
        else:
            level = "了解"
        top_words.append({
            "word": word,
            "count": count,
            "freq_est": freq,
            "category": cat,
            "level": level,
        })

    return {
        "total_jds": total_jds,
        "total_tokens": len(all_tokens),
        "unique_words": len(counter),
        "top_words": top_words,
        "categories": categories,
    }


def generate_report(result, output_path):
    """生成 Markdown 格式的分析报告"""
    lines = []
    lines.append("# JD 关键词分析报告")
    lines.append("")
    lines.append(f"> 分析样本：{result['total_jds']} 个 JD")
    lines.append(f"> 总词数：{result['total_tokens']}")
    lines.append(f"> 不同关键词数：{result['unique_words']}")
    lines.append(f"> 生成时间：见文件修改时间")
    lines.append("")

    # Top 关键词总排名
    lines.append("## Top 30 高频关键词总排名")
    lines.append("")
    lines.append("| 排名 | 关键词 | 出现次数 | 估算出现率 | 分类 | 重要程度 |")
    lines.append("|---|---|---|---|---|---|")
    for i, w in enumerate(result["top_words"][:30], 1):
        lines.append(f"| {i} | {w['word']} | {w['count']} | ~{w['freq_est']:.0f}% | {w['category']} | {w['level']} |")
    lines.append("")

    # 分类统计
    lines.append("## 分类统计")
    lines.append("")

    for cat_name in ["技能/工具", "岗位职责", "任职要求", "软能力"]:
        words = result["categories"].get(cat_name, [])
        if not words:
            continue
        lines.append(f"### {cat_name}（Top 15）")
        lines.append("")
        lines.append("| 关键词 | 出现次数 |")
        lines.append("|---|---|")
        for word, count in words[:15]:
            lines.append(f"| {word} | {count} |")
        lines.append("")

    # 学习优先级建议
    lines.append("## 学习优先级建议")
    lines.append("")
    must_learn = [w for w in result["top_words"] if w["level"] == "必学"]
    important = [w for w in result["top_words"] if w["level"] == "重点学"]
    optional = [w for w in result["top_words"] if w["level"] == "选学"]

    lines.append("### 🎯 必学（出现率 ≥ 70%）")
    if must_learn:
        for w in must_learn[:10]:
            lines.append(f"- **{w['word']}**（{w['category']}）")
    else:
        lines.append("- 暂无（样本量可能不足）")
    lines.append("")

    lines.append("### ⭐ 重点学（出现率 50-70%）")
    if important:
        for w in important[:10]:
            lines.append(f"- {w['word']}（{w['category']}）")
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("### 📖 选学（出现率 30-50%）")
    if optional:
        for w in optional[:10]:
            lines.append(f"- {w['word']}（{w['category']}）")
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append("- 本报告为**辅助工具**，关键词分类和出现率为估算值，需人工校验")
    lines.append("- 出现率 = 词频 / JD 数量 × 系数，是粗略估算，不是精确值")
    lines.append("- 建议结合 JD 全文人工分析，重点关注：岗位职责、任职要求、薪资范围")
    lines.append("- 关键词库可根据目标行业自行扩充（修改脚本中的 KEYWORDS 列表）")
    lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"报告已生成：{output_path}")


def main():
    p = argparse.ArgumentParser(description="JD 关键词分析器")
    p.add_argument("--input", required=True, help="JD 文件或文件夹路径（.txt/.md）")
    p.add_argument("--output", default="jd-analysis-report.md", help="输出报告路径（Markdown）")
    p.add_argument("--top-n", type=int, default=30, help="输出前 N 个高频词")
    args = p.parse_args()

    print("=" * 50)
    print("JD 关键词分析器")
    print("=" * 50)

    # 加载 JD
    jd_texts = load_jd_texts(args.input)
    if not jd_texts:
        print("没有找到 JD 文件，请检查 --input 路径")
        return

    print(f"已加载 {len(jd_texts)} 个 JD：")
    for fname, _ in jd_texts:
        print(f"  - {fname}")
    print()

    # 分析
    print("正在分析...")
    result = analyze(jd_texts, args.top_n)

    # 生成报告
    generate_report(result, args.output)

    # 控制台输出摘要
    print()
    print("【摘要】")
    print(f"  样本数量：{result['total_jds']} 个 JD")
    print(f"  总关键词数：{result['total_tokens']}")
    print(f"  Top 10 高频词：")
    for i, w in enumerate(result["top_words"][:10], 1):
        print(f"    {i}. {w['word']} ({w['count']}次, {w['level']})")

    print()
    print("完成！详细报告见输出文件。")


if __name__ == "__main__":
    main()
