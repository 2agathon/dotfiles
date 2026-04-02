---
name: page-type-spec-generator
description: >
  从业务 xlsx 设计稿生成页类型配置文件。
  触发：用户提供 xlsx 并要求生成 spec、转成配置、新建或维护页类型。
---

# page-type-spec-generator

## 目标

把输入 xlsx 转换为一套 review-ready 的完整规格包：

1. 中间产物
2. `skeleton/`
3. `semantic-draft/`
4. `final-review/`
5. `page-types.data.json`
6. `page-types.tree.json`
7. `types/{TYPE_ID}/page-semantic-spec.json`
8. 各类 hint 文件
9. `slot-manifest.json`

## 默认读取范围

只允许读取：

1. `rules/`
2. `schema/`

默认不读取：

1. `backup/`
2. `refs/`
3. `boundaries/`
4. 任何历史 example

## 执行入口

开始执行时，按以下顺序读取：

1. `rules/field-source-matrix.md`
2. `rules/pipeline/stages.md`
3. `rules/pipeline/artifacts.md`
4. `rules/pipeline/interaction-points.md`
5. `rules/pipeline/validation-checklist.md`
6. `rules/pipeline/state-and-placeholder-policy.md`
7. `rules/pipeline/slot-manifest-contract.md`

## 执行规则

1. 必须按 `rules/pipeline/stages.md` 的阶段顺序执行。
2. 必须按 `rules/field-source-matrix.md` 限制每个对象可读取的规则文件。
3. 生成内容时只使用 `rules/*`。
4. 结构校验时只使用 `schema/*`。
5. 若某对象无法仅凭指定 `rules/*` 生成，停止扩展读取范围，改为记录问题并等待补 rule。
6. 若任一必填 ID 为空或任一对象进入 `blocked`，必须停止后续阶段。
7. 若当前选中 type 之外的对象混入结果，必须视为失败。
8. review-ready 结果必须显式保留所有必填字段与业务上可维护的可选字段；不得靠物理省略隐藏缺口。

## 阶段调度

### Stage 0-3

按 `rules/pipeline/stages.md` 执行：

1. `run-manifest`
2. `raw parse`
3. `normalize`
4. `identity map`

要求：

1. 身份未稳定前，不得生成语义字段。
2. 空 `tag编码` 行必须进入身份解析流程，不得静默丢弃。
3. 任一 canonical id 为空时，视为 Stage 3 失败。
4. `block_start` 行若同时承载首标签定义，必须进入 tag 身份解析，不得只建 block 不建 tag。

### Stage 4-5

执行：

1. `type selection`
2. `existence check`

要求：

1. 交互行为服从 `rules/pipeline/interaction-points.md`。
2. 不得在类型枚举前询问用户选择 `type`。

### Stage 6-7

执行：

1. `skeleton`
2. `semantic draft`

要求：

1. `identity-map.json` 是身份真相。
2. `skeleton/` 负责结构闭合、模板展开和占位显影，不负责最终 prose。
3. 若 `identity-map.json` 与 `skeleton/` 冲突，必须以 `identity-map.json` 为准。
4. 生成字段时，只读取该字段在 `field-source-matrix.md` 中指定的 rule。
5. Stage 7 只允许在骨架既有槽位上逐项语义化，不得混入其他 type。
6. Stage 7 的生成单位只允许是：单个 block、单个 tag、单个 hint 文件或单个 type description。
7. Stage 7 脚本只允许复制、排队、分发单元任务与回写状态；不得一次生成多个同类槽位内容。

### Stage 8-9

执行：

1. `final review`
2. `final handoff`

要求：

1. 校验只负责检查，不负责继续补写正式内容。
2. `final-review/` 必须从 `semantic-draft/` 派生。
3. 最终交付目录必须从 `final-review/` 派生。
4. 不得绕过 `semantic-draft/` 或 `final-review/` 另写一份最终结果。
5. 只要存在 blocking，不得输出正式最终结果。

## 字段与 hint 路由

### 字段生成

1. `page-types.data.json` / `page-types.tree.json` 顶层字段 -> `rules/fields/page-types-top-level-generation.md`
2. `types[].description` -> `rules/fields/type-description-generation.md`
3. `action_paths[]` -> `rules/fields/action-paths-generation.md`
4. `block_types[].description` -> `rules/fields/block-description-generation.md`
5. `tags[].value_hint` -> `rules/fields/value-hint-generation.md`
6. `tags[].context_hint` -> `rules/fields/context-hint-generation.md`
7. `tags[].anchor_binding` -> `rules/fields/anchor-binding-parsing.md`

### hint 生成

1. `tagging-hint.md` -> `rules/hints/tagging-hint-generation.md`
2. `assembly-hint.md` -> `rules/hints/assembly-hint-generation.md`
3. `block-summary-hint.md` -> `rules/hints/block-summary-hint-generation.md`
4. `page-summary-hint.md` -> `rules/hints/page-summary-hint-generation.md`
5. `continuation-hint.md` -> `rules/hints/continuation-hint-generation.md`

## 硬约束

1. 不得阶段倒置。
2. 不得读取未授权材料补足生成内容。
3. 不得把结构校验材料当成生成依据。
4. 不得把人类说明文档当成默认执行输入。
5. 不得隐藏自动决策和剩余风险。
6. 不得用规则外私有模板替代字段生成规则。
7. 允许使用脚本执行单阶段的机械工作；禁止使用单个黑箱脚本跨越多个阶段并直接产出最终结果。
8. 脚本只处理当前阶段允许处理的对象，并真实产出该阶段规定的中间结果。
9. 遇到 blocking 条件时，脚本必须停止，不得继续生成 final。
10. 不得用泛化模板句批量替代字段或 hint 的专属规则执行。
11. 不得在 Stage 7 删除 Stage 6 已显式生成的字段或文件。
12. 不得把空编码具名 tag 伪恢复成 `TAG_U...` 一类正式 id；无显式恢复源时必须走 placeholder 或 blocked。
13. Final Review 的待补项必须以 `final-review/` 或最终交付层为准，不得只引用 `skeleton/`。

## 输出要求

最终必须输出：

1. 中间产物目录
2. `skeleton/`
3. `semantic-draft/`
4. `final-review/`
5. 最终交付目录
6. `slot-manifest.json`
7. `validation-report.json`
8. `audit-report.md`
9. `final-report.md`
