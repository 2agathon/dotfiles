# block answerable question 生成规则

## 目标对象

生成 `block_types[].answerable_question`。

## 输入

1. `Block answerable question`

## Stage 6：Skeleton

1. 若原列为空，不生成 `answerable_question` 字段。
2. 若原列非空，机械转移原文到 `answerable_question` 字段。
3. 不得润色、扩写、摘要、改写或重组原句。

## Stage 7：Semantic Draft

1. 若 Stage 6 未生成该字段，本阶段保持无字段。
2. 若 Stage 6 已生成该字段，直接沿用。
3. 不得把该字段当成 prose 优化对象。

## 禁止

1. 不得根据 `Block description`、tag 集合、hint 文件或其他字段推导 `answerable_question`。
2. 不得把一个问题拆成多个句子重写后再写回。
3. 不得把原句压缩成更短摘要，也不得扩展成说明文。
4. 不得在 Stage 7 / Stage 8 / Stage 9 修改该字段正文。

## 失败信号

1. 原列非空，但结果中没有 `answerable_question` 字段。
2. 原列为空，但结果中凭推断生成了 `answerable_question`。
3. 结果中的 `answerable_question` 不是原列机械转移值，而是改写版。
