# 字段来源矩阵

## 使用规则

1. 生成内容时，只能读取本矩阵为该对象指定的 `rules/*`。
2. review-ready 结构校验时，只能读取本矩阵为该对象指定的 `schema/*`。
3. 未在本矩阵中列出的材料，不得作为默认执行输入。
4. 如果某对象无法仅凭指定的 `rules/*` 生成，说明对应 rule 不完整，应补 rule，不应扩展 Agent 读取范围。
5. 执行时必须先定位当前阶段，只读取该阶段小节，不得跨节取用其他阶段的写权限。
6. 若某阶段在本矩阵中没有该对象的行，表示该阶段不得生成、重写或补写该对象。
7. Skeleton 阶段只允许输出结构闭合、模板展开、显式占位。
8. Semantic Draft 阶段只允许替换 Stage 6 已显式落槽的对象，不得新增字段或章节。
9. Final Review 与 Final Handoff 只允许派生、检查、报告，不得回写业务字段。

## Stage 0-5 前置产物矩阵

| 阶段 | 产物 | 允许读取的 rules | 允许读取的 schema | 允许输出形态 |
|---|---|---|---|---|
| Stage 0 | `run-manifest.json` | `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/interaction-points.md` | — | 运行真相 |
| Stage 1 | `workbook.raw.json` | `rules/parsing/workbook-parsing.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | — | 原始解析结果 |
| Stage 2 | `workbook.normalized.json` | `rules/parsing/header-normalization.md`, `rules/parsing/row-classification.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | — | 规范化结果 |
| Stage 2 | `normalization-report.md` | `rules/parsing/header-normalization.md`, `rules/parsing/row-classification.md`, `rules/pipeline/artifacts.md` | — | 规范化摘要 |
| Stage 3 | `identity-map.json` | `rules/parsing/identity-resolution.md`, `rules/parsing/row-classification.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md` | — | 身份真相 |
| Stage 3 | `identity-issues.md` | `rules/parsing/identity-resolution.md`, `rules/pipeline/artifacts.md` | — | 身份问题摘要 |
| Stage 5 | `existence-check.json` | `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/state-and-placeholder-policy.md` | — | 存在性检查结果 |

## Stage 6 Skeleton 来源矩阵

