# -*- coding: utf-8 -*-
"""
到手工资计算器（确定性计算，不靠 AI 心算）

用法：
    python salary_calculator.py --salary 8000 --probation-ratio 0.8 \
        --social-rate 0.105 --fund-rate 0.05 --fund-base-ratio 1.0

参数说明：
    --salary            转正名义月薪（税前）
    --probation-ratio   试用期工资折扣（如 0.8 表示打 8 折），默认 1.0
    --social-rate       社保个人缴纳比例合计（养老8%+医疗2%+失业0.5%≈0.105）
    --fund-rate         公积金个人缴纳比例（如 0.05 表示 5%）
    --fund-base-ratio   五险一金缴费基数/名义工资（最低基数通常远小于1，如0.3）
                        默认 1.0 表示按全额工资交

说明：
    - 个税用月度简化税率表（起征点 5000），未含专项附加扣除
    - 结果为估算，实际以公司 HR 计算为准
"""
import argparse

# 月度个税税率表：(上限, 税率, 速算扣除数)
TAX_TABLE = [
    (3000, 0.03, 0),
    (12000, 0.10, 210),
    (25000, 0.20, 1410),
    (35000, 0.25, 2660),
    (55000, 0.30, 4410),
    (80000, 0.35, 7160),
    (float('inf'), 0.45, 15160),
]
TAX_FREE = 5000


def calc_tax(taxable):
    if taxable <= 0:
        return 0.0
    for cap, rate, deduct in TAX_TABLE:
        if taxable <= cap:
            return taxable * rate - deduct
    return 0.0


def calc_take_home(gross, social_rate, fund_rate, fund_base_ratio):
    base = gross * fund_base_ratio  # 缴费基数
    social = base * social_rate
    fund = base * fund_rate
    taxable = gross - social - fund - TAX_FREE
    tax = calc_tax(taxable)
    take_home = gross - social - fund - tax
    return {
        "gross": gross,
        "social": social,
        "fund": fund,
        "tax": tax,
        "take_home": take_home,
    }


def main():
    p = argparse.ArgumentParser(description="到手工资计算器")
    p.add_argument("--salary", type=float, required=True, help="转正名义月薪")
    p.add_argument("--probation-ratio", type=float, default=1.0, help="试用期折扣")
    p.add_argument("--social-rate", type=float, default=0.105, help="社保个人比例合计")
    p.add_argument("--fund-rate", type=float, default=0.05, help="公积金个人比例")
    p.add_argument("--fund-base-ratio", type=float, default=1.0, help="缴费基数/工资")
    a = p.parse_args()

    print("【真实到手测算】")
    for label, gross in [
        ("转正", a.salary),
        ("试用期", a.salary * a.probation_ratio),
    ]:
        r = calc_take_home(gross, a.social_rate, a.fund_rate, a.fund_base_ratio)
        print(f"{label}: 名义 {r['gross']:.0f} -> 到手约 {r['take_home']:.0f} "
              f"(社保 {r['social']:.0f} / 公积金 {r['fund']:.0f} / 个税 {r['tax']:.0f})")

    if a.fund_base_ratio < 1.0:
        lost = a.salary * (1 - a.fund_base_ratio) * (a.social_rate + a.fund_rate)
        print(f"提示: 按最低基数缴纳，每月公积金+社保账户比全额缴纳少约 {lost:.0f} 元（隐形亏损）")


if __name__ == "__main__":
    main()
