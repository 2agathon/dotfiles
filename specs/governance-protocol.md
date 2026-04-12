# Governance Protocol v0.4

AI 元认知治理层的接口协议。定义治理 skill 如何声明自己的行为模式，使其可叠加在任何任务 skill 上。

## 这个协议解决什么问题

任务 skill 教 AI "怎么做事"（TDD、code review、security audit）。
治理 skill 约束 AI "做事时怎么管住自己"（什么时候停、什么时候问、什么时候止损）。

两者需要组合使用，但没有接口定义。这份协议是接口。

---

## 核心概念

治理 skill 通过 `metadata.governance` 声明自己的 hook 模式。声明遵循 Agent Skills 开放标准——`metadata` 是规范认可的自定义扩展点。

**单模式 skill**（一种 hook 行为）：

```yaml
metadata:
  governance:
    hook: <hook 类型>
    requires: <需要从执行上下文中观察到什么>
    enforces: <施加什么行为限制>
    produces: <产出什么结构化输出>
    task_agnostic: <是否和任务内容无关>
    task_scope: <适用的任务范围>
```

**多模式 skill**（同一个 skill 在不同触发条件下表现为不同 hook 类型）：

```yaml
metadata:
  governance:
    modes:
      <模式名>:
        hook: <hook 类型>
        requires: <该模式需要观察到什么>
        produces: <该模式产出什么>
      <模式名>:
        hook: <hook 类型>
        requires: ...
        produces: ...
    task_agnostic: <是否和任务内容无关>
    task_scope: <适用的任务范围>
```

多模式时，`hook`/`requires`/`enforces`/`produces` 各模式独立声明；`task_agnostic` 和 `task_scope` 在模式外声明，所有模式共享。

各模式互斥——同一时刻只有一个模式生效，由触发条件决定。

---

## Hook 类型

| 类型 | 行为 | 生命周期位置 |
|---|---|---|
| `foundation` | 始终在场的行为底座，不拦截特定阶段 | 贯穿全程 |
| `pre-gate` | 动手前拦截，确认后放行 | 任务执行前 |
| `constraint` | 执行中持续约束行为边界 | 任务执行中 |
| `monitor` | 执行中持续监测，信号触发时中断 | 任务执行中 |
| `post-protocol` | 执行后沉淀和交接 | 任务执行后 |

### foundation

始终在场，不绑定特定任务阶段。提供所有其他治理 skill 共享的行为基准（标注体系、停止规则、协作约定）。

一个治理体系只有一个 foundation。它不是 hook，是地基。

### pre-gate

在任务开始前拦截。产出需要用户确认的结构化输出（计划、检查结果、风险评估），确认后才放行执行。

特征：有明确的"通过 / 不通过"判断点。

### constraint

在任务执行过程中持续约束 AI 的行为。不产出独立输出，而是限制行为边界——什么能做、什么不能做、范围扩大时怎么办。

特征：AI 看不见它在工作时，说明它在正常工作。只在边界被触碰时才显现。

### monitor

在任务执行过程中持续监测。和 constraint 的区别：constraint 限制行为，monitor 观察状态。monitor 在检测到信号时中断执行，产出结构化评估。

特征：平时沉默，信号触发时中断并报告。

### post-protocol

在任务执行完成后运行。负责沉淀、交接、记录——把执行过程中产生的认识固化为可被下一轮消费的对象。

特征：面向未来读者（可能是 AI），不是面向当前用户。

---

## 字段定义

| 字段 | 类型 | 说明 |
|---|---|---|
| `hook` | enum | 必填。`foundation` / `pre-gate` / `constraint` / `monitor` / `post-protocol` |
| `requires` | string | 这个治理 skill 需要从执行上下文中观察到什么才能工作 |
| `enforces` | string | 施加什么行为限制。constraint 类型必填，其他类型按需 |
| `produces` | string | 产出什么结构化输出。monitor 和 pre-gate 通常必填 |
| `task_agnostic` | boolean | 是否和任务 skill 的具体内容无关。true = 可叠加在任何任务上 |
| `task_scope` | string | 当 `task_agnostic: false` 时，说明适用于什么任务。task_agnostic 为 true 时省略 |

### 各 hook 类型的字段适用性

