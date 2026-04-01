# 状态与占位策略

## 总规则

1. 所有进入最终结果的必填 ID 字段都不得为空字符串。
2. 必填对象不能留空时，必须在“稳定占位符”与“阻断”之间二选一。
3. `blocked` 状态不得进入 `skeleton/` 之后的阶段。
4. 占位不是静默容错，必须可识别、可复用、可记录。

## 身份状态

只允许以下身份状态：

1. `resolved_explicit`
2. `resolved_recovered`
3. `resolved_placeholder`
4. `helper_only`
5. `invalid_or_noise`
6. `blocked`

## 身份状态含义

### `resolved_explicit`

含义：

1. 对象有显式原始 ID
2. 规范化后得到稳定 canonical id

### `resolved_recovered`

含义：

1. 原始 ID 缺失或不可直接使用
2. 但可通过显式同源对象继承，或通过稳定语义生成 canonical id

### `resolved_placeholder`

含义：

1. 对象必须存在
2. 但当前输入不足以形成正常 canonical id
3. 因此生成稳定占位符 id

### `helper_only`

含义：

1. 行只承担 block 内辅助作用
2. 不进入根级对象集合

### `invalid_or_noise`

含义：

1. 不构成可消费对象
2. 仅保留回溯信息

### `blocked`

含义：

1. 存在关键歧义或缺失
2. 当前规则无法安全继续

## 内容状态

只允许以下内容状态：

1. `materialized`
2. `deferred_template`
3. `omitted`
4. `blocked`

## 内容状态含义

### `materialized`

含义：

1. 已生成实质内容

### `deferred_template`

含义：

1. 当前输出文件必须存在
2. 但设计稿无足够素材
3. 因此输出空模板或 TODO 模板

### `omitted`

含义：

1. 当前字段是可选字段
2. 当前无素材或无歧义
3. 因此直接省略

### `blocked`

含义：

1. 当前内容缺失关键条件
2. 不得继续进入最终结果

## 最终结果准入规则

### 允许进入最终结果

1. `resolved_explicit`
2. `resolved_recovered`
3. `resolved_placeholder`
4. `materialized`
5. `deferred_template`
6. `omitted`（仅对可选字段）

### 禁止进入最终结果

1. 空字符串 ID
2. `blocked`
3. `helper_only`
4. `invalid_or_noise`

## 占位符规则

### 1. 何时生成占位符

满足以下条件时，必须生成稳定占位符，而不是返回空字符串：

1. 当前对象按流程必须存在
2. 原始输入不足以形成正常 canonical id
3. 当前问题不是“多候选歧义”，而是“缺稳定命名信号”

### 2. 何时不得生成占位符

满足以下任一条件时，不得用占位符掩盖问题：

1. 多个候选身份同样合理
2. 当前对象本身就不应进入根级集合
3. 当前问题属于结构冲突，而非命名缺失

### 3. 占位符必须记录

生成占位符时，必须记录：

1. 占位符 id
2. 占位原因
3. 来源行号

## hint 文件规则

1. 若文件必须输出但无素材，使用 `deferred_template`
2. 若字段是可选字段且无素材，使用 `omitted`
3. 不得把“无素材”误当成 `blocked`

## 失败信号

以下情况说明状态策略未被执行：

1. 空字符串 ID 进入最终结果
2. `blocked` 对象进入 `skeleton/` 之后阶段
3. 应输出模板的文件被静默省略
4. 应省略的可选字段被错误占位
