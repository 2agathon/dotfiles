---
name: page-type-spec-generator
description: >
  从业务 xlsx 设计稿生成页类型配置文件。
  触发：用户提供 xlsx 并要求生成 spec、转成配置、新建或维护页类型。
---

# page-type-spec-generator

## 目标

把输入 xlsx 转换为：

1. 中间产物
2. `page-types.data.json`
3. `page-types.tree.json`
4. `types/{TYPE_ID}/page-semantic-spec.json`
5. 各类 hint 文件

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

## 执行规则

1. 必须按 `rules/pipeline/stages.md` 的阶段顺序执行。
2. 必须按 `rules/field-source-matrix.md` 限制每个对象可读取的规则文件。
3. 生成内容时只使用 `rules/*`。
4. 结构校验时只使用 `schema/*`。
5. 若某对象无法仅凭指定 `rules/*` 生成，停止扩展读取范围，改为记录问题并等待补 rule。
6. 若任一必填 ID 为空或任一对象进入 `blocked`，必须停止后续阶段。

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
2. `skeleton/` 只承担结构闭合和占位职责。
3. 若 `identity-map.json` 与 `skeleton/` 冲突，必须以 `identity-map.json` 为准。
4. 生成字段时，只读取该字段在 `field-source-matrix.md` 中指定的 rule。

### Stage 8-9

执行：

1. `validation`
2. `final handoff`

要求：

1. 校验只负责检查，不负责继续补写正式内容。
2. 最终交付目录必须从 `semantic-draft/` 派生。
3. 不得绕过 `semantic-draft/` 另写一份最终结果。
4. 只要存在 blocking，不得输出正式最终结果。

## 字段与 hint 路由

### 字段生成

1. `block_types[].description` -> `rules/fields/block-description-generation.md`
2. `tags[].value_hint` -> `rules/fields/value-hint-generation.md`
3. `tags[].context_hint` -> `rules/fields/context-hint-generation.md`
4. `tags[].anchor_binding` -> `rules/fields/anchor-binding-parsing.md`

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

## 输出要求

最终必须输出：

1. 中间产物目录
2. 最终交付目录
3. `validation-report.json`
4. `audit-report.md`
5. `final-report.md`
