# 数据层规范（所有技能必读）

数据层是五个技能共享的"记忆"。没有它，每个技能都是失忆的；有了它，飞轮才能越转越快。

## 一、案例文件夹（每个用户一个）

位置：`cases/<日期-用户代号>/`，例如 `cases/20260903-aimo/`。

首次使用某技能时，若本地无案例文件夹，先从 `assets/templates/case/` 复制一份，再开始工作。

| 文件 | 用途 | 谁写 |
|---|---|---|
| `profile.yaml` | 用户基本信息：背景、目标、城市、薪资底线、限制条件、当前阶段 | 所有技能 |
| `experience-assets.md` | 经历素材库：真实经历整理成可用材料 | 转行门、简历优化 |
| `strengths.md` | 优势清单：每条必须带证据 | 转行门、简历优化 |
| `transition-plan.md` | 转行规划：知识路线、项目安排、时间预算 | 转行门 |
| `project-log.md` | 项目日志：做了哪些实操项目、交付物、可写进简历的 bullet | 转行门、简历优化 |
| `target-roles.csv` | 目标岗位清单：各方向匹配理由、缺口、30天行动、优先级 | 转行门 |
| `expression-weaknesses.md` | 表达弱点清单：口头禅、逻辑毛病、紧张触发点 | 表达训练、JD备战 |
| `interview-story-bank.md` | 面试故事库：STAR 结构化故事 + 风险措辞 + 改进版回答 | 表达训练、JD备战 |
| `application-tracker.csv` | 投递跟踪：投了哪家、回复、面试结果 | 简历优化、JD备战 |
| `interview-log.md` | 面试记录：真实面试题 + 当时怎么答 + 复盘 | JD备战 |
| `offer-review.md` | Offer 评估：条款、到手测算、决策 | Offer评估 |
| `review-log.md` | 复盘日志：每次关键节点的总结 | 所有技能 |

## 二、知识库（跨案例积累，飞轮的主体）

位置：`knowledge-base/`，首次使用时从 `assets/templates/knowledge-base/` 复制。

```
knowledge-base/
├── index.md              # 索引：每个条目的元数据（岗位/日期/关键词/一句话摘要）
├── interview-question-bank/  # 真实面试题库，按岗位分文件
├── industry-data/            # 行业薪资、门槛、真实工作内容
├── project-library.md        # 实操项目库
└── mistake-book.md           # 错题本：失败案例、减分点
```

**检索规则（防上下文过长）**：
1. 技能启动时只读 `index.md`（几百字）
2. 按需读取具体条目文件，不全量加载
3. 引用条目时注明来源文件和日期

## 三、文档入库协议

用户发来 word / pdf / 图片简历或 JD 时：
1. 第一步：转成 markdown，存入案例文件夹（`resume_latest.md` / `jd_<日期>.md`）
2. 旧版本不删，存为 `resume_v1.md` 等，便于对比迭代
3. 之后所有技能只读 markdown，不重复解析原文件

## 四、四类信息分栏（防幻觉核心）

记录任何信息时，必须标注类型：

| 类型 | 含义 | 例子 |
|---|---|---|
| `事实` | 用户亲述或可查证 | "用户上份工作做了一年" |
| `假设` | 未经证实的前提 | "假设用户能接受 6-8K" |
| `推断` | AI 基于事实的判断 | "推断用户表达偏弱" |
| `用户偏好` | 用户的主观意愿 | "用户想长期发展" |

**规则**：`推断` 永远不能当 `事实` 引用。给用户建议时，推断要说明"这是我的判断"。

## 五、证据标记 needs_proof

简历或叙述中缺乏证据的内容，标记 `needs_proof`，不编造、不默认成立。
例：`"独立负责大促活动" [needs_proof：需用户提供具体数据]`

## 六、时间戳

知识库每条内容带日期 `[2026-09-03]`。引用超过 3 个月的薪资 / 行情数据时，标注"此为 X 月数据，建议重新核实"。

## 七、各技能读写职责

| 技能 | 读 | 写 |
|---|---|---|
| 转行门 | profile、knowledge-base/index | profile、transition-plan、target-roles、experience-assets、strengths、project-log |
| 简历优化 | profile、experience-assets、project-log、strengths | resume 文件、application-tracker |
| JD备战 | profile、expression-weaknesses、interview-story-bank、interview-question-bank | interview-log、interview-story-bank、interview-question-bank、mistake-book |
| 表达训练 | profile、expression-weaknesses、interview-story-bank | expression-weaknesses、interview-story-bank |
| Offer评估 | profile、offer 历史 | offer-review、industry-data（薪资数据点） |

**结束前必做**：执行 [归档清单](archive-checklist.md)，没归档不算闭环。
