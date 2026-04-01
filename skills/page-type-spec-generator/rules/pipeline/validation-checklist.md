# 校验清单

## 总规则

1. 校验阶段只负责检查，不负责继续补写正式内容。
2. 每项检查必须给出明确结果：通过 / 警告 / 失败。
3. 失败项必须进入 `validation-report.json`。
4. 警告项必须进入 `audit-report.md`。

## 结构校验

### 1. `page-types.data.json`

必须检查：

1. 是否符合 `schema/page-types.schema.json`
2. 顶层必填字段是否存在
3. `categories` 是否为数组
4. `types` 是否为数组

### 2. `page-types.tree.json`

必须检查：

1. 是否符合 `schema/page-types.schema.json`
2. 顶层必填字段是否存在
3. `categories` 是否为数组
4. `types` 是否为数组

### 3. `page-semantic-spec.json`

必须检查：

1. 是否符合 `schema/page-semantic.schema.json`
2. `page_type.id` 是否存在
3. `block_types` 是否为数组
4. `tags` 是否为数组

## 引用闭合检查

### 4. block 引用闭合

必须检查：

1. `block_types[].tags[].tag_id` 是否都能在根级 `tags[]` 找到

### 5. 标签唯一性

必须检查：

1. 根级 `tags[]` 中是否存在重复 `id`

### 6. block 唯一性

必须检查：

1. `block_types[]` 中是否存在重复 `id`

## 中间产物完整性检查

### 7. 阶段产物存在性

必须检查：

1. `run-manifest.json`
2. `workbook.raw.json`
3. `workbook.normalized.json`
4. `identity-map.json`
5. `skeleton/`
6. `semantic-draft/`

### 8. 类型选择记录

必须检查：

1. `run-manifest.json` 中是否记录了检测到的 `type`
2. `run-manifest.json` 中是否记录了选中的 `type`

### 9. 身份问题记录

必须检查：

1. 若存在空 `tag编码` 行，`identity-issues.md` 中是否有记录
2. `identity-map.json` 中是否保留其分类结果

## 空 `tag编码` 行检查

### 10. 保留检查

必须检查：

1. 空 `tag编码` 且落在标签定义区的行，是否被保留为某种身份结果
2. 是否存在被静默丢弃的此类行

### 11. 分类检查

必须检查：

1. 是否记录为 `recoverable_tag`、`helper_only` 或其他合法分类
2. 若降为 `helper_only`，是否满足降级条件

## 骨架与 draft 分层检查

### 12. `skeleton/` 检查

必须检查：

1. `skeleton/` 中是否只承担结构闭合职责
2. 是否存在高自由度语义内容被提前定稿

### 13. `semantic-draft/` 检查

必须检查：

1. `semantic-draft/` 是否包含完整 draft 内容
2. 最终交付目录是否从 `semantic-draft/` 派生

## 字段职责检查

### 14. `block_types[].description`

必须检查：

1. 是否在描述块语义范围
2. 是否夹带执行策略

### 15. `tags[].value_hint`

必须检查：

1. 是否由 `rules/fields/value-hint-generation.md` 约束生成
2. 是否存在明显拼接痕迹
3. 是否包含不必要的标签头或模板残留

### 16. `tags[].context_hint`

必须检查：

1. 是否由 `rules/fields/context-hint-generation.md` 约束生成
2. 是否越界成解释型说明
3. 是否写入来源位置、判读依据或 OCR 过程

### 17. `tags[].anchor_binding`

必须检查：

1. 是否结构合法
2. 是否保留关键字段
3. 是否存在关键字段缺失却被静默补写

## hint 分层检查

### 18. `tagging-hint.md`

必须检查：

1. 是否只承载段打标相关规则
2. 是否误写组装策略

### 19. `assembly-hint.md`

必须检查：

1. 是否承载块组装执行策略
2. 是否误写标签取值规则

### 20. `block-summary-hint.md`

必须检查：

1. 是否承载块摘要偏好
2. 是否误写组装规则

### 21. `page-summary-hint.md`

必须检查：

1. 是否承载页摘要偏好
2. 若无素材，是否为空模板

### 22. `continuation-hint.md`

必须检查：

1. 是否承载续写判定规则
2. 若无素材，是否为空模板

## 交互与报告检查

### 23. 交互协议检查

必须检查：

1. 是否在类型枚举后才询问用户选 `type`
2. 是否把机械修复错误升级成硬交互

### 24. 报告完整性检查

必须检查：

1. `audit-report.md` 是否写入自动修复
2. `audit-report.md` 是否写入未决问题
3. `final-report.md` 是否写入自动决策
4. `final-report.md` 是否写入剩余风险

## 输出要求

校验阶段结束后，必须输出：

1. `validation-report.json`
2. `audit-report.md`

如果存在失败项，不得把结果标记为完全完成。
