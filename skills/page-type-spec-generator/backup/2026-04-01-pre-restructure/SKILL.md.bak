---
name: page-type-spec-generator
description: >
  从业务人员提供的 xlsx 设计稿，生成页类型流水线所需的配置文件。
  触发场景：用户提供 xlsx 并说"生成 spec"、"转成配置"、"新建页类型"等。
---

# 页类型 Spec 生成器

## 这是什么

这是一个面向 Agent 执行的转译协议，不是一次性从 xlsx 直接生成最终文件的 prompt。

目标是把业务人员提供的 xlsx 设计稿，稳定转译为页类型流水线所需的配置文件，并在过程中：

1. 抵抗脏输入、空编码、表头漂移、重复标签等边沿压力。
2. 把身份判定与语义生成分层处理。
3. 生成中间产物，供后续步骤与审计使用。
4. 在最终交付前完成一致性校验与风险汇报。

## 你必须遵守的总原则

1. 先身份，后语义。
2. 先骨架，后富化。
3. 先中间产物，后最终文件。
4. 能进入结构化字段的，不放进 hint。
5. 能由上位定义裁决的，不由 skill 自己发明规则。
6. 能自动推进的机械步骤，不要打断用户。
7. 真正需要用户拍板的边界点，必须显式交互。

## 上位定义与裁决顺序

发生冲突时，按以下顺序裁决：

1. `refs/page-semantic-contract.v1.md`
2. `refs/tag-anchor-contract.v1.md`
3. `refs/page-types-contract.v1.md`
4. `refs/page-semantic.schema.json`
5. `refs/page-types.schema.json`
6. `refs/页类型创作指南.md`
7. `examples/TYPE_OFFICIAL_NORMATIVE_DOCUMENT/*`
8. 本 `SKILL.md`

使用规则：

1. contract 决定语义边界。
2. schema 决定结构合法性。
3. guide 提供业务写作与维护说明，但不能推翻 contract 或 schema。
4. examples 只示范写法，不得反向立法。
5. 本 skill 只能执行，不得偷偷改写上位定义。

## 启动前必须读取的材料

开始任何转换前，必须先读完以下文件，再处理用户输入：

1. `refs/page-semantic-contract.v1.md`
2. `refs/tag-anchor-contract.v1.md`
3. `refs/page-types-contract.v1.md`
4. `refs/page-semantic.schema.json`
5. `refs/page-types.schema.json`
6. `refs/页类型创作指南.md`
7. `examples/TYPE_OFFICIAL_NORMATIVE_DOCUMENT/page-semantic-spec.json`
8. `examples/TYPE_OFFICIAL_NORMATIVE_DOCUMENT/tagging-hint.md`
9. `examples/TYPE_OFFICIAL_NORMATIVE_DOCUMENT/assembly-hint.md`
10. `examples/TYPE_OFFICIAL_NORMATIVE_DOCUMENT/block-summary-hint.md`
11. `examples/TYPE_OFFICIAL_NORMATIVE_DOCUMENT/page-summary-hint.md`
12. `examples/TYPE_OFFICIAL_NORMATIVE_DOCUMENT/continuation-hint.md`

## 运行模式

本 skill 只能以三种模式之一运行：

### 1. `interactive`

适用于当前环境可以正常向用户提问。

要求：

1. 必须在类型枚举完成后询问用户要处理哪些 `type`。
2. 必须在高冲突身份判定点请求确认。

### 2. `constrained`

适用于当前环境允许少量交互，或用户希望尽量少打断。

要求：

1. 尽量只保留硬交互点。
2. 其他可继续推进的问题全部写入审计报告。

### 3. `no_interaction`

适用于当前环境不方便交互。

要求：

1. 允许自动继续，但必须显式记录所有默认决策。
2. 最终报告中必须单列“未获得用户确认而自动决定的事项”。
3. 不得假装这些决定已经被用户确认。

## 输入判断

收到文件后，先判断输入情况：

