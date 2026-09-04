# 安装指南

Profession-ez 是一组技能文件，支持在所有**能读取本地文件、支持自定义 Skill** 的 AI 智能体中使用。

## 方式一：下载压缩包（推荐，最简单）

1. 打开 GitHub 仓库页面，点击右上角 **Code** → **Download ZIP**
2. 解压到你能找到的位置，比如 `D:\Profession-ez\`
3. 然后按你用的 AI 工具，对照下面的方式导入

---

## 各 AI 工具导入方式

### TRAE / TraeCode / TraeWork（国内推荐）

1. 打开 TRAE，进入你的工作区
2. 找到工作区下的 `.trae/skills/` 目录（没有就新建）
3. 把 Profession-ez 里 `skills/` 下的 **5 个技能文件夹**整个复制进去：
   ```
   你的工作区/
   └── .trae/
       └── skills/
           ├── career-transition-gate/    ← 转行门
           ├── resume-jobhunt/            ← 简历优化
           ├── jd-interview-prep/         ← JD备战
           ├── expression-coach/          ← 表达训练
           └── offer-evaluator/           ← Offer评估
   ```
4. 把 `shared/`、`assets/`、`scripts/` 这三个文件夹放到**工作区根目录**（AI 能访问到的地方）
5. 重启或刷新 TRAE，技能就加载好了

### 扣子（Coze）/ 豆包智能体

1. 在扣子平台创建或打开你的智能体
2. 进入"人设与回复逻辑"→"技能"→"添加技能"
3. 选择"自定义技能"，把每个 skill 的 `SKILL.md` 内容粘贴进去
4. **关键：把 `shared/`、`assets/` 里的文件上传到知识库**——不然 AI 找不到参考文档和模板
5. 触发词建议设置为："转行、改简历、面试、offer、表达训练"等
6. 注意：扣子平台对技能格式有自己的规范，可能需要微调触发词

### Codex / WorkBuddy 类桌面 AI

> 这类工具加载 Skill 时，AI 容易"忘记"自己的角色、找不到知识库文件。
> 以下是**正确加载姿势**，按这个做才不会乱：

1. **方式 A（推荐）：整个文件夹作为工作区**
   - 把整个 Profession-ez 解压到一个目录
   - 在 Codex/WorkBuddy 中打开这个目录作为工作区
   - 把 `skills/` 下的技能文件夹复制到对应 AI 工具的 skills 目录（如 `.codex/skills/`）
   - **关键**：`shared/`、`assets/`、`scripts/` 必须在工作区根目录，AI 才能读到

2. **方式 B：系统提示词 + 知识库**
   - 如果平台不支持 Skill 格式，把 `SKILL.md` 全部内容粘贴到系统提示词
   - 把 `shared/` 和 `assets/templates/knowledge-base/` 里的文件上传为知识库
   - 使用时手动喊"帮我做转行分析""帮我改简历"来触发

3. **验证是否加载正确**（必做！）：
   - 问 AI："你是谁？"
   - 正确回答应该提到"Profession-ez"和"转行陪跑"
   - 如果回答"我是 Codex/我是 WorkBuddy"，说明角色没代入——把 SKILL.md 再贴一次到系统提示词里

### Dify / FastGPT / 其他国产平台

1. 打开你的 AI 应用后台
2. 找到"系统提示词"或"知识库"设置
3. 把 `skills/` 下每个技能的 `SKILL.md` 和 `references/` 内容作为系统提示词或知识库导入
4. `assets/templates/` 里的模板可以上传为文档，供 AI 引用生成
5. `scripts/` 里的 Python 脚本如果平台支持代码执行，可以上传为工具

### Claude Desktop / ChatGPT / Cursor 等海外工具

1. **Claude Desktop**：把整个 Profession-ez 文件夹放到 Claude 能访问的目录，在 Claude 的 `.claude/skills/` 里创建软链接或直接复制 skill 文件夹
2. **ChatGPT（自定义 GPT）**：把 `SKILL.md` 内容放进 Instructions，把 `references/` 和 `assets/` 上传为 Knowledge
3. **Cursor / Windsurf**：在项目根目录创建 `.cursorrules` 或类似文件，把技能规则写进去

> 不同平台的 Skill 机制差异很大，核心原则是：**让 AI 能读到 SKILL.md 的规则 + 能访问到模板和参考文档**。格式可以灵活调整，内容是通用的。

---

## 验证安装成功

两步验证，都通过才算真的装好了：

### 第一步：身份验证
对 AI 说："你是谁？"

✅ 正确回答：提到"Profession-ez""转行陪跑"
❌ 错误回答："我是XX大模型""我是AI助手"（说明角色没代入，需要检查 SKILL.md 是否正确加载）

### 第二步：功能验证
对 AI 说："我想转行，你能帮我做什么？"

✅ 正确：输出转行门引导菜单，问你背景和目标
❌ 错误：回答很泛、东拉西扯、不按流程走（说明知识库或参考文档没加载到）

---

## 目录结构说明（给想搞清楚的人）

```
Profession-ez/
├── skills/                  ← 5 个技能，每个是独立文件夹
│   ├── career-transition-gate/   # 转行门
│   ├── resume-jobhunt/           # 简历优化
│   ├── jd-interview-prep/        # JD 备战
│   ├── expression-coach/         # 表达训练
│   └── offer-evaluator/          # Offer 评估
├── shared/                  ← 共享规则（防幻觉、数据层规范等）
├── assets/
│   └── templates/           ← 模板库（简历、面试记录、错题本等）
├── scripts/                 ← Python 工具脚本（可选，不用也能跑）
├── examples/
│   └── seed-case-aimo/      ← 种子案例（已脱敏，供参考）
├── docs/                    ← 使用文档
└── README.md
```

**技能之间怎么协作？**
5 个技能共享同一个**案例文件夹**（你创建的用户档案）和**知识库**，所以你从转行门开始，后面用简历优化、面试备战时，AI 能记住你的情况，不用每次重新说一遍。

---

## 脚本依赖（可选）

脚本工具不是必须的，不用脚本也能用全部技能。
想用脚本的话，需要 Python 3.7+，安装依赖：

```bash
pip install python-docx pdfplumber
```

脚本包括：
- `salary_calculator.py` —— 到手工资计算器（算真实到手，不靠 AI 心算）
- `extract_resume.py` —— 简历文本提取（Word/PDF → Markdown）
- `normalize_jd.py` —— JD 关键词统计
- `job_match_scorer.py` —— 转行岗位匹配打分

---

## 常见问题

**Q: AI 没识别到技能怎么办？**
A: 检查 SKILL.md 是否在每个技能文件夹的根目录，文件名和路径别错。

**Q: 一定要装 5 个吗？我只用其中一个行不行？**
A: 可以单独用，每个技能都是独立的。但建议全装，因为它们共享数据，链路完整效果更好。

**Q: 我的 AI 平台不支持 Skill 格式怎么办？**
A: 把 SKILL.md 里的内容直接复制粘贴到系统提示词里也能用，就是触发需要你手动喊"帮我做XX"。

**Q: 数据安全吗？**
A: 所有数据都在你本地，技能包本身不收集、不上传任何信息。详见 `docs/safety.md`。
