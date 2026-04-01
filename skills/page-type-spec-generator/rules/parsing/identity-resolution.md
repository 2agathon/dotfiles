# 身份解析规则

## 目标

从 `workbook.normalized.json` 中解析出稳定的：

1. namespace 身份
2. category 身份
3. type 身份
4. block 身份
5. tag 身份
6. block 与 tag 的引用关系

本阶段负责“谁是谁”，不负责生成高自由度语义字段。

## 输入

1. `workbook.normalized.json`
2. `rules/parsing/row-classification.md`
3. `rules/parsing/id-normalization.md`

## 输出

1. `identity-map.json`
2. `identity-issues.md`

## 身份对象

### 1. namespace

来源：

1. `namespace`

规则：

1. 直接使用规范化后的值
2. 若值缺失且无法继承，记为问题

### 2. category

来源：

1. `category_id`
2. `category_name`
3. `category_description`

规则：

1. 同一 `type` 下的 category 身份必须稳定
2. 若同一 `type` 下出现多个冲突 category，记为问题

### 3. type

来源：

1. `type_id`
2. `type_name`

规则：

1. 同一 `type_id` 对应一个稳定的 type 身份
2. `type_id` 规范化后必须全局一致

### 4. block

来源：

1. `Block id`
2. `Block`
3. 当前 block 归属链

规则：

1. `Block id` 非空时开启新的 block 身份
2. 同一规范化 block id 应指向同一 block 身份
3. 同一 block 下可包含多行 `tag_candidate`

### 5. tag

来源：

1. `tag名称`
2. `tag编码`
3. 相关语义列
4. block 引用关系

规则：

1. 根级 tag 身份以规范化后的 canonical id 去重
2. block 只引用 tag，不重复定义 tag 身份

## tag 行分类结果

最终 tag 身份只允许以下状态：

1. `explicit_tag`
2. `recoverable_tag`
3. `helper_only`
4. `invalid_or_noise`

## 解析规则

### 1. `explicit_tag`

满足以下条件时，判为 `explicit_tag`：

1. `tag名称` 非空
2. `tag编码` 非空

动作：

1. 规范化 `tag编码`
2. 建立 canonical tag id
3. 进入根级 tag 集合

### 2. `recoverable_tag`

满足以下条件时，判为 `recoverable_tag`：

1. `tag名称` 非空
2. `tag编码` 为空
3. 且以下任一项非空：
   - `tag定义`
   - `触发模式`
   - `正例`
   - `反例`
   - `必须`
   - `tag anchor binding`
   - `Block role`

动作：

1. 默认保留，不得直接丢弃
2. 进入编码修复流程
3. 进入根级 tag 集合，除非后续被唯一并入某显式标签

### 3. `helper_only`

只有同时满足以下条件时，才允许判为 `helper_only`：

1. `tag名称` 为空，或不足以构成独立标签名
2. 语义列基本为空
3. 当前行只在补充 block 引用说明，不在定义可打标签对象

动作：

1. 不进入根级 tag 集合
2. 只作为 block 级辅助行保留

### 4. `invalid_or_noise`

满足以下条件时，判为 `invalid_or_noise`：

1. `tag名称` 为空
2. 语义列为空
3. 不构成 block 定义，不构成标签定义

动作：

1. 不进入根级 tag 集合
2. 保留原始行号供审计回看

## 空 `tag编码` 行规则

### 总规则

凡是 `tag名称` 非空且落在标签定义区的空 `tag编码` 行，默认先进入 `recoverable_tag`。

### 禁止

1. 不得因为 `tag编码` 为空而直接丢弃
2. 不得因为存在 `Block role` 就直接降为 `helper_only`

## 编码修复流程

### Step 1：尝试继承显式编码

条件：

1. 同一 workbook 中存在语义同源的显式标签

动作：

1. 继承其 canonical id

### Step 2：生成稳定 canonical id

条件：

1. 不存在可继承的显式编码

动作：

1. 基于 tag 身份生成稳定 canonical id
2. 同语义重复行必须复用同一 canonical id
3. 生成规则必须符合 `rules/parsing/id-normalization.md`

### Step 3：冲突挂起

条件：

1. 存在多个同样合理的候选 identity

动作：

1. 记录到 `identity-issues.md`
2. 在允许交互的模式下请求用户决定

## 去重规则

### 1. 根级 tag 去重

1. 根级 `tags[]` 以 canonical id 去重
2. 同一个 canonical id 的重复行合并来源行号

### 2. block 引用去重

1. 同一 block 内对同一 `tag_id + role` 的重复引用只保留一次

### 3. type 级范围

1. 同一 `type` 内重复 tag 应统一身份
2. 不得因为 block 不同就为同一 tag 生成多个根级身份

## `identity-map.json` 最小内容

必须至少包含：

1. namespace
2. category
3. type
4. blocks
5. tags

其中每个 tag 至少包含：

1. `canonical_id`
2. `name`
3. `source_rows`
4. `identity_status`

## `identity-issues.md` 必记内容

必须记录：

1. 空 `tag编码` 行的处理结果
2. 身份冲突
3. 未决问题

## 禁止

1. 不得在本阶段生成 `value_hint`
2. 不得在本阶段生成 `context_hint`
3. 不得在本阶段生成 `anchor_binding`
4. 不得在本阶段生成 block description

## 失败信号

以下情况说明本阶段未完成：

1. 存在空 `tag编码` 行但没有处理记录
2. 存在重复 tag 但没有统一 canonical id
3. 同一 block 中的 tag 引用关系无法回溯
4. 身份冲突被静默吞掉
