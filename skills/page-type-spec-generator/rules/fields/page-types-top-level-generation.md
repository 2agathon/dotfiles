# page-types 顶层字段生成规则

## 目标对象

生成 `page-types.data.json` 与 `page-types.tree.json` 的顶层字段。

## 适用字段

1. `version`
2. `description`
3. `last_updated`
4. `schema_meta`
5. `sources`

## Stage 6：Skeleton

1. `version`：无稳定来源时填 `__PTSG_PENDING__`。
2. `description`：使用固定模板即可。
3. `last_updated`：有稳定运行日就写运行日；否则占位。
4. `schema_meta`：必须显式生成对象。
5. `sources`：必须显式生成数组；无来源时为空数组。

## Stage 7：Semantic Draft

1. `description` 应收束为一句简短范围说明。
2. `description` 应描述 taxonomy 或命名空间覆盖范围，不应绑定当前这次 run 的选中 type。
3. `version`、`owner` 等无稳定来源时允许继续保留占位。
4. `sources` 只有在确有来源时才写入。

## 禁止

1. 不得写技术生成句。
2. 不得编造来源、维护人或变更记录。
3. 不得把顶层字段写成与 taxonomy 范围无关的大段 prose。
4. 不得把 run 级上下文当作最终 `description` 的主体内容。

## 失败信号

1. 顶层字段缺失。
2. `description` 仍是技术生成句。
3. `sources` 出现编造条目。