| 字段 | foundation | pre-gate | constraint | monitor | post-protocol |
|---|---|---|---|---|---|
| `hook` | 必填 | 必填 | 必填 | 必填 | 必填 |
| `requires` | — | 必填 | 必填 | 必填 | 必填 |
| `enforces` | 按需 | 按需 | **必填** | — | — |
| `produces` | — | **必填** | 按需 | **必填** | 按需 |
| `task_agnostic` | — | 必填 | 必填 | 必填 | 必填 |
| `task_scope` | — | 若非 agnostic | 若非 agnostic | 若非 agnostic | 若非 agnostic |

---

## 组合规则

### 多个治理 skill 同时生效

一个任务可以同时被多个治理 skill 覆盖。执行顺序按生命周期自然排列：

```
foundation（始终在场）
  → pre-gate（动手前逐个检查，全部通过才继续）
    → constraint + monitor（执行中并行生效）
      → post-protocol（执行后依次运行）
```

### 同类型冲突

- 同一阶段的多个 pre-gate：全部必须通过
- 同一阶段的多个 constraint：全部同时生效，约束取并集
- 同一阶段的多个 monitor：任意一个触发信号即中断

### task_agnostic 的组合

task_agnostic 的治理 skill 可以和任何任务 skill 组合，不需要额外配置。
非 task_agnostic 的治理 skill 只在 task_scope 匹配时生效。

---

## 范例

每种 hook 类型至少一个范例，按生命周期顺序排列。

### identity（foundation）

```yaml
metadata:
  governance:
    hook: foundation
```

foundation 是地基不是 hook。只需声明类型，不需要 requires/enforces/produces/task_agnostic。一个治理体系只有一个 foundation。

### conversation-to-spec（pre-gate，task_agnostic）

```yaml
metadata:
  governance:
    hook: pre-gate
    requires: conversation approaching commitment window — stable returns, converging language, action-oriented shift
    produces: temporary spec object (structured, with validity/invalidation conditions) → user confirms before commitment
    task_agnostic: true
```

拦截对话→承诺的转换点。虽然"把对话结晶成对象"听起来像 post-protocol，但它面向当前用户要求确认（pre-gate），不是面向未来读者归档（post-protocol）。task_agnostic: true——任何对话都可能接近承诺时刻。

### code-modify（constraint）

```yaml
metadata:
  governance:
    hook: constraint
    requires: original change request scope, files being modified
    enforces: surgical modification, scope control, change visibility, impact verification
    produces: change declaration (conditional — high-risk cross-file changes only)
    task_agnostic: false
    task_scope: code modification (modify, fix, refactor, adjust)
```

只在修改代码时生效。主要是行为限制，只在高风险时才产出改动声明。

### bail-out（monitor）

```yaml
metadata:
  governance:
    hook: monitor
    requires: iteration history — original request, what each round changed, why each change was made
    produces: stop-loss assessment (structured) → user decides next step
    task_agnostic: true
```

任何迭代场景都适用。不需要知道任务是什么，只需要看到迭代历史。

### decision-record（post-protocol，task_agnostic）

```yaml
metadata:
  governance:
    hook: post-protocol
    requires: decision fork — alternatives, trade-offs, constraints that shaped the choice
    produces: decision record (structured, referenceable by docs and future decisions)
    task_agnostic: true
```

任何任务里出现决策分叉都可触发。面向未来读者——让他们知道当时为什么选了这个而不是别的，什么条件下应该重新审视。

### code-relay（多模式：post-protocol + pre-gate）

```yaml
metadata:
  governance:
    modes:
      recognition:
        hook: post-protocol
        requires: code materials, optional existing handover notes or execution summary
        produces: handover note (structured, persisted to .ai/relay/)
      load:
        hook: pre-gate
        requires: handover note (from file or user-pasted)
        produces: load confirmation (structured, max 10 lines per region)
      wrap-up:
        hook: post-protocol
        requires: execution context — what changed, what diverged from expectation
        produces: execution summary (structured, three sections)
    task_agnostic: false
    task_scope: code session relay (cross-session context transfer)
```

三种模式互斥。recognition 和 wrap-up 是 post-protocol（为下一轮沉淀），load 是 pre-gate（为当前轮加载上下文）。这是第一个暴露"单一 hook 字段不够用"的 skill，催生了 `modes` 格式。