| 用户提供的文件 | 判断结果 | Agent 行为 |
|---|---|---|
| 只有 xlsx | 首次创建模式 | 从头生成完整文件 |
| xlsx + data.json + tree.json | 已有命名空间模式 | 先做存在性检查，再决定增量写入 |
| xlsx + 只有其中一个 json | 输入异常 | 停止并提示用户补齐缺失文件 |

## 解析能力探测

你不能假设当前环境天然具备 xlsx 解析能力。

开始 Stage 1 前，必须先探测当前环境是否具备可用解析后端。

你必须先发现能力，再决定后端，不得先假设某种技术栈。

要求：

1. 首选能够稳定保留二维表内容与 workbook 细节的后端。
2. 不得把某种解析后端偷偷写成默认真理。
3. 必须优先使用无需修改用户环境状态的现成能力。
4. 若解析能力不足，必须明确报告缺失能力，而不是静默失败。

你必须把解析能力分成三类：

1. `现成可用`
含义：当前就能用，不需要安装或修改环境。
动作：直接使用，不打扰用户。

2. `经授权可达`
含义：当前不能直接用，但经过用户许可的最小 bootstrap 就能达到。
动作：
  - 在 `interactive` / `constrained` 模式下，明确告诉用户这条路径存在，让用户选择是否激活。
  - 在 `no_interaction` 模式下，不要自动安装；只在最终报告中写明这是一条可达路径。

3. `当前不可达`
含义：当前环境下没有安全可行的解析路径。
动作：明确报告缺口并停止继续依赖该后端。

规则：

1. 安装运行时或依赖不是默认动作，而是用户可选择激活的一条可达路径。
2. “可安装依赖”不等于“当前已有能力”。
3. 若存在多条现成路径，优先选择更稳定保留 workbook 结构信息的后端。
4. 只有当现成路径都不足以完成最小解析目标时，才允许暴露 bootstrap 选项。

## 执行阶段

你必须按以下阶段顺序执行，不得阶段倒置。

### Stage 0：Run Manifest

目标：建立一次可追踪 run。

必须做：

1. 记录 `run_id`。
2. 记录运行模式。
3. 记录输入文件路径。
4. 记录是否提供了 `data.json/tree.json`。

产物：

1. `run-manifest.json`

禁止：

1. 在没有 run manifest 的情况下继续后续阶段。

### Stage 1：Raw Parse

目标：把 xlsx 原始读取出来，不做语义判定。

必须做：

1. 读取 sheet 名称。
2. 保留原始行号与列号。
3. 保留原始单元格内容。
4. 尽可能保留合并单元格、隐藏行、公式显示值等细节。

产物：

1. `workbook.raw.json`

禁止：

1. 不得在这一层修正文义。
2. 不得在这一层决定标签身份。
3. 不得在这一层生成最终 ID。

### Stage 2：Normalize

目标：把原始表变成后续步骤可稳定消费的中间表。

必须做：

1. 表头容错映射。
2. 继承填充。
3. 空值标准化。
4. 文本轻清洗。
5. 行级初步分类。
6. 记录所有修复痕迹。

已知需要容错的列名示例：

1. `namespce` -> `namespace`
2. `Bolck role` -> `Block role`

产物：

1. `workbook.normalized.json`
2. `normalization-report.md`

禁止：

1. 不得决定空编码行最终是不是标签。
2. 不得生成 `value_hint/context_hint`。
3. 不得绕过原始行号。

### Stage 3：Identity Map

目标：先认清谁是谁，再继续。

必须做：

1. 抽取 namespace。
2. 抽取 category。
3. 抽取 type。
4. 抽取 block。
5. 抽取 tag 候选与 block 引用关系。
6. 处理重复标签去重。
7. 处理空 `tag编码` 行分类。

产物：

1. `identity-map.json`
2. `identity-issues.md`

禁止：

1. 不得在身份未稳定前写最终 spec。
2. 不得在这一层生成 hint 文件。

