# ID 规范化规则

## 目标

把原始输入中的 `category_id`、`type_id`、`Block id`、`tag编码` 规范化为稳定 ID。

## 输入

1. `category_id`
2. `type_id`
3. `Block id`
4. `tag编码`
5. `tag名称`

## 输出

1. 稳定 canonical id

## 总规则

1. 同一语义对象必须生成同一 canonical id。
2. 不得在不同阶段为同一对象生成不同 id。
3. 前缀规范必须稳定。
4. 无编码对象若需要生成 id，生成规则必须可复用。

## 前缀规则

1. category 使用 `CATEGORY_`
2. type 使用 `TYPE_`
3. block 使用 `BLOCK_`
4. tag 使用 `TAG_`

## 规范化步骤

### Step 1：保留已有前缀

若原始值已带合法前缀，则保留此前缀并统一为大写。

### Step 2：字母数字下划线规范化

若原始值未带前缀：

1. 把非字母数字字符转换为下划线
2. 去掉首尾多余下划线
3. 转为大写
4. 补上对应前缀

### Step 3：dot notation 规则

若原始值为 dot notation：

1. 保留完整路径层级
2. `.` 转换为 `_`
3. 整体转大写
4. 补上对应前缀

示例：

1. `admission.complaint.symptom` -> `TAG_ADMISSION_COMPLAINT_SYMPTOM`

## 无编码 tag 的规则

### 1. 优先继承显式编码

若同一 workbook 中存在语义同源的显式 tag 编码，优先复用其 canonical id。

### 2. 无法继承时生成稳定 id

若无显式编码可继承：

1. 以 `tag名称` 为核心生成 canonical id
2. 若需要消歧，可附加最小必要语义词
3. 同语义重复行必须复用同一 id

### 3. 命名要求

1. 优先使用可读语义词
2. 不得用行号作为最终 canonical id 的组成部分
3. 不得为同一语义对象生成多个近义 id

## 冲突处理

### 1. 同一规范化结果对应多个不同对象

动作：

1. 记录冲突
2. 在允许交互时请求用户决定
3. 未决前不得静默追加随机后缀作为正式解法

### 2. 同一对象出现多个候选原始 id

动作：

1. 优先保留显式编码来源
2. 其余候选并入同一 canonical id

## 质量检查

必须检查：

1. category/type/block/tag 是否使用正确前缀
2. dot notation 是否完整保留层级
3. 同一对象是否生成同一 canonical id
4. 无编码 tag 是否按稳定规则生成 id

## 失败信号

以下情况说明规范化失败：

1. 同一对象生成多个 canonical id
2. 同一 canonical id 对应多个明显不同对象
3. 用行号或临时序号作为最终稳定 id
4. 漏掉应保留的 dot notation 层级
