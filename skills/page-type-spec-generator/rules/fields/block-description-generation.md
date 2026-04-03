# block description 生成规则

## 目标对象

生成 `block_types[].description`。

## 输入

1. `Block description`
2. `Block`
3. 当前 block 下的 tag 集合

## Stage 6：Skeleton

输出固定模板：

```text
块对象：{Block 或 __PTSG_PENDING__}
主要内容：{Block description 或 __PTSG_PENDING__}
纳入边界：{关键 tag 家族或 __PTSG_PENDING__}
排除边界：{__PTSG_PENDING__ 或稳定边界}
```

规则：

1. 只暴露块对象、主要内容和边界槽位。
2. 不得在 Skeleton 阶段抢先写成长 prose。
3. 不得机械罗列全部 tag 名称当作最终说明。

## Stage 7：Semantic Draft

1. 输出 2-4 句自然语言短段落。
2. 第一句说明块对象。
3. 第二句说明典型内容范围。
4. 若当前 block 的稳定纳入边界或排除边界会直接影响块语义范围，必须在最终描述中显式写出。
5. 只允许写稳定语义边界；不得写动态流程裁决、跳过条件或冲突优先级。

## 禁止

1. 不得把 `assembly-hint` 的执行规则写进来。
2. 不得写“冲突时以 X 为准”“缺少时跳过”这类流程句。
3. 不得把块说明写成统一句式套话。
4. 不得因为想保持纯 prose，就省掉当前组装侧实际依赖的稳定边界。

## 失败信号

1. Skeleton 阶段缺少边界槽位。
2. Semantic Draft 仍是 tag 名称机械堆砌。
3. 最终描述夹带执行策略，而不是块语义。
4. 多个 block 共享明显统一尾句或统一收束段。
5. 出现与当前块语义主轴明显不匹配的错位表述。
6. 出现 `。。`、重复句尾或大段复用未改写痕迹。
7. 大量 block description 复用同一类统一收束句，导致块间区分度显著下降。
8. 当前 block 明明依赖稳定纳入 / 排除边界才能与近邻 block 区分，但最终 description 没有写出该边界。
