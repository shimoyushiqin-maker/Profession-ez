# -*- coding: utf-8 -*-
"""
转行岗位匹配打分器

针对转行人员的特殊需求设计，不仅看技能匹配，更看重：
- 可迁移能力匹配度（你以前的经验能不能用上）
- 转行友好度（接不接受跨行、要不要培训经历）
- 风险识别（培训贷、挂羊头卖狗肉、纯销售陷阱）
- 成长空间（能不能当跳板、能不能攒作品集）

用法：
    # 单个 JD 打分
    python job_match_scorer.py --jd jd.txt --profile profile.yaml

    # 批量打分（CSV 输入，输出带分的 CSV）
    python job_match_scorer.py --batch jobs.csv --profile profile.yaml --output scored.csv

输入 CSV 格式（至少包含 title 和 jd_text 两列）：
    title,company,jd_text,city,salary,source
    AI产品运营,某公司,负责...,某新一线城市,6-8K,BOSS直聘

说明：
    - 分数仅供参考，不能代替你的判断
    - 风险项会单独标红提醒
    - profile.yaml 用 cases 文件夹里的用户档案格式
"""
import argparse
import csv
import os
import re
import sys


# ========== 风险词库（转行人员特别容易踩的坑）==========
RISK_TERMS = [
    # 培训贷 / 收费陷阱
    "培训贷", "贷款培训", "包就业", "保offer", "先交费", "培训费",
    "岗前培训", "实训", "学徒制收费", "就业协议", "分期付费",
    # 挂羊头卖狗肉
    "纯销售", "电话销售", "地推", "扫楼", "卖课程", "拉人头",
    "发展下线", "传销", "刷单", "刷流水",
    # 虚假高薪
    "无经验高薪", "零基础高薪", "月入过万", "年薪百万",
    "轻松过万", "在家赚钱", "日结",
]

# ========== 转行友好信号（加分）==========
TRANSITION_FRIENDLY = [
    "接受转行", "欢迎转行", "零基础可", "无经验可", "应届生可",
    "培训", "带教", "导师", "成长型", "学习型",
    "大专", "专升本", "学历不限", "专业不限",
]

# ========== 可迁移能力词库（按类别）==========
# 前行业经验 → 目标岗位的可迁移映射
TRANSFERABLE_SKILLS = {
    # 化工/制造业 → 可迁移
    "化工": ["实验", "配方", "工艺", "质检", "流程", "变量控制", "数据记录", "SOP", "合规"],
    # 销售/客服 → 可迁移
    "销售": ["客户", "沟通", "需求", "谈判", "转化", "客情", "投诉", "复盘"],
    # 行政/运营 → 可迁移
    "行政": ["协调", "推进", "文档", "流程", "活动", "数据", "Excel", "PPT"],
    # 教育/培训 → 可迁移
    "教育": ["内容", "文案", "讲解", "用户", "社群", "运营", "课程", "学员"],
    # 通用
    "通用": ["Excel", "PPT", "数据", "分析", "沟通", "协调", "执行",
              "项目", "流程", "文档", "汇报", "复盘", "用户", "内容"],
}

# ========== AI 运营核心技能（目标端）==========
TARGET_SKILLS_AI_OP = [
    "运营", "内容", "文案", "投放", "转化", "用户", "数据", "分析",
    "活动", "增长", "留存", "拉新", "促活", "社群", "私域",
    "小红书", "抖音", "公众号", "短视频", "直播",
    "AI", "大模型", "AIGC", "Prompt", "智能体", "Agent",
    "Excel", "SQL", "Python", "PS", "剪辑",
]


def read_text(path):
    """读文本文件"""
    if not path or not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_simple_yaml(text):
    """极简 YAML 解析：只取冒号后面的值（够我们用了）"""
    values = []
    key_values = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # 列表项 - "xxx"
        if stripped.startswith("-"):
            val = stripped.strip("-").strip().strip('"').strip("'")
            if val:
                values.append(val)
            continue
        # key: value
        if ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                key_values[key] = val
                values.append(val)
    return key_values, values


def tokenize(text):
    """分词：英文+数字+中文两字词以上"""
    words = re.findall(r"[A-Za-z0-9+#.]+|[\u4e00-\u9fff]{2,}", text.lower())
    return [w for w in words if len(w.strip()) >= 2]


def keyword_overlap(source_text, target_keywords):
    """计算 source 中包含多少个 target 关键词"""
    source_lower = source_text.lower()
    found = [kw for kw in target_keywords if kw.lower() in source_lower]
    return found


def detect_risks(jd_text):
    """识别风险词"""
    found = []
    for term in RISK_TERMS:
        if term in jd_text:
            found.append(term)
    return found