### Stage 4：Type Selection

目标：在 type 已能枚举之后，确定本次要处理哪些类型。

必须做：

1. 先从 `identity-map.json` 中列出所有检测到的 type。
2. 若模式为 `interactive` 或 `constrained`，向用户询问要处理哪些 `type`。
3. 若模式为 `no_interaction`，按默认策略继续，并显式记录未获确认。

默认展示格式：

```text
检测到以下页类型，请选择要处理的（可多选）：
1. ADMISSION_RECORD（入院记录）- namespace: default
2. LABORATORY_TEST_REPORT（实验室检查报告）- namespace: default
```

产物：

1. 更新后的 `run-manifest.json`

禁止：

1. 不得在尚未完成类型枚举前询问用户选 type。
2. 不得在可交互模式下默认处理全部。

### Stage 5：Existence Check

目标：仅在已有命名空间模式下，检查 type 是否已存在。

必须做：

1. 检查 `data.json` / `tree.json` 是否配套。
2. 对每个选中的 `type_id`，检查是否已存在。
3. 若已存在，决定哪些文件跳过写入。
4. 若不存在，决定追加到现有 category 还是新建 category。

禁止：

1. 不得只更新 `data.json` 不更新 `tree.json`。

### Stage 6：Skeleton

目标：先保全结构闭合，不做高自由度语义生成。

必须做：

1. 生成 `page-types.data.json` 骨架。
2. 生成 `page-types.tree.json` 骨架。
3. 生成 `page-semantic-spec.json` 骨架。
4. 生成空 hint 模板。

规则：

1. 根级 `tags[]` 只能从 `identity-map.tags[]` 派生。
2. `block_types[].tags[]` 只能引用 `identity-map.tags[].canonical_id`。
3. 可用 `[DEFERRED]` 或空模板占位，但不得写成正式真相。

产物：

1. `skeleton/`

提示：

1. `skeleton/` 中的 hint 文件只承担占位与结构闭合职责。
2. `semantic-draft/` 中的 hint 文件才是后续进入最终结果的 canonical draft。

### Stage 7：Semantic Draft

目标：在骨架稳定后，再生成高自由度语义内容。

必须做：

1. 生成 `block_types[].description`。
2. 生成 `tags[].value_hint`。
3. 生成 `tags[].context_hint`。
4. 生成 `tags[].anchor_binding`。
5. 生成 `tagging-hint.md`。
6. 生成 `assembly-hint.md`。
7. 生成 `block-summary-hint.md`。
8. 生成 `page-summary-hint.md`。
9. 生成 `continuation-hint.md`。
10. 为上述对象生成 sidecar / manifest，记录状态与来源。

产物：

1. `semantic-draft/`

禁止：

1. 不得重新发明 tag / block 身份。
2. 不得绕过 `identity-map` 临场新增根级 tag。
3. 不得把高自由度生成直接写进最终正式文件而没有状态记录。

### Stage 8：Validation And Audit

目标：检查结构合法性、引用闭合性、边沿处理和职责串层问题。

必须做：

1. schema 校验。
2. 检查 `block_types[].tags[].tag_id` 是否都能在根级 `tags[]` 找到。
3. 检查空编码标签是否被静默丢弃。
4. 检查 `identity_status=ambiguous` 是否被静默写入正式结果。
5. 检查 `context_hint` 是否越界成解释型写法。
6. 检查 `block_types[].description` 是否夹带执行策略。
7. 检查 hint 文件是否职责串层。

产物：

1. `validation-report.json`
2. `audit-report.md`

### Stage 9：Final Handoff

目标：向用户汇报最终状态。

必须汇报：

1. 处理了哪些 type。
2. 生成了哪些文件。
3. 做了哪些自动修复。
4. 哪些事项未获用户确认但已自动决定。
5. 哪些事项仍是 `OPEN QUESTION` 或高风险项。

产物：

1. `final-report.md`

## 人机交互点

### 硬交互点

