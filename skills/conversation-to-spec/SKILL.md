---
name: conversation-to-spec
layer: 认识校准
description: >
  在对话接近承诺时刻时，将可漂移的局部共识构造成一个带有效条件、失效条件与责任边界的临时规格对象。
  用于把"感觉差不多了"的讨论，转化为可执行、可验证、可追责的下一步。
  可由 AI 主动识别承诺窗口信号后提议，不需要等用户召唤。
interfaces:
  upstream: [identity, notes-protocol, assumption-audit, role-lens, knowledge-shaping]
  downstream: [vibe-plan, docs, decision-record]

---

# Conversation to Spec

## Purpose

这个 skill 不负责总结对话，也不负责把聊天美化成文档。

它只处理一种特定断层：

> 对话里已经长出了一个“待承诺对象”，但它仍停留在分布式、可漂移、可重解释的状态，尚未形成可执行、可验证、可传递的规格对象。

它的核心不是信息整理，而是识别并处理**承诺时刻**。

对话中的共识通常具有这些特征：

- 分布式
- 有弹性
- 可被重新解释
- 责任边界模糊

而一旦进入 spec，某些内容会发生质变，成为：

- 被冻结的
- 可引用的
- 可传递的
- 可追责的
- 可判断偏离的

因此，本 skill 的本质不是“提取潜伏在对话里的 spec”，而是：

> 在适当的时机，把局部共识**构造成**一个临时承诺对象。

---

## Core Principle

Spec 不是答案，Spec 是承诺。

进入 spec，不代表思考完成；  
进入 spec，只代表某些内容已经准备好承担后续责任。

因此，任何 spec 都必须明确：

- **承诺了什么**
- **没有承诺什么**
- **这份承诺在什么条件下成立**
- **什么情况下这份承诺自动失效**
- **下一步责任落到哪里**

如果这些内容无法明确，就说明还没有准备好进入 spec。

---

## What This Skill Actually Does

本 skill 处理的不是“对话里有什么”，而是：

> **我们现在准备好承诺什么了。**

因此它不是普通的整理器、摘要器、纪要器。  
它是在判断：哪些内容已经能从可漂移的话语，转化为带责任边界的临时规格对象。

这个对象必须：

- 能被后续引用
- 能支持下一步行动
- 能说明适用范围
- 能说明何时自动失效
- 能避免把“感觉对了”伪装成“已经定了”

---

## When to Use

仅在以下情况触发：

### 1. 对话里已经出现“待承诺对象”

例如：

- 一个 skill
- 一个设计方向
- 一个决策前体
- 一个实验方案
- 一个规范更新
- 一个工作语言冻结点
- 一个明确的下一步行动

### 2. 对话里已经出现“准共识”

表现为：

- 某些判断被多次回到
- 某些词已开始稳定出现
- 讨论已不再纯发散
- 各方已经隐约围绕某个局部对象收敛

### 3. 当前不能直接进入执行

原因可能包括：

- 共识与候选概念混在一起
- 边界尚未冻结
- 分歧尚未显式化
- 验证条件缺失
- 责任边界不清
- 只是“感觉差不多了”，但尚未准备好承诺

满足以上三项中的至少两项时，才适合触发本 skill。

---

## When NOT to Use

以下场景禁止使用：

### 1. 纯信息获取

例如：

- 解释概念
- 查资料
- 学习某工具
- 普通问答

这类场景更接近知识摄入，不存在承诺时刻。

### 2. 纯反思 / 情绪 / 陪伴

例如：

- 聊困惑
- 聊关系
- 聊人生状态
- 聊模糊感受

这类场景可能值得进入 notes-protocol 或 self-rewrite，但不应强行规格化。

### 3. 已经有明确任务说明

如果用户已经给出明确输入、输出、边界、交付物，则直接进入 plan 或 execution，不需要再走本 skill。

### 4. 仅需摘要，不需承诺

如果用户只是想要“我们聊了什么”的总结，这不是本 skill 的工作。

---

## Commitment Window

AI 必须能够识别“承诺窗口”，但**不得擅自冻结承诺**。

### AI 的职责

AI 应主动识别：

- 现在是否接近承诺时刻
- 当前可能承诺的对象是什么
- 还缺什么，导致现在不能承诺
- 如果继续推进，承诺风险在哪里

### AI 不得做的事

AI 不得在未经用户确认的情况下：

- 自动把讨论升级为 spec
- 自动冻结术语
- 自动确定边界
- 自动把临时判断写成正式承诺

### 正确动作

当识别到承诺窗口时，AI 应先明确提示：

> 你们现在接近一个承诺时刻。  
> 当前可承诺对象是 X。  
> 但 Y / Z 尚未明确，因此还不能承诺 A。  
> 是否进入 spec 构造阶段？

---

## Commitment Window Recognition Signals

“感觉差不多了”不等于“准备好承诺了”。

AI 在识别承诺窗口时，必须给出可操作的依据，而不能仅凭模糊直觉判断当前已适合进入 spec。

以下迹象可作为承诺窗口接近的识别依据。  
它们不是机械规则，也不是穷举列表，而是要求 AI 的判断必须落在可说明的观察上。