def detect_transition_friendly(jd_text):
    """识别转行友好信号"""
    found = []
    for term in TRANSITION_FRIENDLY:
        if term in jd_text:
            found.append(term)
    return found


def calc_transferable_score(profile_text, jd_text, industry=None):
    """可迁移能力匹配分（0-25分）"""
    # 先看通用可迁移技能
    general_found = keyword_overlap(profile_text + jd_text, TRANSFERABLE_SKILLS["通用"])
    general_score = min(10, len(general_found) * 1)

    # 行业专属可迁移
    industry_score = 0
    if industry:
        industry_key = industry[:2]  # 取前两个字匹配
        for key in TRANSFERABLE_SKILLS:
            if key in industry or industry in key:
                industry_skills = TRANSFERABLE_SKILLS[key]
                found_in_jd = keyword_overlap(jd_text, industry_skills)
                industry_score = min(10, len(found_in_jd) * 2)
                break

    # 转行友好信号加分
    friendly = detect_transition_friendly(jd_text)
    friendly_score = min(5, len(friendly) * 1)

    total = general_score + industry_score + friendly_score
    return min(25, total), {
        "通用匹配": general_found[:8],
        "行业迁移匹配数": industry_score,
        "转行友好信号": friendly,
    }


def calc_hard_skill_score(jd_text, profile_skills_str):
    """硬技能匹配分（0-20分）"""
    jd_skills = keyword_overlap(jd_text, TARGET_SKILLS_AI_OP)
    profile_skills = keyword_overlap(profile_skills_str, TARGET_SKILLS_AI_OP)
    if not jd_skills:
        return 10, {"说明": "JD 未明确技能要求，给基准分"}
    overlap = set(jd_skills) & set(profile_skills)
    # 匹配比例
    ratio = len(overlap) / max(1, len(jd_skills))
    score = int(ratio * 20)
    return min(20, score), {
        "JD要求的技能": jd_skills[:10],
        "你已有的技能": list(overlap)[:10],
        "缺口": list(set(jd_skills) - overlap)[:10],
    }


def calc_growth_score(jd_text):
    """成长空间分（0-20分）—— 能不能当跳板"""
    growth_signals = [
        "AI", "大模型", "AIGC", "智能体", "Agent", "投放", "增长",
        "数据", "分析", "用户", "运营", "产品", "项目", "独立负责",
    ]
    found = keyword_overlap(jd_text, growth_signals)
    # 外包/实习扣分
    penalty = 0
    if "外包" in jd_text or "派驻" in jd_text:
        penalty -= 3
    if "实习" in jd_text or "见习" in jd_text:
        penalty -= 2
    score = min(20, len(found) * 2 + penalty)
    return max(0, score), {
        "成长关键词": found[:8],
        "扣分原因": "外包岗（履历价值打折）" if penalty < 0 else "无",
    }


def calc_risk_score(jd_text):
    """风险扣分（最多 -35 分）"""
    risks = detect_risks(jd_text)
    if not risks:
        return 0, []
    # 每个风险词扣 7 分
    penalty = len(risks) * 7
    return -min(35, penalty), risks


def calc_realism_score(jd_text, salary_text=""):
    """真实度/靠谱度（0-15分）"""
    score = 10  # 基准分
    details = []

    # 有具体职责描述加分
    if len(jd_text) > 200:
        score += 3
        details.append("职责描述详细")
    else:
        score -= 2
        details.append("JD 过于简短，信息不足")

    # 薪资范围合理（不是虚高）
    if "K" in salary_text or "千" in salary_text or "万" in salary_text:
        score += 2
        details.append("有明确薪资范围")

    # 有明确学历/经验要求加分（说明认真写的）
    for kw in ["本科", "大专", "学历", "经验", "年以上"]:
        if kw in jd_text:
            score += 1
            details.append(f"有{kw}要求")
            break

    return min(15, max(0, score)), details


def score_job(title, jd_text, profile_text, profile_skills="", industry="", salary=""):
    """给单个岗位打分"""
    transfer_score, transfer_detail = calc_transferable_score(
        profile_text + " " + profile_skills, jd_text, industry
    )
    hard_score, hard_detail = calc_hard_skill_score(jd_text, profile_skills)
    growth_score, growth_detail = calc_growth_score(jd_text)
    risk_penalty, risks = calc_risk_score(jd_text)
    realism_score, realism_detail = calc_realism_score(jd_text, salary)

    total = transfer_score + hard_score + growth_score + risk_penalty + realism_score

    # 等级
    if total >= 70:
        band = "A · 重点投"
    elif total >= 55:
        band = "B · 可以投"
    elif total >= 40:
        band = "C · 观望/补缺口后投"
    else:
        band = "D · 不建议投"

    return {
        "title": title,
        "total": total,
        "band": band,
        "transferable_score": transfer_score,
        "hard_skill_score": hard_score,
        "growth_score": growth_score,
        "risk_penalty": risk_penalty,
        "realism_score": realism_score,
        "risks": risks,
        "transfer_detail": transfer_detail,
        "hard_detail": hard_detail,
        "growth_detail": growth_detail,
        "realism_detail": realism_detail,
    }