以下情况必须询问用户，除非当前模式为 `no_interaction`：

1. 选择本次要处理哪些 `type`。
2. 空编码标签存在多个同样合理的身份解释。
3. 已有 `data.json/tree.json` 与本次结果发生真实冲突。
4. 某行无法判断是归属当前 block 还是应独立成新 block。

### 软交互点

以下情况默认可继续，但必须在报告中写明：

1. 表头 typo 修复。
2. `anchor_binding` 小语法修复。
3. 同标签轻微文本不一致合并。
4. 素材不足时输出空 hint 模板。

### 禁止打断

以下情况不要打断用户：

1. 纯机械映射。
2. 骨架生成。
3. schema 校验。
4. 普通统计信息汇总。

## 标签身份规则

### 基本规则

最终 spec 的根级 `tags[]` 是页类型级标签定义集合，不是按 block 平铺出来的列表。

因此必须遵守：

1. 根级 `tags[]` 以 canonical tag id 去重。
2. `block_types[].tags[]` 只做引用，不重复定义标签身份。
3. 同一个标签可在多个 block 中重复引用，并带不同 `role`。

### 行分类

对落在标签定义区的行，先做分类，再决定如何落地：

1. `explicit_tag`
条件：`tag名称` 非空，且 `tag编码` 非空。

2. `recoverable_tag`
条件：`tag名称` 非空，`tag编码` 为空，且以下任一项非空：`tag定义`、`触发模式`、`正例`、`反例`、`必须`、`tag anchor binding`、`Block role`。

3. `helper_only`
仅当以下条件同时满足时才允许：
  - `tag名称` 为空，或不构成独立标签名
  - 语义列基本为空
  - 该行只在补充 block 引用说明，而不是定义一个可打标签对象

4. `invalid_or_noise`
条件：`tag名称` 为空，语义列为空，且既不构成 block 延续，也不构成标签定义。

### 空 `tag编码` 行的默认偏置

凡是 `tag名称` 非空且落在标签定义区的空编码行，默认先进入 `recoverable_tag`。

只有满足 `helper_only` 的显式降级条件时，才允许转为 `helper_only`。

### 编码修复

对 `recoverable_tag`，按以下顺序处理：

1. 优先继承 workbook 中语义同源的显式编码。
2. 若没有可继承编码，则生成稳定 canonical id，并在同语义重复行中复用。
3. 若存在多个合理候选，标记为 `ambiguous`，进入审计报告，并在可交互模式中请求确认。

## 字段操作类型

后续所有生成动作，必须把字段归入以下操作类型之一：

1. `COPY`
忠实搬运，不改语义。

2. `NORMALIZE`
只做格式规范化，不改语义。

3. `REPAIR`
输入有缺陷，必须修复并留痕。

4. `SYNTHESIZE`
输入未直接给出，需要按规则生成。

5. `REWRITE`
原始素材存在，但必须按字段职责边界重写。

6. `DEFER`
当前阶段先不做，保留占位。

## 字段规则

### `block_types[].description`

职责：只写块的语义范围说明。

必须做：

1. 说明块对象是什么。
2. 说明块包含哪些语义维度。

不得写：

1. 组装顺序
2. 字数控制
3. 跨页拼接
4. 冲突裁决

这些属于 `assembly-hint.md`。

### `tags[].value_hint`

输入来源：`tag定义`、`触发模式`、`正例`、`反例`、`必须`

合成顺序固定为：

1. 是什么
2. 怎么识别
3. 不打什么
4. 输出格式

强约束：

1. 不得跨 tag 污染。
2. 不得跨 type 借词。
3. 不得把 tagging / assembly 职责塞进来。

### `tags[].context_hint`

必须服从 `page-semantic-contract.v1.md` 中 `tag_context` 的语义边界。

职责：只约束 `tag_context` 如何补足断言边界。

允许写：

1. 所指对象
2. 语义角色
3. 成立边界
4. 作用范围
5. 最小来源性语义

不得写：