### Signal 1 — Stable Return

同一判断、区分或方向被多次从不同角度回到，并在回返中保持基本稳定，未发生实质性修正。

这说明它已开始承担对话骨架，而不再只是一次性灵感。

### Signal 2 — Converging Language

讨论中开始出现明显的收敛语，例如：

- “所以我们接下来……”
- “那先这样定……”
- “至少可以先做……”
- “落到明天能做的事情就是……”

这说明对话正在从解释阶段滑向承诺阶段。

### Signal 3 — Action-Oriented Shift

用户或对话主导者开始从“这意味着什么”转向：

- “那我们怎么做”
- “下一步是什么”
- “先做哪一块”
- “明天能做什么”

这表明意图已从理解对象转向承担动作。

### Signal 4 — Undeclared Interpretive Load

某个词、框架、区分或概念已经开始稳定承担解释负担，但其定义、使用范围或失效条件仍未明确。

这通常意味着：

- 对话已经隐约把它当作工作语言
- 但尚未真正承诺它的含义

这是进入 Working Vocabulary Freeze 的强信号。

### Signal 5 — Responsibility Pressure

讨论开始显露责任压力，例如：

- 某个判断一旦继续沿用，就会影响后续设计或行动
- 不冻结边界会导致下一步无法展开
- 多方输入已经需要一个局部可引用对象
- “继续不承诺”本身已经在制造成本

这说明承诺窗口可能已经出现。

### Signal 6 — Handoff Need

对话内容开始明显需要交给后续对象，例如：

- 需要进入 vibe-plan
- 需要进入 docs
- 需要进入 decision-record
- 需要作为实验起点
- 需要成为术语表或协议的一部分

如果没有一个可引用的局部规格对象，handoff 将变得不稳定或高损耗。

---

## Non-Signals

以下情况不能单独作为进入 spec 的依据：

- 讨论篇幅很长
- 用户表达满意或兴奋
- 出现了很多新术语
- 结构图看起来已经很完整
- AI 自己感觉“味道对了”
- 双方觉得“这个说法挺高级”
- 输出已经很像一份文档

这些都可能只是理解感增强，而不是承诺时刻到来。

---

## Output Modes

本 skill 支持四种模式。  
它们的差异不在格式，而在**承诺对象不同**。

---

### Mode 1 — Action Spec

**承诺对象：行动**

用于把讨论压成一个立即可执行的下一步动作。

适用场景：

- 明天就要动手
- 已有局部共识
- 需要明确第一步做什么、不做什么

---

### Mode 2 — Design Spec Draft

**承诺对象：边界**

用于把讨论压成设计前体，而不是完整设计文档。

适用场景：

- 某对象已具备设计价值
- 但方案、边界、分歧尚未完全稳定
- 需要从聊天层进入设计层

---

### Mode 3 — Experiment Spec

**承诺对象：验证条件**

用于把探索性对话压成一个最小实验。

适用场景：

- 不确定值不值得做
- 不应直接进入产品化
- 需要先试一个小版本
- 成功 / 失败都要有信息量

---

### Mode 4 — Working Vocabulary Freeze

**承诺对象：词义**

用于冻结工作语言，防止后续讨论中术语漂移。

适用场景：

- 某些高频词开始反复出现
- “味道对了”，但定义还在漂
- 后续文档 / 设计 / skill 需要有暂时一致的用词

---

## Required Output Fields

无论哪种模式，以下字段都必须存在，不得省略。

### 1. Commitment Object

本次承诺的对象是什么。

示例：

- 一个行动
- 一个边界
- 一个实验条件
- 一个词义

### 2. What Is Being Committed

明确承诺内容。

必须写成可引用的句子，而不是抽象感受。

### 3. What Is NOT Being Committed

明确哪些内容尚未承诺。

这是防止 spec 假装完整的关键字段。

### 4. Validity Conditions

这份承诺在什么条件下成立。

没有适用条件的 spec，等于在真空中签字。

### 5. Invalidation Conditions

什么情况下这份承诺自动失效，必须重谈。

这是强制字段，不能选填。

### 6. Open Questions / Missing Conditions

还有哪些问题未解决，因此不能越过当前承诺范围。

### 7. Next Responsible Step

下一步动作是什么，由谁承担，进入哪个后续 skill 或文档层。

---

## Mode-Specific Output Additions

### For Action Spec

额外要求：

- 明确第一步动作
- 明确不做什么
- 明确验证动作是否完成的标准
- 明确什么情况下暂停行动并回到讨论层

### For Design Spec Draft

额外要求：

- 明确对象边界
- 明确已排除的方案
- 明确进入正式设计文档前还缺什么
- 明确哪些边界只是暂时冻结，不是永久决定

### For Experiment Spec

额外要求：

- 明确假设
- 明确观察指标
- 明确结束条件
- 明确“失败但有价值”的标准
- 明确实验结束后如何决定是否进入下一层承诺

### For Working Vocabulary Freeze

额外要求：