| 产物文件 | 逻辑对象 / 章节 | 允许读取的 rules | 目标 schema | 允许输出形态 |
|---|---|---|---|---|
| `slot-manifest.json` | 根对象 | `rules/pipeline/slot-manifest-contract.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/stages.md` | — | 槽位清单初始化 |
| `skeleton/page-types.data.json` | 顶层字段 | `rules/fields/page-types-top-level-generation.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md` | `schema/review/page-types.schema.json` | 结构闭合 + 显式占位 |
| `skeleton/page-types.data.json` | `categories[]`, `types[].id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/state-and-placeholder-policy.md` | `schema/review/page-types.schema.json` | 结构真相或稳定占位 |
| `skeleton/page-types.data.json` | `types[].description` | `rules/fields/type-description-generation.md` | `schema/review/page-types.schema.json` | 固定模板 |
| `skeleton/page-types.tree.json` | 顶层字段 | `rules/fields/page-types-top-level-generation.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md` | `schema/review/page-types.schema.json` | 结构闭合 + 显式占位 |
| `skeleton/page-types.tree.json` | `categories[]`, `types[].id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/state-and-placeholder-policy.md` | `schema/review/page-types.schema.json` | 结构真相或稳定占位 |
| `skeleton/page-types.tree.json` | `types[].description` | `rules/fields/type-description-generation.md` | `schema/review/page-types.schema.json` | 固定模板 |
| `skeleton/page-semantic-spec.json` | `page_type.id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/stages.md` | `schema/review/page-semantic.schema.json` | 结构真相或稳定占位 |
| `skeleton/page-semantic-spec.json` | `action_paths[]` | `rules/fields/action-paths-generation.md`, `rules/pipeline/state-and-placeholder-policy.md` | `schema/review/page-semantic.schema.json` | 空结构或占位结构 |
| `skeleton/page-semantic-spec.json` | `block_types[].id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/state-and-placeholder-policy.md` | `schema/review/page-semantic.schema.json` | 结构真相或稳定占位 |
| `skeleton/page-semantic-spec.json` | `block_types[].tags[]` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/state-and-placeholder-policy.md` | `schema/review/page-semantic.schema.json` | 结构真相 |
| `skeleton/page-semantic-spec.json` | `block_types[].description` | `rules/fields/block-description-generation.md` | `schema/review/page-semantic.schema.json` | 固定模板：块对象 / 块语义 / 语义维度 |
| `skeleton/page-semantic-spec.json` | `tags[].id/name` | `rules/parsing/identity-resolution.md`, `rules/parsing/id-normalization.md`, `rules/pipeline/state-and-placeholder-policy.md` | `schema/review/page-semantic.schema.json` | 结构真相或稳定占位 |
| `skeleton/page-semantic-spec.json` | `tags[].value_hint` | `rules/fields/value-hint-generation.md` | `schema/review/page-semantic.schema.json` | 固定模板：定义 / 触发 / 正例 / 反例 / 必须 |
| `skeleton/page-semantic-spec.json` | `tags[].context_hint` | `rules/fields/context-hint-generation.md` | `schema/review/page-semantic.schema.json` | 显式字段 + `__PTSG_PENDING__` |
| `skeleton/page-semantic-spec.json` | `tags[].anchor_binding` | `rules/fields/anchor-binding-parsing.md` | `schema/review/page-semantic.schema.json` | 结构化对象或占位对象 |
| `skeleton/tagging-hint.md` | 全文件 | `rules/hints/tagging-hint-generation.md` | — | 固定章节骨架 + 显式占位 |
| `skeleton/assembly-hint.md` | 全文件 | `rules/hints/assembly-hint-generation.md` | — | 固定章节骨架 + 显式占位 |
| `skeleton/block-summary-hint.md` | 全文件 | `rules/hints/block-summary-hint-generation.md` | — | 摘要模板槽位骨架 + 显式占位 |
| `skeleton/page-summary-hint.md` | 全文件 | `rules/hints/page-summary-hint-generation.md` | — | 固定章节骨架 + 显式占位 |
| `skeleton/continuation-hint.md` | 全文件 | `rules/hints/continuation-hint-generation.md` | — | 固定章节骨架 + 显式占位 |

## Stage 7 Semantic Draft 来源矩阵

执行约束：

1. Stage 7 的单次内容生成单位只允许是：一个 block、一个 tag、一个 hint 文件或一个 type description。
2. 脚本只允许复制 `skeleton/`、排队单元任务、分发单元任务和回写 `slot-manifest.json`。
3. 不得使用单个脚本步骤批量替换多个 `value_hint`、多个 `context_hint`、多个 block description 或多个 hint 文件内容。

| 产物文件 | 逻辑对象 / 章节 | 前置要求 | 允许读取的 rules | 允许输出形态 |
|---|---|---|---|---|
| `slot-manifest.json` | 根对象 | 已存在 Stage 6 槽位清单 | `rules/pipeline/slot-manifest-contract.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/stages.md` | 槽位状态回写 |
| `semantic-draft/page-types.data.json` | 顶层字段 | 已存在 Stage 6 显式字段 | `rules/fields/page-types-top-level-generation.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md` | 仅替换既有槽位为语义草稿 |
| `semantic-draft/page-types.data.json` | `types[].description` | 已存在 Stage 6 固定模板 | `rules/fields/type-description-generation.md` | 自然语言段落或保留占位 |
| `semantic-draft/page-types.tree.json` | 顶层字段 | 已存在 Stage 6 显式字段 | `rules/fields/page-types-top-level-generation.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md` | 仅替换既有槽位为语义草稿 |
| `semantic-draft/page-types.tree.json` | `types[].description` | 已存在 Stage 6 固定模板 | `rules/fields/type-description-generation.md` | 自然语言段落或保留占位 |
| `semantic-draft/page-semantic-spec.json` | `action_paths[]` | 已存在 Stage 6 空结构或占位结构 | `rules/fields/action-paths-generation.md`, `rules/pipeline/state-and-placeholder-policy.md` | 正式结构或保留占位结构 |
| `semantic-draft/page-semantic-spec.json` | `block_types[].description` | 已存在 Stage 6 固定模板 | `rules/fields/block-description-generation.md` | 自然语言段落 |
| `semantic-draft/page-semantic-spec.json` | `tags[].value_hint` | 已存在 Stage 6 固定模板 | `rules/fields/value-hint-generation.md` | 自然语言段落 |
| `semantic-draft/page-semantic-spec.json` | `tags[].context_hint` | 已存在 Stage 6 显式字段 | `rules/fields/context-hint-generation.md` | 最小语义短句或保留占位 |
| `semantic-draft/page-semantic-spec.json` | `tags[].anchor_binding` | 已存在 Stage 6 结构化对象或占位对象 | `rules/fields/anchor-binding-parsing.md` | 正式结构或保留占位对象 |
| `semantic-draft/tagging-hint.md` | 全文件 | 已存在 Stage 6 固定章节骨架 | `rules/hints/tagging-hint-generation.md` | 打标规则草稿 |
| `semantic-draft/assembly-hint.md` | 全文件 | 已存在 Stage 6 固定章节骨架 | `rules/hints/assembly-hint-generation.md` | 组装策略草稿 |
| `semantic-draft/block-summary-hint.md` | 全文件 | 已存在 Stage 6 摘要模板槽位骨架 | `rules/hints/block-summary-hint-generation.md` | 块摘要规则或模板草稿 |
| `semantic-draft/page-summary-hint.md` | 全文件 | 已存在 Stage 6 固定章节骨架 | `rules/hints/page-summary-hint-generation.md` | 页摘要规则草稿 |
| `semantic-draft/continuation-hint.md` | 全文件 | 已存在 Stage 6 固定章节骨架 | `rules/hints/continuation-hint-generation.md` | 续写判定规则草稿 |

## Stage 8 Final Review 校验矩阵

| 产物 | 检查对象 | 允许读取的 rules / schema | 检查维度 | 禁止动作 |
|---|---|---|---|---|
| `final-review/` | `semantic-draft/` 派生目录 | `rules/pipeline/validation-checklist.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/stages.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/slot-manifest-contract.md`, `schema/review/page-types.schema.json`, `schema/review/page-semantic.schema.json` | 派生闭合、type 污染、占位残留、模板残留 | 不得回写业务字段 |
| `validation-report.json` | 全部中间产物 | `rules/pipeline/validation-checklist.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/slot-manifest-contract.md`, `schema/review/page-types.schema.json`, `schema/review/page-semantic.schema.json` | 结构状态、语义状态、review-ready 状态 | 不得补写内容 |
| `audit-report.md` | 全部中间产物 | `rules/pipeline/validation-checklist.md`, `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/interaction-points.md`, `rules/pipeline/slot-manifest-contract.md` | 自动修复、风险、人工待补项 | 不得补写内容 |

## Stage 9 Final Handoff 收口矩阵

| 产物 | 允许读取的 rules | 允许输出形态 | 禁止动作 |
|---|---|---|---|
| `final-report.md` | `rules/pipeline/state-and-placeholder-policy.md`, `rules/pipeline/artifacts.md`, `rules/pipeline/interaction-points.md`, `rules/pipeline/stages.md`, `rules/pipeline/slot-manifest-contract.md` | 最终收口说明 | 不得回写业务字段 |

## 跨阶段对照索引

| 逻辑对象 | Stage 6 Skeleton 形态 | Stage 7 Semantic Draft 形态 | Stage 8 Final Review 关注点 |
|---|---|---|---|
| `types[].description` | 固定模板 | 自然语言段落或保留占位 | 检查弱模板残留 |
| `block_types[].description` | 固定模板 | 自然语言段落 | 检查是否混入执行策略 |
| `tags[].value_hint` | 固定模板 | 自然语言段落 | 检查模板残留与区分度 |
| `tags[].context_hint` | 显式字段 + 占位 | 最小语义短句或保留占位 | 检查误补 / 漏补 |
| `tags[].anchor_binding` | 结构化对象或占位对象 | 正式结构或保留占位对象 | 检查关键字段闭合 |
| `tagging-hint.md` | 固定章节骨架 | 打标规则草稿 | 检查批量套话 |
| `assembly-hint.md` | 固定章节骨架 | 组装策略草稿 | 检查越界写到摘要或取值 |
| `block-summary-hint.md` | 摘要模板槽位骨架 | 块摘要规则或模板草稿 | 检查是否误写组装逻辑 |
| `page-summary-hint.md` | 固定章节骨架 | 页摘要规则草稿 | 检查是否误写块级内容 |
| `continuation-hint.md` | 固定章节骨架 | 续写判定规则草稿 | 检查是否误写打标或组装内容 |

## 对象约束

### 身份优先级

1. `identity-map.json` 是身份真相。
2. `skeleton/` 只承担结构闭合、模板展开和占位职责。
3. 若 `identity-map.json` 与 `skeleton/` 冲突，必须以 `identity-map.json` 为准。
4. 若 `identity-map.json` 含有 `blocked` 或空 ID，不得继续进入 final。
5. Stage 7 生成对象必须限定在当前选中 type 的 identity 子集内。

### 阶段边界

1. Stage 6 只允许写 `Stage 6 Skeleton 来源矩阵` 中的行。
2. Stage 7 只允许写 `Stage 7 Semantic Draft 来源矩阵` 中的行。
3. Stage 8 只允许写 `Stage 8 Final Review 校验矩阵` 中的行。
4. Stage 9 只允许写 `Stage 9 Final Handoff 收口矩阵` 中的行。

## 失败信号

以下情况说明当前规则体系不完整或阶段边界被突破：

1. 某对象无法仅凭本矩阵指定的 `rules/*` 生成。
2. 某对象需要读取本矩阵未指定的材料才能生成。
3. 某对象需要依赖历史样例才能决定写法。
4. 某对象需要依赖人类说明文档才能确定语义边界。
5. 某阶段写入了本矩阵未授权的阶段产物。
6. Stage 7 试图新增 Stage 6 未显式落槽的字段或章节。
