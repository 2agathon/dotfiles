# 状态与占位策略

## 总规则

1. 所有进入最终结果的必填 ID 字段都不得为空字符串。
2. 必填对象不能留空时，必须在“稳定占位符”与“阻断”之间二选一。
3. `blocked` 状态不得进入 `skeleton/` 之后的阶段。
4. 占位不是静默容错，必须可识别、可复用、可记录。
5. 具名对象不得因编码缺失而直接降为 `helper_only`。
6. review-ready 结果允许显式占位。除字段规则明确允许的空字符串外，不允许空字符串。
7. 当“继续推进流程”和“恢复依据是否足够稳固”冲突时，必须优先选择更保守状态。

## 统一占位值

1. 字符串占位符：`__PTSG_PENDING__`
2. Markdown 占位符：`__PTSG_PENDING__`

## 占位 ID 规则

1. `CATEGORY_PLACEHOLDER_*`
2. `TYPE_PLACEHOLDER_*`
3. `BLOCK_PLACEHOLDER_*`
4. `TAG_PLACEHOLDER_*`

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

1. 对象有显式原始 ID
2. 规范化后得到稳定 canonical id

### `resolved_recovered`

1. 原始 ID 缺失或不可直接使用
2. 但可通过显式同源对象继承，或通过规则内明示的唯一显式恢复源得到 canonical id
3. 不得仅凭显示名、中文名或 codepoint 串现造正式 id
4. 若恢复依据带争议但仍被采用，必须在报告中列为高风险自动决策

### `resolved_placeholder`

1. 对象必须存在
2. 当前输入不足以形成正常 canonical id
3. 因此生成稳定占位符 id
4. 具名空编码 tag 且不存在显式恢复源时，默认优先进入本状态

### `helper_only`

1. 行只承担 block 内辅助作用
2. 不进入根级对象集合
3. 不得用于承接具名且带语义载荷的对象

### `invalid_or_noise`

1. 不构成可消费对象
2. 仅保留回溯信息

### `blocked`

1. 存在关键歧义或缺失
2. 当前规则无法安全继续

## 槽位状态

只允许以下槽位状态：

1. `transferred`
2. `templated`
3. `pending_semantic`
4. `pending_human`
5. `missing_required_source`
6. `optional_visible_empty`
7. `deferred_template`
8. `materialized`
9. `blocked`

## 槽位状态含义

### `transferred`

1. 可机械确定的结构化值已直接转移

### `templated`

1. 骨架阶段已按固定模板展开
2. 仍未进入语义润色

### `pending_semantic`

1. 槽位必须存在
2. 当前已显式落槽
3. 等待 Stage 7 语义化

### `pending_human`

1. 槽位必须存在
2. AI 当前不能安全完成
3. 需人工复核或补写

### `missing_required_source`

1. schema 或业务要求该槽位存在
2. 当前 Excel 无可用来源
3. 只能显式占位并进入待补清单

### `optional_visible_empty`

1. 槽位语义上可为空
2. 为了 review-ready 可见性仍显式保留

### `deferred_template`

1. 当前输出文件必须存在
2. 但设计稿无足够素材
3. 因此输出空模板或 TODO 模板

### `materialized`

1. 已生成实质内容

### `blocked`

1. 当前内容缺失关键条件
2. 不得继续进入最终结果

## 具名空编码行策略

### 默认规则

满足以下条件的行，视为具名空编码行：

1. `tag名称` 非空
2. 位于标签定义区
3. `tag编码` 为空

具名空编码行必须按以下顺序处理：

1. 若存在显式恢复源，进入 `resolved_recovered`
2. 若不存在显式恢复源但对象按流程必须存在，进入 `resolved_placeholder`
3. 若存在真实多候选歧义或结构冲突，则进入 `blocked`

说明：

1. `record_time_source` 这类 role 默认只算辅助信号，不单独构成显式恢复源。
2. 只有当本 skill 在规则中明示列出某个 role-based recovery 白名单时，role 才能成为恢复依据。

### placeholder 收束规则

1. 在同一 selected type 内，若多个具名空编码 tag 具有相同显示名、相同角色、相同结构功能，默认优先复用同一个 placeholder id。
2. 只有当存在稳定证据证明这些空编码 tag 语义上彼此不同，才允许生成 `DUP` 变体。
3. 若生成 `DUP` 变体，必须记录 `placeholder_distinction_reason`。

### 禁止规则

具名空编码行不得：

1. 直接丢弃
2. 直接输出空字符串 ID
3. 仅因存在 `role` 就降为 `helper_only`
4. 把中文显示名直接转成 `TAG_U...` 一类非占位 recovered id
5. 仅因存在 `record_time_source` 等 role 就直接进入 `resolved_recovered`
6. 在无显式区分理由时，为同一显示名和同一角色无限制生成多个 placeholder `DUP` 变体

## 复合结构占位规则

1. 对于 `action_paths[]` 这类复合可选结构，若关键子字段不稳定，优先输出空数组 `[]`，而不是把子字段全部保留为 `__PTSG_PENDING__`。
2. 只有当业务要求“该对象必须显式存在”时，才允许保留占位结构。

## 最终结果准入规则

### 允许进入最终结果

1. `resolved_explicit`
2. `resolved_recovered`
3. `resolved_placeholder`
4. `transferred`
5. `templated`
6. `pending_semantic`
7. `pending_human`
8. `missing_required_source`
9. `optional_visible_empty`
10. `deferred_template`
11. `materialized`

说明：

1. `resolved_placeholder` 允许进入最终结果，但必须在报告中显式列出。
2. `pending_semantic` 与 `pending_human` 允许进入 review-ready 结果，但必须出现在待补清单中。

### 禁止进入最终结果

1. 空字符串 ID
2. `blocked`
3. `helper_only`
4. `invalid_or_noise`

## `helper_only` 准入条件

只有同时满足以下条件时，才允许使用 `helper_only`：

1. 当前对象不应进入根级集合
2. 当前行不构成独立可消费标签
3. 当前问题不是编码缺失，而是对象职责本身仅为辅助

只要任一条件不满足，不得使用 `helper_only`。

## 占位符规则

### 1. 何时生成占位符

满足以下条件时，必须生成稳定占位符，而不是返回空字符串：

1. 当前对象或槽位按流程必须存在
2. 原始输入不足以形成正常值
3. 当前问题不是“多候选歧义”，而是“缺稳定来源信号”

### 2. 何时不得生成占位符

满足以下任一条件时，不得用占位符掩盖问题：

1. 多个候选身份同样合理
2. 当前对象本身就不应进入根级集合
3. 当前问题属于结构冲突，而非命名或来源缺失

### 3. 占位符必须记录

生成占位符时，必须记录：

1. 占位符值
2. 占位原因
3. 来源行号
4. 槽位状态

## hint 文件规则

1. 若文件必须输出但无素材，使用 `deferred_template`
2. 若字段是可选字段但需在 review-ready 结果中显式可见，使用 `optional_visible_empty` 或 `pending_human`
3. 不得把“无素材”误当成 `blocked`

## 失败信号

以下情况说明状态策略未被执行：

1. 空字符串 ID 进入最终结果
2. `blocked` 对象进入 `skeleton/` 之后阶段
3. 应输出模板的文件被静默省略
4. 应显式可见的可选字段被物理省略，或本应保持无字段的对象被错误补成显式字段
5. 具名空编码行被直接降为 `helper_only`
6. 空编码 tag 被解析成 `TAG_U...` 一类非占位 canonical id
