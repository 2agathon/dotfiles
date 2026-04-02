# 行分类规则

## 目标

把 `workbook.normalized.json` 中的每一行归入稳定的行类型，供身份解析阶段使用。

本阶段只负责分类，不负责最终身份裁决。

## 输入

1. `workbook.normalized.json`

## 输出

1. 每行的 `row_kind`

## 允许的 `row_kind`

1. `block_start`
2. `tag_candidate`
3. `helper_candidate`
4. `empty`
5. `unknown`

## 分类顺序

必须按以下顺序判断，先命中者优先：

1. `empty`
2. `block_start`
3. `tag_candidate`
4. `helper_candidate`
5. `unknown`

## 判定规则

### 1. `empty`

满足以下条件时，判为 `empty`：

1. 当前行所有规范字段均为空

### 2. `block_start`

满足以下条件时，判为 `block_start`：

1. `Block id` 非空

说明：

1. `block_start` 表示一个新 block 的起始行
2. `block_start` 行仍可能同时承载该 block 的首个 tag 定义
3. 若当前行同时满足 `tag_candidate` 的信号，`row_kind` 仍记为 `block_start`，但必须额外标记 `carries_tag_candidate = true`
4. 命中 `block_start` 后，不再把 `row_kind` 改写为更低优先级类型；首标签解析交由后续身份阶段处理

### 3. `tag_candidate`

满足以下条件时，判为 `tag_candidate`：

1. `tag名称` 非空
2. 且以下任一项非空：
   - `tag编码`
   - `tag定义`
   - `tag anchor binding`
   - `触发模式`
   - `正例`
   - `反例`
   - `必须`
   - `Block role`

说明：

1. `tag_candidate` 只表示“这行可能参与标签定义”，不等于最终一定进入根级 `tags[]`

### 4. `helper_candidate`

满足以下条件时，判为 `helper_candidate`：

1. `tag名称` 为空或不足以构成独立标签名
2. `Block role` 非空，或当前行明显只在补充 block 级说明
3. 且不满足 `block_start` 与 `tag_candidate`

说明：

1. `helper_candidate` 只是候选，不代表最终一定降为 helper

### 5. `unknown`

未命中以上任一规则时，判为 `unknown`

说明：

1. `unknown` 行不得静默丢弃
2. 必须在后续阶段进入问题记录或继续人工审查

## 行归属辅助规则

### 1. block 归属链

1. `block_start` 行开启新的 block 归属链
2. 后续连续行若未遇到新的 `block_start`，则默认归属于最近的 `block_start`

### 2. `tag_candidate` 的 block 归属

1. 若当前行不是 `block_start`，但处于某个已开启 block 归属链下，则默认归属于最近的 block
2. 若当前行无法归属于任何 block，则标记为异常情况，进入后续身份问题记录

## 记录要求

每一行完成分类后，必须至少保留：

1. `row_index`
2. `row_kind`
3. 当前 block 归属状态
4. `carries_tag_candidate`（仅 `block_start` 行需要；其他行默认 `false`）

## 禁止

1. 不得在本阶段决定某个 `tag_candidate` 最终是 `recoverable_tag` 还是 `helper_only`
2. 不得在本阶段生成 canonical id
3. 不得因为当前行难判就直接跳过

## 失败信号

以下情况说明本阶段未完成：

1. 存在未分类行但没有标记为 `unknown`
2. `tag_candidate` 行无法回溯其 block 归属状态
3. `helper_candidate` 被直接当成最终 helper 身份
4. `block_start` 行没有形成新的 block 归属链
5. `block_start` 行明明携带 tag 定义信号，但没有被标记为 `carries_tag_candidate`
