# 更新日志

所有重要变更都记录在这里。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.2.0] - 2026-09-03

### 新增
- `job_match_scorer.py` 转行岗位匹配打分脚本（可迁移能力/转行友好度/风险识别/成长空间五维）
- `target-roles.csv` 目标岗位清单模板（匹配理由/缺口/30天行动/优先级）
- `interview-story-bank.md` 面试故事库模板（STAR + 可迁移点 + 风险措辞 + 改进回答）
- `docs/platform-boundaries.md` 平台使用边界说明
- 安装文档增加多智能体适配说明（TRAE / 扣子 / Dify / Claude / ChatGPT 等）

### 优化
- 数据层规范补充 target-roles、interview-story-bank 两个文件定义
- 归档清单增加对应检查项
- 各技能数据层读写职责同步更新

## [0.1.0] - 2026-09-03

### 新增
- 首个版本：五个技能全链路上线
  - `career-transition-gate` 转行门（行业真相核查 / 动机深挖 / 现实检验作业 / 可行性评估 / 知识点补全 / 实操项目设计）
  - `resume-jobhunt` 简历优化（翻译模式 / 升级模式 / 真实性审核 / 投递渠道）
  - `jd-interview-prep` JD 备战（JD 核查 / 知识补全 / 模拟面试 / 面试复盘）
  - `expression-coach` 表达训练（表达评估 / 提示词点评 / STAR 故事库 / 紧张管理 / 三档开关）
  - `offer-evaluator` Offer 评估（谈薪策略 / 到手测算 / 六维评估 / 红线清单）
- 共享规范：数据层规范、开机引导协议、防幻觉规则、归档清单
- 案例文件夹模板 + 知识库模板 + 实操项目库
- 确定性计算脚本：到手工资计算器、JD 关键词统计、简历文本提取
- 种子案例：作者真实转行经历（已脱敏）
- 文档：安装、使用、首次使用指南、安全隐私、常见问题

### 说明
- 案例文件夹结构与"证据驱动"理念参考自 [JobOK](https://github.com/GresonKwan/JobOK)（MIT）
