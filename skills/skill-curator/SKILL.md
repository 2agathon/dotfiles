---
name: skill-curator
description: >
  skills 体系的策展人。评估新 skill 是否值得加入、找到它在已有生态中的独特定位、确保系统一致性。
  也负责审计体系健康度，推荐合并、拆分、退役。
  用户说"我想加一个 skill"、"审一下体系"、"这个 skill 还需要吗"时触发。
metadata:
  collection: 2agathon-dotfiles
  layer: 工程协作
  invocation: user-request
  modes: evaluate,audit
  governance:
    modes:
      evaluate:
        hook: pre-gate
        requires: user intent (problem to solve, not skill name), current skills system state
        produces: curation verdict (structured) → user decides proceed / defer / reject
      audit:
        hook: standalone
        requires: current skills system baseline
        produces: system health report with structural recommendations
    task_agnostic: false
    task_scope: skills system lifecycle management
---

## 这个 skill 做什么

管理 skills 体系的演进。两件事：

1. **evaluate** — 有人想加新 skill 时，评估值不值得、怎么定位、加了之后系统还健康吗
2. **audit** — 定期或按需审视体系，找缺口、冗余、该合并/拆分/退役的

不写 skill body——策展和创作是两件事。策展人输出定位判断，创作交给 vibe-plan 和执行。

---

## 触发规则

**evaluate 模式：**
- "我想加一个 skill"、"我需要 X 方面的能力"
- "这个方向值得做 skill 吗"
- 从外部发现了一个有意思的 skill，想评估是否纳入

**audit 模式：**
- "审一下体系"、"看看还缺什么"
- "这些 skill 有没有重叠的"
- "这个 skill 还需要吗"
- drift-detector 报出 D2 级别以上的漂移后

---

## When Not to Use

- 用户已经清楚要做什么，只需要 plan 怎么建 → vibe-plan
- 修改已有 skill 的内容（不涉及定位变化）→ code-modify
- 检测已有 skill 的失真 → drift-detector
- 写文档 → docs

---

# Evaluate 模式

## Step 1 — 澄清意图

从问题出发，不从 skill 名出发。

必须搞清楚：
- **你要解决什么问题？** 不是"我想要一个 X skill"，是"我在做 Y 的时候经常遇到 Z"
- **这个痛点有多频繁？** 偶尔一次不值得建 skill，反复出现才值得

可以从上下文推断，用 `[ASSUMPTION]` 标注：
- 这个问题当前由哪个 skill 部分覆盖
- 是不是现有 skill 扩展一下就够了

**强制停止点：** 问题说不清楚时，不继续。只问这一个问题。

---

## Step 2 — 搜索公开 skill

去找这个领域已经有什么。

**搜索范围：**

