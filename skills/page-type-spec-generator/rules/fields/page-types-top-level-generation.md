# page-types 顶层字段生成规则

## 目标

生成 `page-types.data.json` 与 `page-types.tree.json` 的顶层字段。

这些字段主要服务于 taxonomy 管理、人工 review 与版本治理，不是主要的 LLM prompt 输入。因此写法要求是：

1. 简洁
2. 事实化
3. 不臆造来源

## 适用字段

1. `version`
2. `description`
3. `last_updated`
4. `schema_meta`
5. `sources`

## 总规则

1. Skeleton 阶段必须显式生成以上字段。
2. 若 Excel 或运行上下文无来源，必须显式占位或保留空结构。
3. Semantic Draft 阶段只做最小润色，不要把治理字段写成大段说明文。

## Stage 6：Skeleton

### `version`

1. 必须显式生成。
2. 若当前没有稳定版本来源，填 `__PTSG_PENDING__`。

### `description`

1. 必须显式生成。
2. 使用固定模板即可：`命名空间：{namespace}；当前选中类型：{TYPE_ID}；状态：__PTSG_PENDING__。`

### `last_updated`

1. 必须显式生成。
2. 若本次 run 的日期就是期望口径，可直接写运行日。
3. 若日期口径仍需人工确认，填 `__PTSG_PENDING__`。

### `schema_meta`

1. 必须显式生成对象。
2. 无来源字段保留空数组、空对象或占位值。

### `sources`

1. 必须显式生成数组。
2. 没有稳定来源时保留空数组，不要臆造标准或文献。

## Stage 7：Semantic Draft

1. `description` 应收束为一句简短范围说明。
2. `description` 应描述 taxonomy 文件或命名空间的覆盖范围，不应绑定当前这次 run 的选中 type。
3. `version`、`owner` 等无稳定来源时允许继续保留占位。
4. `sources` 只有在确有来源时才写入。

## 禁止

1. 不得写“Generated from workbook ...”这类弱模板句。
2. 不得编造来源、维护人或变更记录。
3. 不得把顶层字段写成与 type 识别无关的大段 prose。
4. 不得把“当前选中类型是 X”这类 run 级上下文当作最终 `description` 的主体内容。

## 失败信号

1. 顶层字段缺失。
2. `description` 仍是技术生成句。
3. `sources` 出现编造条目。
