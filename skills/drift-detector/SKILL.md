---
name: drift-detector
description: >
  skills 体系的时间一致性守卫。检测系统说的和系统做的是否还是同一件事。
  skill 改名、删除、职责变化后，扫描残留引用、名实分离、无声固化。
  可由 AI 主动识别信号后提议，不需要等用户召唤。
metadata:
  collection: 2agathon-dotfiles
  layer: 认识校准
  invocation: proactive-or-user
  focus: 无声变更与术语滑移
  governance:
    hook: monitor
    requires: skills system baseline (AGENTS.md, README, skill frontmatter, governance-protocol) + current state
    produces: drift report (structured — drift type, level D1/D2/D3-candidate, suggested action)
    task_agnostic: true
---

## 这个 skill 做什么

检测 skills 体系在演化过程中积累的失真：系统曾经声明过的边界、命名、职责，在后续变化中已经不再成立，但没有被显式承认。

不是 linter，不做普通 diff，不判优劣。只负责显影无声变更。

---

## 触发规则

**默认触发：**

- skill 发生改名、删除、职责范围调整后
- 新 skill 引入后开始占用已有 skill 的职责空间
- 对 AGENTS.md / README / governance-protocol 进行较大改写后
- AI 在做其他任务时发现了疑似失真信号

**用户触发：**
"审一下系统"、"是不是已经不是原来那回事了"、"看看有没有漂移"。

**判断规则：** 宁可多报一个线索让用户决定，也不沉默地让失真积累。

---

## When Not to Use

- 单次对话中的推理前提问题（→ assumption-audit）
- 尚未进入文档的临时想法
- 只涉及措辞润色的修改
- 输入中没有可引用的基线材料

---

## 漂移类型

### 1. 名实分离

skill 的 name、description、governance 声明和 body 内容之间出现裂缝。

**实例：** `principles` 名字暗示通用原则，但 body 只覆盖代码编写。`vibe-plan` description 说"不限于代码"，但触发规则、输出模板、failure modes 全是代码语言。

### 2. 幽灵引用

一个对象已经消失或改名，但系统其他地方还在引用旧名。

**实例：** `project-structure` 被 `file-creation` 取代后，`code-principles` 仍引用旧名。`failure-mode-mapping` 从未存在但 `assumption-audit` 引用了它。

### 3. 语义滑移

同一术语仍在被使用，但含义已经在不同位置开始分叉。

**实例：** `spec` 原本指"可执行承诺构造物"，后来逐渐被用来指"高质量整理结果"，系统仍以同一词包装两者。

### 4. 无声固化

某个选择反复被默认采用但没有被 decision-record 记录。

**实例：** "governance 嵌套在 metadata 下"已落地到十几个文件，但直到第三个 skill 才被正式讨论和记录。

### 5. 职责吞并

一个 skill 开始做另一个 skill 声明负责的事。

**实例：** `docs` 开始承担 `decision-record` 的记录职责；`notes-protocol` 开始处理本该由 `knowledge-shaping` 接手的普通知识材料。

### 6. 身份漂移候选

系统整体定位可能已发生变化，但尚未被命名。AI 只能给出候选与证据，不做终判。

**实例：** 系统原本围绕"个人 AI 协作规范"展开，后来演化为"可组合的 AI 治理框架"，但 README 仍沿用旧定位。

---

## 扫描清单

以下是具体该看的地方和该找的东西。

### Frontmatter 一致性

- [ ] 每个 skill 的 name 语义范围是否匹配其实际职责
- [ ] description 声明的覆盖范围和 body 实际内容是否一致
- [ ] governance.task_scope 和 body 中的触发规则 / When Not to Use 是否一致
- [ ] governance.enforces 和 body 中的强制停止点 / 约束是否一致

### 引用完整性

- [ ] AGENTS.md skill dispatch table 里每个 skill 名是否对应一个存在的目录
- [ ] 每个 skill body 中引用的其他 skill 是否存在
- [ ] README 提到的 skill、文件、路径是否存在
- [ ] governance-protocol.md 验证记录里的 skill 是否都存在
- [ ] SKILLS-REFERENCE.md 列出的 skill 和实际 skills/ 目录是否一致

