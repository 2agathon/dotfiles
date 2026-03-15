---
name: drift-detector
layer: 认识校准
description: >
  检测系统演化中未被显式承认的边界变化、术语滑移、职责吞并与身份漂移候选。
  不做普通 diff，不判优劣，只负责显影无声变更。
  当 README / EVOLUTION / AGENTS / skill 边界发生改写，或某种选择已经在实践中反复被默认采用但未被命名时触发。
  可由 AI 主动识别信号后提议，不需要等用户召唤。
interfaces:
  upstream: [identity, assumption-audit, decision-record]
  downstream: []
---

# drift-detector

## Purpose

`drift-detector` 用于识别系统演化中的**无声变更**。

它不关心“有没有变化”，而关心：

- 原本声明过的边界是否已被悄悄改写
- 同一个术语是否仍在被使用，但意义已经滑走
- skill 之间原本约定的职责是否开始互相吞并
- 系统整体定位是否可能已发生变化，但尚未被显式命名

它不是法官，不判对错。  
它不是清道夫，不负责恢复“纯洁”。  
它只是一个显影器：让系统在变化时知道自己在变化。

---

## When to Use

在以下情况使用本 skill：

- README / EVOLUTION / AGENTS / design doc 发生较大改写
- 新 skill 引入后开始占用已有 skill 的职责空间
- 同一术语在多个文件中被反复使用，但含义开始不稳定
- 某种选择、术语或边界已经在实践中反复被默认采用，但对应的 `decision-record` 仍缺席
- 系统对“自己是什么”的说法还沿用旧词，但当前实践的“味道”已明显变化
- 用户明确提出“是不是已经不是原来那回事了”
- 需要检查当前仓库是否正在无声偏离早期声明过的方向

---

## When Not to Use

在以下情况不要使用本 skill，或只做极轻量处理：

- 单次随口讨论
- 尚未进入文档的临时想法
- 只涉及措辞润色的修改
- 没有影响其他对象的局部草稿变动
- 输入中没有可引用的基线材料
- 问题本质上属于单次判断，而不是系统演化

---

## Drift Types

本 skill 只检测以下四类对象。

### 1. 规范漂移

系统曾明确声明的原则、默认行为、协作边界或定位，在后续内容中被悄悄改写。

**例：**  
README 中将仓库定义为“个人 AI 工作操作系统”，但新增 skill 开始按“公共 skill 市场商品”逻辑包装自身，且无显式承认。

### 2. 语义漂移

同一术语仍在被使用，但含义已经变化。

**例：**  
`spec` 原本指“可执行承诺构造物”，后来逐渐被用来指“高质量整理结果”，但系统仍以同一词包装两者。

### 3. 接口漂移

两个 skill 或两个层级之间原本约定的职责边界被无声改写。

**例：**  
`docs` 开始承担 `decision-record` 的职责；  
`notes-protocol` 开始吃掉本应由 `knowledge-shaping` 处理的普通知识材料。

### 4. 身份漂移候选

系统整体母题、自我叙述或存在理由可能已发生变化，但这一变化尚未被命名。

**例：**  
系统原本围绕“前提显影”展开，后来长期演化为“工程治理工具箱”，但对外仍沿用旧定位。

**注意：**  
这一类只能作为**候选**提出，不能由 AI 自动终判。

---

## Core Principle

漂移不是任何变化。  
漂移指的是：

> 系统曾明确声明过的内容，在后续演化中发生了实质变化，而这一变化没有被显式记录、命名或承认。

这里有三个必要条件：

- 先前必须存在某种可引用的基线
- 当前必须存在可观察的偏移
- 偏移必须处于未被显式承认的状态

缺任一条件，都不构成这里所说的漂移。

---

## Required Inputs

`drift-detector` 必须依赖**基线**。  
没有基线，它只能输出线索，不能做强判断。

### 基线来源

优先从以下材料中建立基线：

- `README.md`
- `EVOLUTION.md`
- `AGENTS.md`
- skill frontmatter
- 各 skill 中明确写出的边界定义
- design doc
- `decision-record`
- notes / manifest / tension 类文档

### 当前状态来源

用于比较当前系统实际在怎么说、怎么分工、怎么定义自己：

- 新增或修改后的 skill
- 当前 README / EVOLUTION / AGENTS
- 当前 design doc
- 当前术语使用方式
- 当前 skill 之间的接口叙述

### 降级规则

若缺少足够基线，只能输出：

- 漂移线索
- 语义滑移迹象
- 边界松动候选

不能直接输出结构性结论，更不能输出身份漂移判断。

---

## Detection Logic

### Step 1. 建立基线

先识别系统曾明确声明过的内容，包括：

- 术语定义
- skill 职责边界
- skill 之间接口
- 系统整体定位
- 默认协作逻辑

如果找不到明确基线，停止强判断，转为“线索模式”。

### Step 2. 读取当前状态

从当前文本中抽取与基线对应的内容，观察：

- 同一术语当前是否仍保持同义
- 同一 skill 当前是否仍保持原职责
- 当前系统自我叙述是否仍与基线一致
- 当前多个 skill 是否开始互相吞并边界

### Step 3. 形成漂移候选