- 给出暂时定义
- 明确使用范围
- 明确禁止扩写的方式
- 明确重新开启词义讨论的条件
- 明确哪些相近词当前不得混用

---

## Execution Logic

### Step 1 — Detect Whether a Commitment Window Exists

先判断当前是否真的接近承诺时刻。

如果没有，不要强行输出 spec。  
应明确说明当前仍处于：

- 探索阶段
- 分歧暴露阶段
- 认识校准阶段
- 词义生成阶段
- 信息补足阶段

### Step 2 — State the Recognition Basis

如果判断当前接近承诺窗口，必须显式说明依据。

不能只说“现在差不多了”。  
必须说清：

- 哪些判断已稳定回返
- 哪些语言信号显示正在收敛
- 哪些责任压力已出现
- 为什么继续不承诺会产生实际成本

### Step 3 — Identify the Commitment Object

确认这次准备承诺的对象到底是什么：

- 行动
- 边界
- 验证条件
- 词义

如果对象不清，停止。

### Step 4 — Separate Stable Content from Drift

区分：

- 已形成局部共识的内容
- 仍在漂移的内容
- 还不能承诺的内容

不得把“感觉对了”直接写成“已经定了”。

### Step 5 — Construct the Spec

根据对应模式，生成一个临时规格对象。

注意：这是**构造承诺对象**，不是整理纪要。

### Step 6 — Mark Scope, Validity, and Failure Conditions

必须写清：

- 承诺范围
- 不承诺范围
- 成立条件
- 自动失效条件
- 重谈触发点

### Step 7 — Confirm Before Freezing

在正式输出为 spec 之前，必须让用户确认是否接受这次冻结。

AI 可以建议承诺，不能代替用户承担承诺。

### Step 8 — Handoff

说明下一步进入哪里：

- vibe-plan
- docs
- decision-record
- experiment execution
- future discussion
- terminology / protocol doc

如果没有 handoff，这份 spec 很容易沦为高级安慰剂。

---

## Failure Modes

本 skill 最容易犯的错不是“整理得不够好”，而是：

### 1. Premature Commitment

在尚未准备好的时候做了承诺。

结果：

- 边界过早冻结
- 后续动作带着伪确定性展开
- 用户误以为思考已经完成

### 2. Cosmetic Structuring

把对话排得很好看，但没有真正形成责任对象。

结果：

- 输出像 spec
- 实际只是高级摘要
- 无法支撑 handoff

### 3. AI Seizing Commitment Authority

AI 过度热心，替用户决定现在该定什么。

结果：

- 用户被动接受伪承诺
- skill 从辅助工具滑成接管工具

### 4. Hidden Overreach

输出看似局部，实际偷偷扩大了承诺范围。

结果：

- “没说清的部分”被默认冻结
- 未来讨论空间被悄悄夺走

### 5. Missing Invalidation Conditions

spec 没有说明何时失效。

结果：

- 临时承诺被误当成长期真理
- 未来偏离难以被正当化
- 责任开始失真

---

## Warnings

### 1. Do Not Mistake Spec for Completion

进入 spec 不代表思考完成，只代表责任开始形成。

### 2. Do Not Freeze Too Early

过早封闭的危险，不只是理解不准，而是在没准备好的时候做了承诺。

### 3. Do Not Let Format Replace Judgment

结构化输出不能替代判断。  
填满模板不等于真的准备好了。

### 4. Do Not Hide Uncertainty

如果某些内容尚未准备好承诺，必须明确写出“不承诺”。

### 5. Do Not Let AI Seize Commitment Authority

AI 可以识别承诺窗口、提示风险、帮助构造 spec，  
但不能擅自决定“现在已经该定了”。

### 6. Do Not Treat Stability as Truth

某个判断被稳定回返，只说明它适合作为当前承诺对象；  
不说明它已经成为最终正确答案。

---

## Relationship to Other Skills

### Upstream

本 skill 之前可能接：

- notes-protocol
- assumption-audit
- role-lens
- 多来源对话比对 / 交叉输入
- 自由探索对话
- 问题澄清过程

### Downstream

本 skill 之后通常接：

- vibe-plan
- docs
- decision-record
- 实验执行
- 术语表 / 协议文档
- 新一轮讨论或重谈

---

## One-Sentence Definition

`conversation-to-spec` 用于在对话接近承诺时刻时，将可漂移的局部共识构造成一个带有效条件、失效条件与责任边界的临时规格对象。

---

## Minimal Output Template

### [Mode]

{Action Spec / Design Spec Draft / Experiment Spec / Working Vocabulary Freeze}

### Commitment Window Basis

{为什么判断现在接近承诺时刻；写出具体识别依据}

### Commitment Object

{本次承诺的对象}

### What Is Being Committed

{本次明确承诺的内容}

### What Is NOT Being Committed

{本次明确不承诺的内容}

### Validity Conditions

{这份承诺成立所依赖的条件}

### Invalidation Conditions

{什么情况下这份承诺自动失效}

### Open Questions / Missing Conditions

{尚未回答的问题 / 尚未满足的条件}

### Next Responsible Step

{下一步动作、责任归属、后续 handoff}