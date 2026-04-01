# 字段来源矩阵

## 使用规则

1. 生成内容时，只能读取本矩阵为该对象指定的 `rules/*`。
2. 结构校验时，只能读取本矩阵为该对象指定的 `schema/*`。
3. 未在本矩阵中列出的材料，不得作为默认执行输入。
4. 如果某对象无法仅凭指定的 `rules/*` 生成，说明对应 rule 不完整，应补 rule，不应扩展 Agent 读取范围。

## 矩阵

| 目标对象 | 允许读取的 rules | 允许读取的 schema | 阶段 |
|---|---|---|---|
| `run-manifest.json` | `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/interaction-points.md` | — | Stage 0 |
| `workbook.raw.json` | `rules/parsing/workbook-parsing.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | — | Stage 1 |
| `workbook.normalized.json` | `rules/parsing/header-normalization.md`, `rules/parsing/row-classification.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | — | Stage 2 |
| `normalization-report.md` | `rules/parsing/header-normalization.md`, `rules/parsing/row-classification.md`, `rules/pipeline/artifacts.md` | — | Stage 2 |
| `identity-map.json` | `rules/parsing/identity-resolution.md`, `rules/parsing/row-classification.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | — | Stage 3 |
| `identity-issues.md` | `rules/parsing/identity-resolution.md`, `rules/pipeline/artifacts.md` | — | Stage 3 |
| `page-types.data.json` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | `schema/page-types.schema.json` | Stage 5 / Stage 6 |
| `page-types.tree.json` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | `schema/page-types.schema.json` | Stage 5 / Stage 6 |
| `page_type.id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/stages.md` | `schema/page-semantic.schema.json` | Stage 6 |
| `block_types[].id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md` | `schema/page-semantic.schema.json` | Stage 6 |
| `block_types[].tags[]` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md` | `schema/page-semantic.schema.json` | Stage 6 |
| `tags[].id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md` | `schema/page-semantic.schema.json` | Stage 6 |
| `block_types[].description` | `rules/fields/block-description-generation.md` | `schema/page-semantic.schema.json` | Stage 7 |
| `tags[].value_hint` | `rules/fields/value-hint-generation.md` | `schema/page-semantic.schema.json` | Stage 7 |
| `tags[].context_hint` | `rules/fields/context-hint-generation.md` | `schema/page-semantic.schema.json` | Stage 7 |
| `tags[].anchor_binding` | `rules/fields/anchor-binding-parsing.md` | `schema/page-semantic.schema.json` | Stage 7 |
| `tagging-hint.md` | `rules/hints/tagging-hint-generation.md` | — | Stage 7 |
| `assembly-hint.md` | `rules/hints/assembly-hint-generation.md` | — | Stage 7 |
| `block-summary-hint.md` | `rules/hints/block-summary-hint-generation.md` | — | Stage 7 |
| `page-summary-hint.md` | `rules/hints/page-summary-hint-generation.md` | — | Stage 7 |
| `continuation-hint.md` | `rules/hints/continuation-hint-generation.md` | — | Stage 7 |
| `validation-report.json` | `rules/pipeline/validation-checklist.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | `schema/page-types.schema.json`, `schema/page-semantic.schema.json` | Stage 8 |
| `audit-report.md` | `rules/pipeline/validation-checklist.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/interaction-points.md` | — | Stage 8 |
| `final-report.md` | `rules/pipeline/artifacts.md`, `rules/pipeline/interaction-points.md`, `rules/pipeline/stages.md` | — | Stage 9 |

## 对象约束

### 身份优先级

1. `identity-map.json` 是身份真相。
2. `skeleton/` 只承担结构闭合和占位职责。
3. 若 `identity-map.json` 与 `skeleton/` 冲突，必须以 `identity-map.json` 为准。

### `tags[].value_hint`

1. 只允许读取 `rules/fields/value-hint-generation.md`。
2. 不得读取其他字段规则来补足内容。

### `tags[].context_hint`

1. 只允许读取 `rules/fields/context-hint-generation.md`。
2. 不得读取其他字段规则来补足内容。

### `tags[].anchor_binding`

1. 只允许读取 `rules/fields/anchor-binding-parsing.md`。
2. 不得读取其他字段规则来补足内容。

### hint 文件

1. 每个 hint 文件只允许读取自己的生成 rule。
2. 不得为了生成某个 hint 文件而默认读取其他 hint 的 rule。

## 失败信号

以下情况说明当前规则体系不完整：

1. 某对象无法仅凭本矩阵指定的 `rules/*` 生成。
2. 某对象需要读取本矩阵未指定的材料才能生成。
3. 某对象需要依赖历史样例才能决定写法。
4. 某对象需要依赖人类说明文档才能确定语义边界。