---

## 验证记录

所有治理 skill 已完成 governance 声明。以下是验证结果和关键发现：

| Skill | Hook 类型 | 验证结论 |
|---|---|---|
| ~~identity~~ | foundation | ✅ 显式声明，只需 `hook: foundation`，无需其他字段（foundation 是地基，不是 hook） |
| ~~vibe-plan~~ | pre-gate | ✅ 经典 pre-gate。enforces（plan 确认前不写代码）和 produces（设计文档）都需要 |
| ~~file-creation~~ | pre-gate | ✅ 仅 create 模式声明 governance。audit 模式是独立诊断工具，不参与任务生命周期 |
| ~~code-relay~~ | 多模式 | ✅ post-protocol + pre-gate，催生 modes 格式 |
| ~~code-test~~ | constraint | ✅ 是 constraint 不是 pre-gate。它不拦截、不产出通过/不通过判定，持续约束测试写法 |
| ~~decision-record~~ | post-protocol | ✅ task_agnostic: true。任何任务里出现决策分叉都可触发，不限于代码 |
| ~~git-commit~~ | pre-gate | ✅ 单模式，不需要 modes。安全检查/分支确认/逻辑单元分析是连续门检步骤，不是独立模式 |
| ~~docs~~ | constraint | ✅ 持续约束写法。新建文档的"三件事确认"是 constraint 的入口检查，不独立为 pre-gate |
| ~~assumption-audit~~ | monitor | ✅ task_agnostic: true。监测前提信号（结论强于证据、词比定义快），触发时产出结构化审计报告 |
| ~~conversation-to-spec~~ | pre-gate | ✅ task_agnostic: true。在对话→承诺转换点拦截，产出临时规格对象，用户确认后放行。不是 post-protocol——面向当前用户要求确认，不是面向未来读者归档 |
| ~~role-lens~~ | monitor | ✅ task_agnostic: true。监测单一透镜主导信号，触发时产出冲突重读分析（主导+挑战+处理结果） |
| ~~drift-detector~~ | monitor | ✅ task_agnostic: true。监测系统演化中的无声变更，触发时产出分级漂移报告（D1/D2/D3-candidate） |

### 关键发现

1. **foundation 极简**：只需 `hook: foundation`，不需要 requires/enforces/produces/task_agnostic。它不是某个任务的 hook，是所有 hook 的地基。
2. **audit 类模式不参与治理**：file-creation 的 audit 模式是用户主动发起的诊断，不属于任务生命周期的任何阶段。用 `note` 字段说明即可。
3. **连续步骤 ≠ 多模式**：git-commit 的多个步骤（安全检查→分支确认→逻辑单元→message 生成）是同一次触发的连续流程，不是独立模式。modes 用于不同触发条件导致完全不同行为的场景（如 code-relay）。
4. **constraint 可以有入口检查**：docs 在新建文档时有"确认三件事"的门控，但它是 constraint 行为的启动条件，不是独立的 pre-gate。判断标准：这个检查是为了让后续 constraint 正常工作（docs），还是检查本身就是交付物（vibe-plan）。
5. **conversation-to-spec 是 pre-gate 不是 post-protocol**：虽然它"把对话结晶成对象"听起来像 post-protocol，但它的核心行为是拦截对话→承诺的转换，要求用户确认后才放行。post-protocol 面向未来读者归档，conversation-to-spec 面向当前用户要求确认——这是区分标准。
6. **认识校准类全部 task_agnostic: true**：前提审计、透镜检测、漂移监测、承诺门控都不依赖具体任务内容，可叠加在任何对话上。这是治理框架最独特的层——跨越工程和认知边界的元监测。

---

## 版本

- v0.1 — 从 bail-out 和 code-modify 两个样本提取。单模式格式。
- v0.2 — 加入 code-relay 验证。发现单模式格式不足，新增 `modes` 多模式格式。
- v0.3 — 工程执行 + 工程协作类治理 skill 验证完成。确认 foundation 极简声明、audit 类不参与治理、连续步骤不等于多模式、constraint 可含入口检查。
- v0.4 — 认识校准类 4 个 skill 验证完成。确认 conversation-to-spec 是 pre-gate（不是 post-protocol），认识校准类全部 task_agnostic: true。所有治理 skill governance 声明完成。
