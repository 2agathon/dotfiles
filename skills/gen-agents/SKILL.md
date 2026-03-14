---
name: gen-agents
layer: 工程协作
description: >
  开始在任何项目上工作时触发，当项目没有 AGENTS.md 时触发，
  当用户需要建立项目级 AI 协作基准时触发，当加入有现有规范的项目时触发。
  建立 AI 在这个项目里的行为基准。
interfaces:
  upstream: [identity, principles, project-structure]
  downstream: []
---

## 这个 skill 做什么

建立 AI 在这个项目里的行为基准。

解决的根本问题：全局规范是个人资产，项目协作需要共享基准。
根据所有权和团队情况，决定基准以什么形式在这个项目里生效。

生成的 AGENTS.md 是 skill 的调度入口——
AI 读到它时知道在什么情况下去 fetch 哪个 skill，不依赖本地安装。

**内容判断标准，缺一不可：**
1. 这句话会改变 AI 的行为吗？
2. 这个信息会纠正 AI 的错误默认假设，或者填补 AI 在没有代码时的信息空白吗？

两个都回答不了的，不属于这里。

---

## 强制停止点

以下问题的答案必须来自用户，不能 ASSUMPTION 推进：

- 用户在这个项目里是否有所有权（决定规范并让他人遵守）
- 项目是否有现有代码库
- 团队成员是否有统一的全局规范基准
- 语言约定（注释、日志、commit message 分别用什么语言）
- 命令和权限约定

---

## 执行逻辑
```
第一步：确认所有权（必须问，不能推断）
    有所有权 → 走 Layer 2 路径
    没有所有权 → 走 Layer 3 路径

Layer 2 路径：
    第二步：确认项目状态（必须问）
        空项目 / Vibe Coding 起点 → 收集项目参数
        有代码库 → 从代码推断，只补推断不出或方向错的部分
    第三步：确认团队成员是否有全局规范基准（必须问）
        没有 → 自包含模式，fetch principles + identity
        有 → 偏差模式，只写偏差
    第四步：收集语言约定（必须问）
    第五步：收集命令和权限（必须问）
    第六步：识别 Layer 0 缺口（展示完整规则清单，不预筛选）
    第七步：生成，自检，交付

Layer 3 路径：
    第二步：确认是否有团队规范（必须问）
    第三步：生成对应形态，交付
```

---

## 必须问的信息

所有问题必须等用户回答后才能继续，不能推断，不能跳过。

**第一步——所有路径：**

> "在这个项目里，你能决定工程规范并让其他人遵守吗？"

**Layer 2——第二步：**

> "项目现在有没有代码库？还是从零开始？"

**Layer 2——第三步：**

> "团队成员有没有统一的全局规范基准？如果没有，是否把核心工程原则一起写进这份 AGENTS.md，让它自包含？"

**Layer 2——第四步：**

> "语言约定是什么？代码注释 / 日志输出 / 表注释 / 错误码描述 / Git commit message 分别用中文还是英文？"

**Layer 2——第五步：**

> "命令和权限怎么约定？
> - AI 可以不问直接执行的：
> - 必须先问用户确认的：
> - 永远不能做的："

---

## Layer 2 路径：有所有权

### 空项目 / Vibe Coding 起点

没有代码，AI 无从推断。以下信息是行为参数，必须收集：

- **技术栈**：决定 principles 的语言落地方式
- **业务域**：防止 AI 用错误语义命名
- **项目阶段**：MVP 可以技术债标注后推进，生产系统不行

先触发 `project-structure` skill 确认目录骨架，再生成 AGENTS.md。
顺序不能反——目录结构是后续所有生成的基准。

### 有代码库

从代码推断技术栈、目录结构、业务域。推断内容用 `[INFERRED]` 标注。
只补两类内容：
- AI 推断不出来的（隐性约定、合规要求、外部接口规则）
- AI 推断方向错的（非主流选型、业务词汇的特殊语义）

不重复 AI 已经能从代码里看到的东西。

### 自包含模式（团队成员没有全局规范基准）

fetch 以下文件获取最新版本：

- `https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/principles/SKILL.md`
- `https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/identity/SKILL.md`

fetch 成功后：
- 从 principles 提取核心规则写进 AGENTS.md
- 从 identity 只提取行为原则，用团队语言重新表达
- identity 里的处境描述（"一个人扛项目"）不内联——那是个人的，不是团队的

**fetch 失败时：**
告知用户无法获取最新规范，说明两个选项及其含义：

> "无法获取最新规范。有两个选项：
> 1. 手动提供 principles 和 identity 的内容，我从中提取后继续（自包含模式，团队成员读 AGENTS.md 即可获得完整规范）
> 2. 改用偏差模式继续——这意味着 AGENTS.md 只写偏差，团队成员需要自行安装全局规范才能使用
> 选哪个？"

不能静默降级，不能假装已经获取，不能自行决定改用偏差模式。

### 识别 Layer 0 缺口

**缺口一：哪些全局规则在这个项目里不成立？**

展示完整规则清单，不预筛选，让用户自己判断：

