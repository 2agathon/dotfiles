# 产物协议

## 总规则

1. 每个阶段都必须产生对应产物。
2. 同名产物必须覆盖本次运行结果，不得混入上次运行内容。
3. 所有产物都必须可被后续阶段直接读取。
4. 产物中必须保留回溯信息，不得只保留最终结论。

## `run-manifest.json`

### 必含内容

1. `run_id`
2. 运行模式
3. 输入文件列表
4. 是否提供 `page-types.data.json`
5. 是否提供 `page-types.tree.json`
6. 当前选中的 `type`

### 用途

1. 后续阶段读取运行模式
2. 后续阶段读取本次处理范围

## `workbook.raw.json`

### 必含内容

1. sheet 列表
2. 原始行号
3. 原始列号或列名
4. 原始单元格值

### 用途

1. 为 `workbook.normalized.json` 提供原始来源
2. 供后续审计回看原始输入

## `workbook.normalized.json`

### 必含内容

1. 规范化后的表头
2. 每行的规范化字段值
3. 行号
4. 表头修复记录
5. 继承填充记录
6. 行级初步分类结果

### 用途

1. 为 `identity-map.json` 提供稳定输入
2. 供 `normalization-report.md` 生成摘要

## `normalization-report.md`

### 必含内容

1. 表头修复摘要
2. 继承填充摘要
3. 文本清洗摘要
4. 行分类摘要

### 用途

1. 向用户说明规范化阶段做了哪些自动修复

## `identity-map.json`

### 必含内容

1. namespace
2. category 身份
3. type 身份
4. block 身份
5. tag 身份
6. block 与 tag 的引用关系
7. 空 `tag编码` 行的分类结果
8. 每个身份对象的终态

### 用途

1. 为骨架生成提供唯一身份来源
2. 为身份问题报告提供依据

## `identity-issues.md`

### 必含内容

1. 空 `tag编码` 行处理记录
2. 身份冲突记录
3. 未决身份问题
4. 占位符生成记录

### 用途

1. 向用户暴露身份层的高风险点

## `skeleton/`

### 必含内容

1. `page-types.data.json`
2. `page-types.tree.json`
3. `page-semantic-spec.json`
4. 五个或六个空 hint 模板

### 用途

1. 为 semantic draft 提供结构闭合底座

### 约束

1. `skeleton/` 中的内容只承担结构闭合职责
2. 高自由度语义内容不得在此层定稿

## `semantic-draft/`

### 必含内容

1. `page-types.data.json`
2. `page-types.tree.json`
3. `page-semantic-spec.json`
4. 各 hint 文件

### 用途

1. 作为最终交付前的完整草稿结果
2. 为校验和审计提供输入

### 约束

1. `semantic-draft/` 是最终内容的直接上游
2. 若后续要输出正式结果，应从本层派生，而不是跳过本层重生一份

## `validation-report.json`

### 必含内容

1. 结构校验结果
2. 引用闭合结果
3. 中间结果完整性检查结果
4. `blocking` 列表
5. `warning` 列表
6. `pass` 列表

### 用途

1. 为 `audit-report.md` 提供结构化检查结果
2. 为最终收口提供阻塞信息

## `audit-report.md`

### 必含内容

1. 输入摘要
2. 自动修复摘要
3. 身份问题摘要
4. 结构校验摘要
5. 未决问题摘要
6. 占位符摘要

### 用途

1. 向用户说明本次转换有哪些风险与默认决策

## 最终交付目录

### 必含内容

1. `{namespace}/page-types.data.json`
2. `{namespace}/page-types.tree.json`
3. `{namespace}/types/{TYPE_ID}/page-semantic-spec.json`
4. `{namespace}/types/{TYPE_ID}/*.md`

### 用途

1. 作为最终交付结果目录

### 约束

1. 最终交付目录必须从 `semantic-draft/` 派生
2. 不得绕过 `semantic-draft/` 直接另写一份最终结果
3. 不得包含空字符串 ID
4. 不得包含 `blocked` 对象

## `final-report.md`

### 必含内容

1. 处理了哪些 `type`
2. 生成了哪些文件
3. 做了哪些自动决策
4. 剩余风险有哪些
5. 是否存在占位符对象

### 用途

1. 作为最终对用户的收口说明
