# block description 生成规则

## 目标

生成 `block_types[].description`。

这个字段不只是给人看，也会随 `block_types` 一起进入块组装 prompt，因此必须同时满足：

1. 对人可读
2. 对 LLM 有边界提示价值
3. 不承载流程算法细节

## 输入

1. `Block description`
2. `Block`
3. 当前 block 下的 tag 集合

## 作用

`block_types[].description` 应说明：

1. 这个块在语义上是什么
2. 它通常纳入哪类信息
3. 它和相邻块的关键边界是什么

它不负责说明：

1. 组装顺序
2. 缺项处理
3. 冲突优先级
4. 跨页策略

这些内容属于 `assembly-hint.md`。

## Stage 6：Skeleton

输出固定模板：

```text
块对象：{Block 或 __PTSG_PENDING__}
主要内容：{Block description 或 __PTSG_PENDING__}
纳入边界：{关键 tag 家族或 __PTSG_PENDING__}
排除边界：{若无稳定信息则 __PTSG_PENDING__}
```

### 规则

1. Skeleton 阶段只暴露块对象、主要内容和边界槽位。
2. 不得在 Skeleton 阶段抢先写成长 prose。
3. 不得机械罗列全部 tag 名称当作最终说明。

## Stage 7：Semantic Draft

### 目标形态

1. 2-4 句自然语言短段落。
2. 第一层说明块对象。
3. 第二层说明典型内容范围。
4. 第三层只在必要时补充强边界。

### 写法要求

1. 优先写语义家族，不要把所有 tag 名称全抄一遍。
2. 只有当排除边界真的重要时才写“不要纳入什么”。
3. 尽量让相邻 block 的 description 能一眼看出差异。

## 禁止

1. 不得把 `assembly-hint` 的执行规则写进来。
2. 不得写“冲突时以 X 为准”“缺少时跳过”这类流程句。
3. 不得把块说明写成统一句式的套话。

## 失败信号

1. Skeleton 阶段缺少边界槽位。
2. Semantic Draft 仍是 tag 名称机械堆砌。
3. 最终描述夹带执行策略，而不是块语义。
