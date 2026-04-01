# 身份解析规则

## 目标

从 `workbook.normalized.json` 解析出稳定的 namespace/category/type/block/tag 身份，以及 block 与 tag 的引用关系。

## 输入

1. `workbook.normalized.json`
2. `rules/parsing/row-classification.md`
3. `rules/parsing/id-normalization.md`
4. `rules/pipeline/state-and-placeholder-policy.md`

## 输出

1. `identity-map.json`
2. `identity-issues.md`

## 总规则

1. 本阶段只决定身份，不生成高自由度语义字段。
2. 本阶段必须给每个候选对象一个终态。
3. 终态未决时不得进入后续阶段。

## 终态

tag 身份终态只允许：

1. `resolved_explicit`
2. `resolved_recovered`
3. `resolved_placeholder`
4. `helper_only`
5. `invalid_or_noise`
6. `blocked`

## 准入规则

### 允许进入根级对象集合

1. `resolved_explicit`
2. `resolved_recovered`
3. `resolved_placeholder`

### 禁止进入根级对象集合

1. `helper_only`
2. `invalid_or_noise`
3. `blocked`

## namespace/category/type/block 解析

### namespace

1. 直接使用规范化后的 `namespace`
2. 若缺失且无法继承，标记 `blocked`

### category

1. 从 `category_id/category_name/category_description` 建立 category 身份
2. `category.id` 必须通过 `id-normalization.md` 生成非空 canonical id
3. 同一 `type` 下若出现多个冲突 category，标记 `blocked`

### type

1. 从 `type_id/type_name` 建立 type 身份
2. `type.id` 必须通过 `id-normalization.md` 生成非空 canonical id
3. 同一 `type_id` 必须对应单一稳定 type 身份

### block

1. `Block id` 非空时开启新的 block 身份
2. `block.id` 必须通过 `id-normalization.md` 生成非空 canonical id
3. 同一 canonical block id 必须对应同一 block 身份

## tag 解析

### Step 1：判定候选来源

只处理以下行：

1. `row_kind = tag_candidate`
2. `row_kind = helper_candidate`

### Step 2：判定 tag 终态

#### `resolved_explicit`

条件：

1. `tag名称` 非空
2. `tag编码` 非空

动作：

1. 通过 `id-normalization.md` 规范化 `tag编码`
2. 建立非空 canonical id

#### `resolved_recovered`

条件：

1. `tag名称` 非空
2. `tag编码` 为空
3. 存在语义同源的显式 tag，或可由稳定语义生成非空 canonical id

动作：

1. 优先继承显式 canonical id
2. 否则按 `id-normalization.md` 生成稳定 canonical id

#### `resolved_placeholder`

条件：

1. 当前 tag 按流程必须存在
2. 正常恢复路径无法得到非空 canonical id
3. 当前问题不是多候选歧义

动作：

1. 按 `id-normalization.md` 生成稳定占位符 id
2. 记录占位原因

#### `helper_only`

条件：

1. 当前行只承担 block 内辅助作用
2. 不在定义可进入根级集合的 tag

#### `invalid_or_noise`

条件：

1. 当前行不构成可消费对象

#### `blocked`

条件：

1. 存在多个同样合理的身份解释
2. 无法确定应继承哪个 canonical id
3. namespace/category/type/block 上游身份本身未稳定

动作：

1. 记录问题
2. 阻断后续阶段

## 空 `tag编码` 行规则

1. `tag名称` 非空且落在标签定义区时，默认先进入恢复流程。
2. 不得因 `tag编码` 为空而直接丢弃。
3. 不得因存在 `Block role` 就直接降为 `helper_only`。
4. 恢复失败时，必须在 `resolved_placeholder` 与 `blocked` 之间二选一；不得返回空字符串 ID。

## 引用关系规则

1. block 只引用 canonical tag id，不重复定义 tag 身份。
2. 同一 block 内对同一 `tag_id + role` 的重复引用只保留一次。
3. 若某 block 引用到 `blocked/helper_only/invalid_or_noise` 的 tag，必须记录问题，不得进入最终结果。

## `identity-map.json` 最小字段

每个 tag 至少包含：

1. `canonical_id`
2. `name`
3. `identity_state`
4. `source_rows`
5. `placeholder_reason`（仅 `resolved_placeholder` 时）

## `identity-issues.md` 必记内容

必须记录：

1. 空 `tag编码` 行的处理结果
2. 占位符生成记录
3. 身份冲突
4. `blocked` 对象

## 阻断条件

满足以下任一条件时，本阶段必须判定失败：

1. 任一 canonical id 为空字符串
2. 任一对象进入 `blocked`
3. 同一对象得到多个 canonical id
4. 明显不同对象得到同一 canonical id 且无法收敛

## 禁止

1. 不得在本阶段生成 `value_hint`
2. 不得在本阶段生成 `context_hint`
3. 不得在本阶段生成 `anchor_binding`
4. 不得在本阶段生成 block description

## 失败信号

以下情况说明本阶段未完成：

1. 空 `tag编码` 行没有处理记录
2. 任何 ID 为空字符串
3. `blocked` 对象进入后续阶段
4. 身份冲突被静默吞掉
