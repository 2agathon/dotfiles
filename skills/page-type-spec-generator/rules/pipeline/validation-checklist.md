# 校验门禁

## 总规则

1. 本阶段负责门禁，不负责继续补写正式内容。
2. 每项检查结果必须归入：`blocking`、`warning`、`pass`。
3. 存在任一 `blocking` 时，不得通过到最终交付。

## Blocking Gates

### 1. schema 失败

以下任一失败，记为 `blocking`：

1. `page-types.data.json` 不符合 `schema/page-types.schema.json`
2. `page-types.tree.json` 不符合 `schema/page-types.schema.json`
3. `page-semantic-spec.json` 不符合 `schema/page-semantic.schema.json`

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

### 5. 最终结果绕过 semantic draft

以下任一失败，记为 `blocking`：

1. 最终交付目录不是从 `semantic-draft/` 派生
2. 最终交付目录与 `semantic-draft/` 的核心对象集合不一致

## Warning Gates

### 6. 占位符进入最终结果

以下情况记为 `warning`：

1. 存在 `resolved_placeholder` 对象进入最终结果

### 7. `value_hint` 模板化过强

以下情况记为 `warning`：

1. 多个不同 tag 的 `value_hint` 完全相同
2. `value_hint` 只剩通用句而缺少本标签区分信息

### 8. `context_hint` 异常稀少

以下情况记为 `warning`：

1. 当前 type 存在明显时间类或角色类标签，但 `context_hint` 全部为空

### 9. hint 贫血

以下情况记为 `warning`：

1. `tagging-hint.md`、`assembly-hint.md`、`block-summary-hint.md` 只有极少量泛化内容

## Pass Gates

### 10. 合法省略

以下情况可记为 `pass`：

1. `context_hint` 因无歧义而省略
2. `anchor_binding` 因原列为空而省略
3. `page-summary-hint.md` 无素材时输出空模板
4. `continuation-hint.md` 无素材时输出空模板

## 报告要求

### `validation-report.json`

必须包含：

1. `blocking`
2. `warnings`
3. `pass`
4. 最终总状态

### `audit-report.md`

必须写入：

1. 所有自动修复
2. 所有占位符生成
3. 所有 warning
4. 所有 blocking

## 最终状态规则

1. 若 `blocking` 非空，最终状态必须失败。
2. 若 `blocking` 为空但 `warnings` 非空，最终状态为通过但有风险。
3. 只有 `blocking` 为空时，才允许生成最终交付目录。
