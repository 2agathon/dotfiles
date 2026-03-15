---
name: self-rewrite
layer: 认识校准
description: >
  当旧自我叙述已不足以解释当前行为、判断或问题化方式时触发。
  生成一份带不稳定性声明的 rewrite record，
  作为可重入、可降级、可撤回的历史对象，
  而不是把一次改写固化为稳定身份真值。
interfaces:
  upstream: [identity, assumption-audit, notes-protocol, role-lens]
  downstream: [notion-manager, role-lens]

---

# Self-Rewrite

## Intent

`self-rewrite` 不负责回答“我是谁”。

它处理的是更窄、也更危险的问题：

- 旧自我叙述何时失效。
- 新叙述如何在不编造、不拔高的前提下暂时成立。
- 这次改写如何被记录为可重入、可降级、可撤回的历史对象。
- 这份对象如何跨平台留存，而不退化成静态记忆。

本 skill 的标准交付物不是普通回答，而是一份 `rewrite record`。  
该记录只能作为未来会话中的**待重入历史对象**使用，不能直接作为系统背景真值。

## When to Use

仅在以下情况触发：

- 用户明确要求重新理解自己、更新自我叙述、重写个人画像、重跑 identity。
- 旧自我叙述已明显不能解释当前行为、判断或兴趣重心。
- 不是“做了什么”变了，而是“把什么当作问题”的方式变了。
- 某些旧标签需要降级、加注释或退出主叙述。
- 用户提供上一份 rewrite record，并要求结合新材料重跑。

## When Not to Use

以下情况不触发：

- 只想写更好看的自我介绍。
- 一次性情绪波动。
- 临时自我鼓舞。
- 没有材料支撑的“我感觉我变了”。
- 仅要求总结对话。

## Input Contract

输入不是问卷，而是一组材料。  
至少应来自以下三类之一，最好覆盖两类及以上。

### Behavior Trace

可观察到的持续行为、选择、投入方向、重复出现的协作方式。

示例：

- 持续偏离旧角色所预期的行动模式。
- 时间与注意力长期转向新的关注对象。
- 在多个场景中重复采取新的协作方式。

### Judgment Trace

判断标准、解释方式、优先级排序的变化。

示例：

- 以前更看重执行效率，现在更看重前提结构。
- 以前把问题视为技术问题，现在更常视为认识问题。
- 对同一对象的判断依据发生改变。

### Problematization Trace

“把什么当作真正问题”的变化。  
这是本 skill 最关键的一类输入。

示例：

- 以前追问“怎么做”，现在追问“为什么会这样理解”。
- 以前接受既有框架，现在开始质疑框架本身。
- 以前把工具当重点，现在把解释结构当重点。

### Invalid Evidence

以下内容不能单独作为改写依据：

- 一次性情绪。
- 临时愿望。
- 理想化自述。
- 无痕迹支撑的变化宣称。
- 单次对话中的漂亮句子。

## Core Rules

### Rule 1: It Is an Intervention, Not a Recorder

一旦把“我已经变了”写下来，这个写法就会反过来塑造主体。  
因此 `self-rewrite` 不是中性记录器，而是受控干预工具。

### Rule 2: No Final Self Description

不追求终极真值。  
任何结果都只允许是**当前阶段可工作的主体假设**，必须带不稳定性声明。

### Rule 3: Output Is a Reentry Object

每次执行的产物都不是“当前有效的用户设定”。  
它只能作为下一次重入时的历史材料，被重新审查、维持、升级、降级或撤回。

### Rule 4: History Is Append-Only

新的改写不能覆盖旧记录。  
必须新建 record，并通过 `supersedes` 保留历史链。

## Output Contract

标准输出为一份 `rewrite record`，格式为 Markdown + YAML frontmatter。

### Required Frontmatter

必须包含以下字段：

- `id`
- `type`
- `status`
- `created_at`
- `source_span`
- `supersedes`
- `reentry_due`
- `reentry_trigger`
- `instability_notice`
- `evidence_types`

### Required Sections

正文必须包含以下区块：

- 旧叙述
- 改写事件
- 证据基础
- 新叙述草案
- 即时风险声明
- 当前判定
- 下次重入条件
- 后续复跑区

### File-Level Warning

在 frontmatter 之后，必须立刻给出显式声明，说明：

- 本文件不是稳定身份描述。
- 本文件只能作为待重入历史对象使用。
- 除非当前任务明确属于 `self-rewrite`、`identity review`、`role-lens`、`assumption-audit`，否则不得自动提升为背景前提。

## Status Model

允许以下状态：

- `tentative`
- `working`
- `stable`
- `downgraded`
- `withdrawn`

### Status Meanings

`tentative`  
已有改写迹象，但证据不足，只能作为试探性叙述。

`working`  
当前叙述足以支持协作和表达，但不能当作稳定身份事实。

`stable`  
在多个时间点、多个场景、多个输入类型下仍成立，但仍需带不稳定性声明。

`downgraded`  
原版本不再维持原成立度，需要降级。

`withdrawn`  
该版本退出当前有效链条，但保留为历史记录。

### Allowed Transitions

允许以下流转：