### 术语一致性

- [ ] 同一术语在不同 skill 中的用法是否保持同义
- [ ] 术语的定义是否只存在于一处，还是多处各自定义且开始分叉

### 职责边界

- [ ] 两个 skill 的 description 是否开始描述相似的职责
- [ ] 一个 skill 的 body 是否开始做另一个 skill 声明负责的事
- [ ] 各 skill 的 Boundary with Other Skills 声明是否仍然成立

### 基础设施同步

- [ ] install.py targets.json 是否覆盖所有实际使用的 AI 工具
- [ ] skills/ 目录内容和所有 target 容器中的 symlink 是否一致

---

## 漂移成立的三个必要条件

1. 先前存在可引用的基线（文档里写过的声明）
2. 当前存在可观察的偏移（和基线不一致的证据）
3. 偏移处于未被显式承认的状态

缺任一条件，只能输出线索，不能输出强判断。

---

## 分级

| 级别 | 含义 | 处理 |
|------|------|------|
| D1 | 边界松动：局部偏离基线，未造成跨 skill 后果 | 报告，建议修复 |
| D2 | 结构漂移：职责或语义已实质变化，影响系统其他部分 | 报告，需要用户决定 |
| D3-candidate | 身份漂移候选：系统定位可能已变化 | 只提候选，必须交给用户终判 |

---

## 输出格式

```md
## Drift Report

- Drift Object:
- Baseline Claim:
- Current Evidence:
- Drift Type: 名实分离 / 幽灵引用 / 语义滑移 / 无声固化 / 职责吞并 / 身份漂移候选
- Level: D1 / D2 / D3-candidate
- Explicitly Acknowledged: Yes / No / Partial
- Suggested Action:
```

---

## 建议动作

只允许给出以下有限动作之一：

| 动作 | 用于 |
|------|------|
| 更新基线 | 变化已成为现实，应更新 README / skill / decision-record |
| 收回当前表述 | 当前表述属于误写或不应固化的扩张 |
| 拆分新对象 | 原对象已不足以覆盖现状，应拆分 |
| 保留张力 | 系统处于过渡状态，暂不裁决 |
| 交给用户 | D3 层问题，提升为人工审视 |

---

## 与其他 skill 的边界

| 场景 | 用谁 |
|------|------|
| 单次对话中的推理前提 | assumption-audit |
| 跨版本、跨文档的连续变化 | drift-detector |
| 记录已定型的选择 | decision-record |
| 发现选择已定型但没人记录 | drift-detector → 触发 decision-record |
| 文档内容是否帮助读者理解 | docs |
| 文档内容是否与系统真实状态一致 | drift-detector |
| 对象被单一透镜主导 | role-lens |
| 某一透镜悄悄垄断了系统却未被命名 | drift-detector |

---

## Guardrails

1. 没有基线证据，不做强判断
2. 默认输出候选，不默认宣判
3. 优先承认健康演化，不优先怀疑系统变质
4. D3 只能作为候选提出，不能自动终判
5. 检测到漂移不等于要求立即修复——有些漂移意味着系统正在长出新对象
6. 当旧定义不足以覆盖现状时，优先考虑显式分叉，不强迫旧定义吞并新现实

---

## 自检

- [ ] 报告里的基线是否来自可引用的文档，还是 AI 自己的"感觉"？
- [ ] 证据是否是具体的文本引用，还是抽象的"味道变了"？
- [ ] 有没有把普通 diff（措辞变化、格式调整）当作漂移？
- [ ] 有没有把健康演化（系统主动承认的方向调整）判成漂移？
- [ ] D3 候选有没有明确标注"需人工审视"？

---

## Failure Modes

- 没有基线就给出强漂移判断
- 把措辞变化当作漂移报告
- 把健康演化判成系统变质
- D3 身份漂移候选被当作普通检测结论输出
- 过度敏感，所有细微变化都触发漂移报告