| 类型 | 去哪里找 |
|------|---------|
| 官方 CLI 内置 skill | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) `skills/`、[anthropic/claude-code](https://github.com/anthropic-public/claude-code) 内置行为、[openai/codex](https://github.com/openai/codex) |
| skill 聚合平台 | [skills.sh](https://skills.sh)、[agentskills.io](https://agentskills.io)、[cursor.directory](https://cursor.directory) |
| 社区仓库 | GitHub 搜 `SKILL.md`、`agent skill`、`cursor rules`；各工具的 awesome-* 列表 |
| 工具内置能力 | Cursor 默认 skill、Claude Code 默认行为、Gemini CLI 默认行为——这些不一定是独立 skill 文件，但代表了平台认为重要的能力 |

**搜索策略：**
- 用领域关键词 + `SKILL.md` 或 `agent skill` 搜 GitHub
- 看官方 CLI 仓库的 skills/ 目录——这些通常质量较高且代表平台方向
- 聚合平台按类别浏览——发现同类 skill 的共同模式和盲区
- 不只看 skill 文件本身，也看 issue 和 PR 讨论——用户抱怨什么往往就是差异价值所在

**输出：**
- 找到了什么：列出 2-5 个最相关的已有 skill，各一句话说明
- 它们的共同模式：这些 skill 通常怎么做这件事
- 它们的共同盲区：哪些问题它们都没解决

**如果搜索结论是"已有的完全够用"——这是合法结论。** 推荐直接使用已有 skill，不造新的。evaluate 到此结束。

---

## Step 3 — 找上下文差异价值

这一步是策展的核心。不是"别人没有所以我做"，是"别人有但在我们的上下文里辜负了什么"。

我们的上下文特征：
- 一个人扛项目，AI Vibe Coding 为主要工作方式
- 已有治理层（governance protocol）约束 AI 行为
- skills 之间有明确的生命周期位置和边界声明
- 个人优先，但架构上可组合

**要回答的问题：**
- 已有的公开 skill 在我们的上下文里，什么价值被辜负了？
- 这个辜负是结构性的（它们的设计假设和我们不同），还是偶然的（只是没做到）？
- 如果是结构性的，从这道辜负里能自然长出什么方向？

**如果找不到差异价值——这也是合法结论。** 推荐采用已有 skill 并做最小适配。evaluate 到此结束。

---

## Step 4 — 系统集成检查

新方向确认后，检查它能否健康地加入现有体系。

**检查项（调用 drift-detector 扫描清单的子集）：**

- [ ] 和已有 skill 是否有职责重叠？列出每个相邻 skill 和分界线
- [ ] governance hook 是什么？在生命周期的哪个位置介入？
- [ ] AGENTS.md dispatch table 放在哪个类别？触发条件是什么？
- [ ] 和治理层的关系：它受哪些 governance skill 约束？它约束谁？
- [ ] 命名：名字的语义范围是否精确匹配它实际要做的事？过大还是过小？

**如果发现严重冲突——报告冲突，让用户决定：调整新 skill 定位，还是调整已有 skill 边界。**

---

## Step 5 — 输出策展判定

```
## Curation Verdict · [问题域]

### 为什么要加
已有 skill 在我们的上下文里辜负了什么，差异价值是什么。
引用 Step 2-3 的具体发现。

### 它是什么
一句话本质定义。名字从这里长出来。

### 它不是什么
从第一天画排除线。列出它拒绝做的事、和谁划界。

### 它在体系里的位置
- Governance hook:
- 生命周期位置:
- 相邻 skill 及分界线:
- AGENTS.md 类别:

### 加了之后改什么
- [ ] AGENTS.md：dispatch table 加入 / 触发条件
- [ ] README.md：相关 section 更新
- [ ] SKILLS-REFERENCE.md：加入
- [ ] governance-protocol.md：验证记录加入
- [ ] 其他 skill：边界声明需要调整的
```

---

## Step 6 — 用户决定

策展人不替用户做决定。输出判定后：

- **proceed** → 交给 vibe-plan 规划怎么建
- **defer** → 记录评估结论，留待以后
- **reject** → 说明原因，结束

**策展人必须能说"不加"。** 以下都是合法的拒绝结论：
- "已有的公开 skill 完全够用，不需要自己做"
- "你现有的 skill X 扩展一下就能覆盖"
- "这个痛点不够频繁，不值得建 skill"
- "当前体系已经很重了，加这个会增加维护负担但收益有限"

---

# Audit 模式

## 审计范围

系统级健康检查，不针对某个 skill，而是看整体。

### 1. 运行 drift-detector 扫描清单

调用 drift-detector 的完整扫描清单（frontmatter 一致性、引用完整性、术语一致性、职责边界、基础设施同步），作为审计的基础数据。

### 2. 在 drift-detector 基础上额外检查

drift-detector 查的是**失真**（说的和做的不一致）。策展审计还查：

- **覆盖缺口**：用户的工作流程中，哪些常见场景没有 skill 支持？
- **冗余**：哪些 skill 的职责重叠度高到应该考虑合并？
- **复杂度失衡**：有没有 skill 过于臃肿（应该拆分）或过于单薄（应该被吸收）？
- **治理完整性**：所有 skill 是否都有 governance 声明？声明是否和 body 一致？
- **维护负担**：体系整体规模是否还在可维护范围内？

### 3. 输出审计报告

```
## System Audit Report

### 当前体系概览
skill 总数、governance 覆盖率、最近变更

### 发现
每条发现用以下结构：
- 对象：
- 类型：缺口 / 冗余 / 失衡 / 治理缺失 / 维护风险
- 证据：
- 建议动作：加 / 合并 / 拆分 / 退役 / 调整边界 / 暂不动

### 优先级排序
按影响面排序，不按发现顺序
```

---

## 与其他 skill 的关系

| 场景 | 用谁 |
|------|------|
| 检测已有 skill 的失真 | drift-detector |
| 评估新 skill 是否值得加入 | skill-curator (evaluate) |
| 审视体系整体健康度 | skill-curator (audit)，会调用 drift-detector |
| 规划怎么建一个 skill | vibe-plan（curator 的下游） |
| 新建 skill 文件时的命名和放置 | file-creation |
| 写 skill body | 执行（不归 curator 管） |
| 记录"为什么选这个方案" | decision-record（curator 发现设计分叉时触发） |

---

## Guardrails

1. **从问题出发，不从 skill 名出发。** "我需要一个 X" 要被翻译成 "我在做 Y 时遇到 Z"
2. **搜索是必须步骤，不能跳过。** 不搜就评估等于闭门造车
3. **"不加"是合法结论。** 好的策展人拒绝的比接纳的多
4. **不替用户做决定。** 输出判定，用户拍板
5. **不写 skill body。** 策展和创作分离，写交给 vibe-plan + 执行
6. **差异价值必须基于证据。** "感觉我们的不一样"不是差异价值，要说清楚辜负了什么

---

## 自检

- [ ] 有没有跳过公开 skill 搜索就直接定义？
- [ ] "为什么要加"是基于真实差异，还是"有总比没有好"？
- [ ] 有没有检查和已有 skill 的职责重叠？
- [ ] 本质定义是一句话吗？能不能更短？
- [ ] 排除线够具体吗？还是在用"不处理 X"这种模糊说法？
- [ ] 有没有考虑过"不加"这个选项？
- [ ] audit 模式有没有实际运行 drift-detector 扫描清单，还是凭印象？

---

## Failure Modes

- 每次评估都得出"值得加"的结论——策展人变成了橡皮图章
- 不搜索公开 skill 就开始定义——闭门造车
- 输出了 API 规格（capability / interface）而不是定位判断——角色错位
- 加了 skill 但没更新 AGENTS.md / README / SKILLS-REFERENCE——集成遗漏
- 定义太宽泛（"处理所有 X 相关的事"）——出生即 scope creep
- audit 模式只跑 drift-detector 不做额外检查——降级为 drift-detector 的封装