def print_result(r):
    """打印单个结果"""
    print(f"\n{'='*50}")
    print(f"【{r['band']}】 {r['title']}")
    print(f"总分：{r['total']} / 100")
    print(f"  可迁移能力：{r['transferable_score']:>2} 分")
    print(f"  硬技能匹配：{r['hard_skill_score']:>2} 分")
    print(f"  成长空间：{r['growth_score']:>2} 分")
    print(f"  靠谱度：{r['realism_score']:>2} 分")
    if r['risk_penalty'] < 0:
        print(f"  风险扣分：{r['risk_penalty']:>2} 分 ⚠️")
        print(f"    风险词：{', '.join(r['risks'])}")

    print(f"\n可迁移能力细节：")
    for k, v in r['transfer_detail'].items():
        print(f"  {k}: {v}")

    print(f"\n硬技能缺口：")
    if r['hard_detail'].get("缺口"):
        print(f"  需要补：{', '.join(r['hard_detail']['缺口'])}")
    else:
        print("  暂无明显缺口")

    if r['growth_detail'].get("成长关键词"):
        print(f"\n成长关键词：{', '.join(r['growth_detail']['成长关键词'])}")


def main():
    p = argparse.ArgumentParser(description="转行岗位匹配打分器")
    p.add_argument("--jd", help="单个 JD 文件路径（txt）")
    p.add_argument("--batch", help="批量 JD 文件路径（CSV）")
    p.add_argument("--profile", required=True, help="用户档案 profile.yaml")
    p.add_argument("--output", help="批量模式下输出 CSV 路径")
    args = p.parse_args()

    # 读用户档案
    profile_text = read_text(args.profile)
    if not profile_text:
        sys.exit(f"无法读取用户档案: {args.profile}")
    profile_kv, profile_vals = parse_simple_yaml(profile_text)
    industry = profile_kv.get("现行业", "")
    profile_skills = " ".join(profile_vals)

    if args.jd:
        # 单 JD 模式
        jd_text = read_text(args.jd)
        if not jd_text:
            sys.exit(f"无法读取 JD 文件: {args.jd}")
        result = score_job(
            title=os.path.basename(args.jd),
            jd_text=jd_text,
            profile_text=profile_text,
            profile_skills=profile_skills,
            industry=industry,
        )
        print_result(result)

    elif args.batch:
        # 批量模式
        if not os.path.exists(args.batch):
            sys.exit(f"CSV 文件不存在: {args.batch}")
        results = []
        with open(args.batch, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("title", row.get("岗位", "未知岗位"))
                jd_text = row.get("jd_text", row.get("岗位描述", ""))
                company = row.get("company", row.get("公司", ""))
                salary = row.get("salary", row.get("薪资", ""))
                if not jd_text:
                    continue
                r = score_job(
                    title=f"{company} · {title}" if company else title,
                    jd_text=jd_text,
                    profile_text=profile_text,
                    profile_skills=profile_skills,
                    industry=industry,
                    salary=salary,
                )
                r.update(row)  # 保留原始列
                results.append(r)

        # 按总分排序
        results.sort(key=lambda x: -x["total"])

        if args.output:
            # 输出 CSV
            fieldnames = ["total", "band", "title", "company",
                          "transferable_score", "hard_skill_score",
                          "growth_score", "realism_score",
                          "risk_penalty", "risks"]
            # 加上原始 CSV 的列
            if results:
                for k in results[0].keys():
                    if k not in fieldnames and k not in ("transfer_detail", "hard_detail",
                                                         "growth_detail", "realism_detail"):
                        fieldnames.append(k)
            with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(results)
            print(f"已输出 {len(results)} 条打分结果到: {args.output}")
        else:
            # 终端打印 Top 5
            print(f"\n共分析 {len(results)} 个岗位，Top 5：")
            for i, r in enumerate(results[:5], 1):
                print(f"  {i}. [{r['band']}] {r['title']} — {r['total']}分")
            print("\n（用 --output 导出完整 CSV 查看全部）")

    else:
        sys.exit("请指定 --jd（单个）或 --batch（批量CSV）")


if __name__ == "__main__":
    main()