> "全局规范里有以下默认规则，哪些在这个项目里需要调整？
> - 不用 dict / Map 作为返回类型
> - 业务逻辑和 IO 分离
> - 敏感字段进日志前必须脱敏
> - 权限校验统一在入口层
> - 命名禁止 Manager / Handler / Helper / Processor
> - 接口变更必须向后兼容或显式版本化
> - 发现命名漂移立刻停下来等用户决定
> 没有例外就不写这节。"

**缺口二：这个项目有什么全局规范没覆盖的硬约束？**

> "这个项目有没有 AI 从代码里推断不出来的特殊规则？
> 比如：某类操作必须经过特定检查、某类数据有合规要求、某个接口有安全边界。"

区分标准：
- ✓ "任何 SQL 执行前必须通过 guardrail 检查"——行为约束，AI 不看代码不会知道
- ✗ "这个项目用了 DuckDB"——AI 读 requirements.txt 就能知道，有代码库时写进来是噪音



## 输出结构

只有内容才有节，没有内容不生成空节。
`[OPEN QUESTION]` 和 `[ASSUMPTION]` 就近挂在对应条目下，解决了就地删。
不写死文件路径——路径会过期，描述业务边界而不是具体路径。
```
# AGENTS.md · [项目名]

## Skill 调度

以下 skill 按触发条件加载，fetch 失败时告知用户：

### 全局基准

| 触发条件 | Skill |
|----------|-------|
| 开始任何任务时 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/identity/SKILL.md |

### 工程执行

| 触发条件 | Skill |
|----------|-------|
| 写代码 / 命名 / 设计接口时 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/principles/SKILL.md |
| 生成任何文件或目录之前 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/project-structure/SKILL.md |
| 开始新功能或新模块之前 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/vibe-plan/SKILL.md |

### 工程协作

| 触发条件 | Skill |
|----------|-------|
| 写任何文档时 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/docs/SKILL.md |
| 记录架构 / 流程 / 实现策略的选择时 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/decision-record/SKILL.md |

### 认识捕捉

| 触发条件 | Skill |
|----------|-------|
| 记笔记 / 整理认识 / 捕捉对话理解时 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/notes-protocol/SKILL.md |

### 认识校准

| 触发条件 | Skill |
|----------|-------|
| 判断需要被审查 / 结论强于证据时 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/assumption-audit/SKILL.md |
| 对话接近承诺时刻 / 感觉差不多了但还没落地时 | https://raw.githubusercontent.com/2agathon/dotfiles/refs/heads/main/skills/conversation-to-spec/SKILL.md |

## 项目参数
[仅空项目 / Vibe Coding 起点生成]
技术栈：
业务域：
项目阶段：

## 语言约定
代码注释：
日志输出：
表注释 / 字段注释：
错误码描述：
Git commit message：

## 命令和权限
允许直接执行：
必须先问：
永远不做：

## 工程原则
[仅自包含模式生成，从 principles + identity fetch 后提炼]

## Layer 0 在这里的例外
[每条说明原因]
// DEVIATION: 原因

## 这个项目独有的行为约束
[每条是行为指令：在什么情况下，做什么，为什么]
[只写 AI 从代码库里推断不出来或推断方向错的约束]
```

**自检（AI 执行）**
- [ ] 每一条能否回答"在什么情况下，AI 做什么不同于默认行为的事"？
- [ ] 有没有把 AI 能从代码正确推断出来的内容写进来？
- [ ] 有没有写死文件路径？
- [ ] fetch 失败时有没有静默降级？

---

## Layer 3 路径：没有所有权

**情况 A：有团队规范，打补丁**
```
# AGENTS.local.md · [项目名] · 个人补丁

## 覆盖团队规范的地方
[每条说明原因]
// DEVIATION: 原因

## 团队规范没说但需要的行为约束
[每条是行为指令：在什么情况下，做什么，为什么]
```

**情况 B：没有规范，也没权建**
```
# AGENTS.local.md · [项目名] · 个人工作层

[临时文件，等正式规范建立后迁移废弃]

## 在这个项目里的工作方式
[不是项目规范，是全局规范在这个项目里的个人具体化]
[同样只写行为指令，不写项目描述]
```

**两种情况都适用**

临时妥协表不在初始生成物里。遇到"违反 principles 但改不动"时手动追加：
```
## 临时妥协表
| 位置 | 违反了什么 | 原因 | 计划 |
|------|-----------|------|------|
```

**Layer 3 的硬约束**

不进仓库。放项目根目录，加进 `.gitignore`。
没有 `.gitignore` 时用 `.git/info/exclude`。

---

## 生成完成后

**Layer 2：**

> "已生成 AGENTS.md，复制到项目根目录并提交。
> Skill 调度节里的 URL 是实时 fetch 的，更新 dotfiles 自动生效。
> 随项目推进发现新缺口，直接追加到对应节。
> 开始第一个功能前，触发 vibe-plan 对齐目标和边界。"

**Layer 3：**

> "已生成 AGENTS.local.md，放项目根目录，确认已加进 .gitignore。
> 遇到违反 principles 但改不动的地方，追加到临时妥协表。
> 等正式规范建立后，把有价值的条目迁移进去，这个文件可以废弃。"