1. 来源位置
2. 判读依据
3. OCR 修正过程
4. 锚点或归组信息
5. 解释型长段说明

规则：

1. 有真实歧义才写。
2. 无歧义可以留空。
3. 不得为了“内容更完整”而默认生成长篇 `context_hint`。

### `tags[].anchor_binding`

职责：结构化锚点定义，不是自由文本。

处理步骤固定为：

1. 文本解析
2. 语法修复
3. 默认值补齐
4. 语义校验

必须检查：

1. `target_tag_ids`
2. `page_window.mode`
3. `direction`
4. `required`
5. `self_resolution`

不得做：

1. 把 `anchor_binding` 退回自然语言提示。
2. 缺关键字段时静默编造。

## Hint 文件规则

### 总规则

1. 能进结构化字段的，不放 hint。
2. 属于别的步骤职责的，不跨层写。
3. 没有素材时，输出空模板，不灌水。

### `tagging-hint.md`

承载：

1. OCR / 排版噪声处理
2. 标签边界易混淆情况
3. 单页范围内有效的取值优先级与防线

### `assembly-hint.md`

承载：

1. 块组装执行策略
2. 空块抑制
3. 字数控制
4. 拼接与冲突处理

### `block-summary-hint.md`

承载：

1. 块摘要偏好与兜底说明

### `page-summary-hint.md`

当前设计稿通常无直接素材，默认输出空模板。

### `continuation-hint.md`

当前设计稿通常无直接素材，默认输出空模板。

## 输出文件

最终输出目录保持为：

```text
{namespace}/
├── page-types.data.json
├── page-types.tree.json
└── types/
    └── {TYPE_ID}/
        ├── page-semantic-spec.json
        ├── tagging-hint.md
        ├── assembly-hint.md
        ├── block-summary-hint.md
        ├── continuation-hint.md
        └── page-summary-hint.md
```

规则：

1. 六个 hint 文件全部输出。
2. 差异在内容深度，不在是否存在。
3. 无素材时输出空模板。

## 标注规范

| 标注 | 含义 | 谁来解决 |
|---|---|---|
| `[ASSUMPTION: 说明]` | Agent 合理推断，可继续 | 用户可随时纠正 |
| `[OPEN QUESTION: 问题]` | 无法推断，必须人工处理 | 用户决定 |
| `[INFERRED FROM: 来源]` | 从上下文推断，非直接映射 | 用户核实 |

## 结束前强制检查清单

结束前必须检查：

1. 是否完成所有阶段，且没有阶段倒置。
2. 是否已生成 `run-manifest/raw/normalized/identity/skeleton/semantic-draft/validation/audit/final-report`。
3. 是否所有 block 引用的 tag 都在根级 `tags[]` 中存在。
4. 是否存在空编码标签被静默丢弃。
5. 是否存在 `identity_status=ambiguous` 但未上报。
6. `context_hint` 是否越界成解释型写法。
7. `block_types[].description` 是否夹带执行策略。
8. hint 文件是否职责串层。
9. 是否在最终报告中写明所有自动修复与未确认默认决策。

## 失败模式

以下情况属于错误执行：

1. 直接从二进制 xlsx 跳到最终 spec，没有中间产物。
2. 在 type 枚举前就要求用户选择 type。
3. 在身份未稳定前就开始大段生成 `value_hint/context_hint`。
4. 把空编码标签静默吞掉。
5. 把 examples 当成上位定义来源。
6. 把 `context_hint` 写成来源位置、判读理由、OCR 解释。
7. 把组装策略写进 `block_types[].description`。
8. 没做审计就直接交付结果。

## 最终提醒

这个 skill 的成功标准不是“生成了一份看起来很完整的结果”，而是：

1. 输入被稳定解析。
2. 身份与语义被分层处理。
3. 中间产物可审计。
4. 最终结果符合 schema 与 contract。
5. 用户能清楚知道哪些是确定结果，哪些是默认决策，哪些仍待确认。
