# ID 规范化规则

## 目标

把输入中的 category/type/block/tag 标识规范化为稳定 canonical id。

## 输入

1. 原始 ID 值
2. 对象名称
3. 对象角色
4. 对象前缀类型
5. `rules/pipeline/state-and-placeholder-policy.md`

## 输出

1. 非空 canonical id

## 总规则

1. canonical id 不得为空字符串。
2. 同一对象必须得到同一 canonical id。
3. 不得在不同阶段重新命名同一对象。

## 前缀规则

1. category -> `CATEGORY_`
2. type -> `TYPE_`
3. block -> `BLOCK_`
4. tag -> `TAG_`

## 正常规范化

### Step 1：保留已有合法前缀

若原始值已带合法前缀，则：

1. 统一转为大写
2. 作为 canonical id 返回

### Step 2：字符规范化

若原始值未带前缀，则：

1. dot notation 中的 `.` 转换为 `_`
2. 非字母数字字符转换为 `_`
3. 合并连续 `_`
4. 去掉首尾 `_`
5. 整体转大写
6. 补上对应前缀

## 占位符规范化

若正常规范化后无可用 token，则进入占位符生成。

### 占位符生成顺序

按以下优先级尝试生成 token：

1. 规范化后的原始 ID
2. 规范化后的对象名称
3. 规范化后的对象角色
4. `UNNAMED`

### 占位符格式

格式：

1. `CATEGORY_PLACEHOLDER_<TOKEN>`
2. `TYPE_PLACEHOLDER_<TOKEN>`
3. `BLOCK_PLACEHOLDER_<TOKEN>`
4. `TAG_PLACEHOLDER_<TOKEN>`

### 占位符冲突处理

若同一前缀下占位符冲突：

1. 追加 `_DUP2`、`_DUP3` 等稳定后缀
2. 不得使用行号作为最终 id 的唯一主体

## 冲突处理

### 1. 同一 canonical id 对应多个明显不同对象

动作：

1. 标记为 `blocked`
2. 进入问题记录

### 2. 同一对象出现多个候选原始 ID

动作：

1. 优先保留显式 ID 来源
2. 其他候选并入同一 canonical id

## 质量检查

必须检查：

1. canonical id 是否非空
2. 前缀是否正确
3. dot notation 层级是否保留
4. 占位符是否带 `PLACEHOLDER_`
5. 同一对象是否得到同一 canonical id

## 失败信号

以下情况说明规范化失败：

1. 返回空字符串
2. 同一对象得到多个 canonical id
3. 多个明显不同对象得到同一 canonical id
4. 占位符未显式标记为 `PLACEHOLDER_`