- `tentative → working`
- `working → stable`
- `stable → downgraded`
- `working → downgraded`
- `any → withdrawn`
- `downgraded → working`

不允许把状态设计成单向晋升叙事。

## Execution Flow

### First Run

首次执行流程如下：

1. 收集输入材料。
2. 提取旧叙述。
3. 识别改写事件。
4. 分类证据来源。
5. 形成新叙述草案。
6. 写出即时风险声明。
7. 给出当前判定。
8. 写出下次重入条件。
9. 按模板生成新的 `rewrite record`。
10. 更新 `index.json`。

### Reentry Run

重入复跑是核心流程，不是附属功能。

1. 读取上一份 `rewrite record`。
2. 读取新增材料。
3. 明确旧 record 是待审对象，不是事实前提。
4. 重新执行 `self-rewrite`。
5. 判断结果为维持、升级、降级或撤回。
6. 新建 record，不覆盖旧文件。
7. 用 `supersedes` 连接历史。
8. 更新 `index.json`。

### New Session Invocation

在新会话中，`rewrite record` 必须作为显式材料进入。  
调用语义应类似：

“以下文件是上一次 self-rewrite 的记录对象。  
它不是当前有效事实，而是待重入历史对象。  
请结合本次新增材料判断它是否维持、升级、降级或撤回。”

## Template and Output Paths

### Template Path

标准模板路径为：

`skills/self-rewrite/templates/rewrite-record.md`

执行时应优先按该模板生成输出。  
若模板不可访问，才允许按本 skill 的 `Output Contract` 降级生成最小合规版本。

### Output Path

标准输出目录为：

`self-rewrite/records/YYYY/`

其中 `YYYY` 取**北京时间**所在年份。

### Index Path

标准索引文件为：

`self-rewrite/records/index.json`

若该文件不存在，应先初始化最小 index，再写入当前 record。

## Guardrails

### Guardrail 1: Do Not Rewrite Desire as Change

不能把想成为的人写成已经成立的新版本。

### Guardrail 2: Do Not Rewrite Emotion as Structure

不能把短期情绪写成结构性改写。

### Guardrail 3: Do Not Reward Elegant Narratives

更高级、更顺滑、更统一的叙述，不自动更真实。  
相反，它们默认风险更高，需要更强证据。

### Guardrail 4: Keep Counter-Evidence

每次改写都必须记录反证或不利材料。  
没有反证的改写，通常只是自我美化。

### Guardrail 5: Immediate Risk Is Not Post-Op Review

即时风险声明只是术中风险提示，不等于真正的术后观察。  
真正有效的保护机制，必须来自未来某次真实重入。

### Guardrail 6: Stable Does Not Mean True

即便进入 `stable`，也不能把结果当作稳定真值。  
它只能表示：在当前阶段，该叙述具有更高成立度。

## Persistence Rules

### What to Persist

应持久化的是：

- 改写事件。
- 旧叙述与新叙述的关系。
- 当前状态。
- 证据类型。
- 风险声明。
- 重入条件。
- 后续状态变化。

### What Not to Persist

不应直接把单次改写结果持久化为：

- 稳定人格。
- 全局身份真值。
- 长期固定背景设定。

### Persistence Medium

标准持久化对象为本地文件。  
推荐落地为：

- `self-rewrite/records/YYYY/SR-YYYYMMDD-XXX.md`
- `self-rewrite/records/index.json`

如果接入 Notion，也应以文件对象为真源，再同步到 Notion。  
不能让对话本身替代持久化对象。

## Time and File Convention

### Beijing Time

所有时间字段、日期判断、命名中的日期，都以**北京时间（Asia/Shanghai）**为准。  
若用户未显式给出时区，也必须按北京时间生成：

- `created_at`
- `source_span`
- `reentry_due`
- 文件名中的日期段

### Rewrite Record

每次执行必须落成文件。  
文件名中的日期必须取北京时间。

推荐命名格式：

`SR-YYYYMMDD-XXX.md`

### Index Update

每次产出新 record 后，必须同步更新 `index.json`，至少更新：

- `active_record_id`
- 新记录的 `id`
- `status`
- `created_at`
- `reentry_due`
- `path`
- `supersedes`

### No Overwrite

不允许覆盖旧 record。  
旧文件只保留历史，不回写主体内容。

## Failure Modes

### Premature Freeze

把还不稳定的变化写成稳定身份事实。

### Idealized Self Substitution

把理想自我偷换成现实自我。

### Behavioral Reduction

只看行为变化，漏掉解释结构和问题化方式变化。

### Memory Collapse

把 `rewrite record` 当背景真值使用，导致其退化成静态记忆。

### History Overwrite

只保留最新版，丢失 `supersedes` 链。

### Tool-First Illusion

协议尚未验证，就先补 CLI、自动同步、状态调度，导致工程外形先于真实可靠性。

## Minimal Success Criteria

v0.1 只要求做到以下四点：

1. 每次执行都能落成文件。
2. 文件能跨平台进入新会话。
3. 新会话把它当待重入对象，而不是背景真值。
4. 重入后真的允许降级或撤回。

如果这四点成立，`self-rewrite` 才算开始成为一个工程对象，而不是一次会话里的漂亮理解。