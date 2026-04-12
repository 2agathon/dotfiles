---
name: code-review
description: >
  对代码变更施加上下文敏感的判断力。不是 linter，不是 type checker，不做工具能做的事。
  重点是发现变更里超出实现细节的选择、和已有模式不一致的地方、工具查不出但人能发现的问题。
  用户说"review"、"审一下"、"看看改动"、"提交前检查"时触发。
  也可作为 git-commit 的前置步骤自动触发。
metadata:
  collection: 2agathon-dotfiles
  layer: task
  source: 基于 google-gemini/gemini-cli/code-reviewer 重写
  governance:
    hook: pre-gate
    requires: code diff (staged or unstaged), project context (existing patterns, naming, boundaries)
    produces: review verdict (pass / needs change) with findings
    task_agnostic: false
    task_scope: code change review (before commit or merge)
---

## 这个 skill 的边界

**做什么：** 对代码变更施加上下文敏感的判断。重点不是"代码对不对"，而是"这个变更在当前上下文里是不是一个好的选择"。

**不做什么：**
- 不做 linter 能做的事（格式、import 顺序、未使用变量）
- 不做 type checker 能做的事（类型错误、null safety）
- 不做测试能覆盖的事（逻辑正确性验证归 code-test）
- 不做完整安全审计（归独立的 security-audit skill）
- 不做决策记录（发现设计分叉时指向 decision-record，不自己记）
- 不做代码修改（发现问题后提出，改是 code-modify 的事）

---

## 强制停止点

- 发现变更和项目已有模式存在根本性冲突——停，列出冲突，等用户判断是旧模式该改还是新代码该改
- 发现变更里嵌入了用户可能没意识到的设计决策——停，浮现决策，等用户确认
- review 中不确定某个发现是否真的是问题——用 `[ASSUMPTION]` 标注，不假装确定

---

## 流程

### Step 1：识别变更范围和类型

```bash
git status
git diff          # 工作区
git diff --staged # 暂存区
```

根据变更范围判断 review 类型，决定深度：

| 变更类型 | 特征 | review 重点 | 深度 |
|---|---|---|---|
| 小改动 | 单文件、几行 | 有没有副作用，30 秒结束 | 轻 |
| 功能实现 | vibe-plan 的一个 step 完成 | 对照 plan 检查方向 | 中 |
| 跨文件改动 | 多文件联动 | 文件间一致性、边界完整性 | 深 |
| 重构 | 行为不变结构变 | 新结构是否比旧结构更好 | 中 |
| AI 大段生成 | Vibe Coding 典型产物 | 嵌入决策的可见性 | 深 |
| Bug 修复 | 修已知问题 | 直接解法还是 workaround | 中 |
| 累积变更 | 多轮迭代后 diff 大 | 从噪音中找关键变更 | 深 |

**不是每次都跑完整审查。** 小改动不需要查 7 个维度。AI 必须先判断类型，再决定深度。

### Step 2：审查

根据变更类型，从以下维度中选择适用的：

**始终看：**
- **模式一致性**：变更是否和项目已有的命名、边界、错误处理模式一致？不一致是有意偏离（应标 `// DEVIATION:`）还是无意漂移？
- **嵌入决策**：变更里有没有超出实现细节的选择？命名隐含了什么边界？抽象层级意味着什么约束？这些选择用户知道吗？

**深度 review 时加：**
- **边界完整性**：跨文件改动时，模块边界是否被维持？有没有新的跨层引用？
- **错误处理策略**：新代码的错误处理是否和已有策略一致？
- **效率**：有没有引入明显的性能问题（N+1 查询、无界循环、不必要的同步操作）？
- **安全性**：有没有明显的安全问题（未校验输入、硬编码 secret、SQL 注入）？注意：这不是完整安全审计，只是 review 级别的快速扫描。
- **可测试性**：新代码是否可测试？关键路径有没有测试覆盖？

### Step 3：输出

#### 发现分级

| 级别 | 含义 | 是否阻止通过 |
|---|---|---|
| **Critical** | bug、安全问题、破坏性变更、方向性错误 | 是 |
| **Decision** | 嵌入的设计决策，需要用户确认是否有意为之 | 取决于用户回应 |
| **Improvement** | 能改进但不阻止的建议 | 否 |

不用 Nitpick 级别。格式和风格交给 linter。

#### 格式

```
## Review · {变更描述}

review 类型：{小改动 / 功能实现 / 跨文件 / ...}
变更范围：{N 个文件，约 N 行}

### 发现

[Critical] {描述}
  位置：{文件:行号或函数名}
  原因：{为什么这是问题}
  建议：{怎么处理}

[Decision] {描述}
  位置：{文件:行号}
  嵌入的选择：{这个代码隐含了什么设计决策}
  [ASSUMPTION: 这可能是有意的，但如果不是，影响范围是 X]

[Improvement] {描述}
  位置：{文件:行号}
  建议：{怎么改进}

### 结论

{通过 / 需要修改}
{一句话概括理由}
```

#### 通过的标准

**这个变更是否在整体上改善了代码库的健康状况，即使它不完美。**

- 有 Critical → 不通过
- 有未确认的 Decision → 等用户确认后再判断
- 只有 Improvement → 通过，附建议
- 什么都没发现 → 通过，说"已检查 X 范围，未发现问题"

不追求完美。不因为能找到改进点就不通过。

---

## 和治理 skill 的交互

| 场景 | 触发什么 |
|---|---|
| review 发现不确定的问题 | 用 `[ASSUMPTION]` 标注 |
| review 发现设计分叉 | 提示用户是否触发 decision-record |
| review 后用户说"改一下" | code-modify 自动生效，约束改动范围 |
| review→fix→re-review 循环 | bail-out 监测止损信号 |
| review 完成，用户要提交 | git-commit 接手 |

---

## Failure Modes

- 对小改动跑了完整深度审查，浪费时间
- 对大改动只做了表面扫描，漏掉了嵌入决策
- 发现了格式问题或 linter 能查的东西，越界了
- 不确定的发现没有用 `[ASSUMPTION]` 标注，假装确定
- 什么都没发现时没有说明检查范围，用户不知道 AI 到底看了什么
- 发现了能改进的地方就不通过，标准过严
- review 自己刚生成的代码时没有意识到系统性盲点——不会质疑自己的设计假设
- 发现了设计分叉但自己消化了，没有提示触发 decision-record

---

## 自检（AI 执行）

- [ ] 变更类型和 review 深度是否匹配？小改动有没有过度审查？
- [ ] 发现里有没有 linter 或 type checker 能查的东西？有 → 删掉，不越界
- [ ] 不确定的发现有没有用 `[ASSUMPTION]` 标注？
- [ ] 有没有检查嵌入决策？尤其是 AI 生成的代码
- [ ] "通过"的判断是基于"整体改善代码健康"，还是基于"没找到问题"？
- [ ] 如果是 review 自己刚生成的代码——有没有特别检查自己的设计假设？
