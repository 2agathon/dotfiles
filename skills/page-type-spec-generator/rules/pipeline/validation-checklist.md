# 校验门禁

## 总规则

1. 本阶段负责门禁，不负责继续补写正式内容。
2. 每项检查结果必须归入：`blocking`、`warning`、`pass`。
3. 存在任一 `blocking` 时，不得通过到最终交付。
4. 校验必须区分结构状态、语义状态与 review-ready 状态。

## Blocking Gates

### 1. review schema 失败

以下任一失败，记为 `blocking`：

1. `page-types.data.json` 不符合 `schema/review/page-types.schema.json`
2. `page-types.tree.json` 不符合 `schema/review/page-types.schema.json`
3. `page-semantic-spec.json` 不符合 `schema/review/page-semantic.schema.json`

### 2. 必填 ID 为空

以下任一为空字符串，记为 `blocking`：

1. `page_type.id`
2. `block_types[].id`
3. 根级 `tags[].id`
4. `block_types[].tags[].tag_id`
5. `categories[].id`
6. `types[].id`

### 3. 身份阻断未被拦截

以下任一出现，记为 `blocking`：

1. `identity-map.json` 中存在 `blocked`
2. `helper_only`、`invalid_or_noise` 被写入最终根级对象集合
3. `identity-map.json` 与最终结果中的对象 id 不一致

### 4. 引用闭合失败

以下任一失败，记为 `blocking`：

1. `block_types[].tags[].tag_id` 在根级 `tags[]` 中找不到
2. block/tag 存在重复 ID 冲突且未收敛
3. `action_paths[].block_type_ids` 中的值在 `block_types[].id` 中找不到

### 5. 最终结果绕过 semantic draft / final review

以下任一失败，记为 `blocking`：

1. 最终交付目录不是从 `final-review/` 派生
2. `final-review/` 不是从 `semantic-draft/` 派生
3. 最终交付目录与 `semantic-draft/` 的核心对象集合不一致

### 6. type 污染

以下任一失败，记为 `blocking`：

1. `page-semantic-spec.json` 中的 `block_types[].id` 不属于当前选中 type 的 identity-map block 集合
2. `page-semantic-spec.json` 中的根级 `tags[].id` 不属于当前选中 type 的 identity-map tag 集合
3. 最终结果混入未选中 type 的对象

### 7. block 首标签缺失

以下任一失败，记为 `blocking`：

1. `workbook.normalized.json` 中 `block_start` 行携带首标签定义信号，但 `identity-map.json` 中没有对应 tag 身份
2. `identity-map.json` 中存在来自 `block_start` 首标签行的 tag，但最终 `page-semantic-spec.json` 未包含该 tag

### 8. 空编码伪恢复 ID

以下任一失败，记为 `blocking`：

1. `raw_id` 为空的具名 tag 被标记为 `resolved_recovered`，但没有 `recovery_source`
2. 缺失原始 ID 的 tag 最终使用 `TAG_U...` 一类非占位 canonical id

### 9. 槽位清单失真

以下任一失败，记为 `blocking`：

1. `slot-manifest.json` 缺失
2. 结果文件中的显式槽位与 `slot-manifest.json` 记录不一致
3. 某个必填字段存在于结果文件但未出现在 `slot-manifest.json`
4. `final-review/` 中存在显式占位，但 `pending_slots` 未列出该槽位

## Warning Gates

### 8. 显式占位进入最终结果

以下情况记为 `warning`：

1. 存在 `resolved_placeholder` 对象进入最终结果
2. 存在 `__PTSG_PENDING__` 残留
3. `pending_slots` 统计层级不是 `final-review` 或最终交付层

### 9. `value_hint` 仍为骨架模板态

以下情况记为 `warning`：

1. 多个不同 tag 的 `value_hint` 仍保留完全相同的骨架模板结构
2. `value_hint` 只剩字段头拼接而缺少语义收束
3. 主识别句主要由通用模板构成，缺少当前 tag 的专属识别信号

### 10. `context_hint` 异常稀少或异常泛化

以下情况记为 `warning`：

1. 当前 type 存在明显时间类或角色类标签，但 `context_hint` 全部保留占位或全部泛化
2. 明显低歧义标签被错误补写长句

### 11. hint 贫血或模板化

以下情况记为 `warning`：

1. `tagging-hint.md`、`assembly-hint.md`、`block-summary-hint.md` 只有极少量泛化内容
2. 同一句泛化提醒被换名后批量套用
3. hint 文件仍停留在 skeleton 模板态

### 12. 规则替代

以下情况记为 `warning`：

1. 某阶段结果明显由通用私有模板生成，而非对应 rule 约束的结果形态

### 13. 人工待补项较多

以下情况记为 `warning`：

1. `pending_slots` 达到当前 type 可见槽位的一定比例
2. 关键说明型字段仍大面积保留占位

## Pass Gates

### 14. 合法显式占位

以下情况可记为 `pass`：

1. `context_hint` 在 skeleton 与 final-review 中显式保留占位，且已被标记为 `pending_human`
2. `page-summary-hint.md` 无素材时输出显式空模板
3. `continuation-hint.md` 无素材时输出显式空模板
4. schema 要求但 Excel 无来源的字段已显式占位并进入待补清单

## 报告要求

### `validation-report.json`

必须包含：

1. `structure_status`
2. `semantic_status`
3. `review_readiness_status`
4. `blocking`
5. `warnings`
6. `pass`
7. `pending_slots`
8. `status`

### `audit-report.md`

必须写入：

1. 所有自动修复
2. 所有占位符生成
3. 所有 warning
4. 所有 blocking
5. 所有人工待补项

## 最终状态规则

1. 若 `blocking` 非空，最终状态必须失败。
2. 若 `blocking` 为空但 `warnings` 非空，最终状态为通过但有风险。
3. 只有 `blocking` 为空时，才允许生成最终交付目录。
