# -*- coding: utf-8 -*-
"""
JD 关键词统计：提取岗位描述里的高频要求词，辅助判断真实技能需求

用法：
    python normalize_jd.py jd.txt
    （jd.txt 里放岗位描述文本）

说明：
    内置一份运营/技术常见关键词表，统计每个词出现次数，按频次排序。
    关键词表可自行扩充。
"""
import sys
import os

KEYWORDS = [
    # 运营类
    "运营", "投放", "转化", "拉新", "留存", "促活", "增长", "内容", "文案",
    "活动", "大促", "营销", "社群", "用户", "数据", "分析", "复盘",
    "小红书", "抖音", "公众号", "私域", "直播", "短视频",
    "Landing Page", "落地页", "页面", "Banner", "海报", "素材",
    "优惠券", "满减", "秒杀", "库存", "价格", "配置",
    "Push", "短信", "邮件", "触达", "资源位",
    # AI 类
    "AI", "大模型", "AIGC", "Prompt", "提示词", "智能体", "Agent",
    "机器学习", "深度学习", "NLP", "算法",
    # 技能类
    "Excel", "SQL", "Python", "PPT", "PS", "剪辑",
    # 通用要求
    "沟通", "协调", "执行", "抗压", "自驱", "学习", "经验", "本科",
]


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python normalize_jd.py jd.txt")
    path = sys.argv[1]
    if not os.path.exists(path):
        sys.exit(f"文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    counts = [(kw, text.count(kw)) for kw in KEYWORDS if kw in text]
    counts.sort(key=lambda x: -x[1])
    print("【JD 高频关键词】")
    for kw, c in counts:
        print(f"{kw}: {c}")
    if not counts:
        print("未匹配到内置关键词，可自行扩充 KEYWORDS 列表")


if __name__ == "__main__":
    main()