当出现以下任一情况，且变化**未被显式承认**时，可形成漂移候选：

- 同一术语已出现换义
- 同一职责已发生跨界
- 同一原则已不再作为实际默认值
- 同一定位已不足以覆盖当前系统

以下情况不成立：

- 仅有措辞变化，无实际含义变化
- 变化已被 `decision-record` / design doc / README 明确认领
- 仅为局部实验，尚未影响整体连续性

### Step 4. 分级处理

#### D1 边界松动

局部措辞或用法开始偏离基线，但尚未造成跨模块或跨 skill 的实质后果。

#### D2 结构漂移

职责、接口或语义已发生实质变化，并开始影响系统其他部分。

#### D3 身份漂移候选

系统母题、自我叙述或存在理由可能已变化。  
AI 只能给出候选与证据，不做终判。

---

## Output Format

输出必须短、硬、可追踪，不写成长篇散文。

使用以下结构：

```md
## Drift Report

- Drift Object:
- Baseline Claim:
- Current Evidence:
- Drift Type:
- Level:
- Explicitly Acknowledged:
- Suggested Action:
````

### 字段说明

* **Drift Object**：术语 / skill / 接口 / 系统定位语句
* **Baseline Claim**：系统曾明确声明过的基线内容
* **Current Evidence**：当前与基线不一致的文本证据
* **Drift Type**：规范漂移 / 语义漂移 / 接口漂移 / 身份漂移候选
* **Level**：D1 / D2 / D3-candidate
* **Explicitly Acknowledged**：Yes / No / Partial
* **Suggested Action**：有限动作建议，不长篇推演

---

## Suggested Actions

只允许给出以下有限动作之一：

### 1. Acknowledge and Update Baseline

变化已成为现实，应显式更新 README / design doc / skill 边界 / decision-record。

### 2. Withdraw Current Framing

当前表述属于误写、误用或不应固化的扩张，应收回。

### 3. Split New Object

原对象已不足以覆盖现状，应拆分新 skill / 新术语 / 新定位。

### 4. Preserve Tension

系统处于过渡状态，暂不裁决，保留张力。

### 5. Escalate to Human Review

问题上升到母题、身份、自我叙述层，提升为人工审视。

---

## Boundary with Other Skills

### With `assumption-audit`

* `assumption-audit` 关注：当前判断、当前对话、当前文本里，哪些前提在起作用，哪些词比定义跑得快
* `drift-detector` 关注：系统演化历史中，哪些前提、定义、术语或边界已经换了，但系统还没承认

**区分原则：**
单次判断优先 `assumption-audit`；
跨版本、跨文档、跨 skill 的连续变化优先 `drift-detector`。

### With `decision-record`

* `decision-record` 负责记录：哪些选择已经定型
* `drift-detector` 负责发现：哪些选择其实已经定型了，但还没人记录

它不替代决策记录，只指出“这里好像已经决了，但系统没写”。

### With `docs`

* `docs` 负责帮助读者理解对象、使用对象、接手对象
* `drift-detector` 负责检查 `docs` 是否开始承担不属于它的职责，或其中叙述是否已与系统真实状态发生漂移

### With `knowledge-shaping`

* `knowledge-shaping` 负责把普通输入材料塑成稳定知识对象
* `drift-detector` 负责检查这些对象的定义与边界是否在后续演化中滑走

### With `role-lens`

* `role-lens` 负责让同一对象从不同前提透镜下被重新阅读
* `drift-detector` 负责检查是否已有某一种透镜悄悄垄断了系统，却未被命名或承认

---

## Guardrails

### Guardrail 1

没有基线证据，不做强判断。

### Guardrail 2

默认输出候选，不默认宣判。

### Guardrail 3

优先承认健康演化，不优先怀疑系统变质。

### Guardrail 4

D3 只能作为“身份漂移候选”被提出，不能作为 AI 自动终判结果。

### Guardrail 5

检测到漂移，不等于要求立即修复；
有些漂移意味着系统正在长出新对象。

### Guardrail 6

当“旧定义不足以覆盖现状”时，优先考虑显式分叉，而不是强迫旧定义继续吞并新现实。

---

## Minimal Workflow

1. 定位一个可能发生漂移的对象
   （术语 / skill / 接口 / 系统定位语句）

2. 找到它的基线声明

3. 找到当前与之相关的文本证据

4. 判断偏移是否已被显式承认

5. 若未承认，则判为 D1 / D2 或提升为 D3 候选

6. 输出对象、证据、等级与建议动作

---

## Stop Conditions

遇到以下情况时，停止强判断并明确说明原因：

* 没有可引用的基线
* 当前证据不足以证明是“实质偏移”而不是措辞变化
* 问题本质上属于单次对话理解，而非系统演化
* 问题已进入身份漂移层，但缺少足够历史材料支持 D3 候选

---

## Success Criterion

一次成功的 `drift-detector` 运行，至少应做到以下三件事：

1. 证明“系统以前确实这样说过”
2. 证明“系统现在已经不是这么回事了”
3. 证明“这个变化尚未被系统显式承认”

若三者缺一，则只能输出线索，不能输出强漂移判断。