# type description 生成规则

## 目标对象

生成 `types[].description`。

## 输入

1. `type_name`
2. `category_name`
3. 当前 type 的 block 名称集合
4. 与相邻 type 的已知边界信息

## Stage 6：Skeleton

输出固定模板：

```text
类型名：{type_name}
所属分类：{category_name}
典型块：{block_names_joined 或 __PTSG_PENDING__}
识别边界：__PTSG_PENDING__
```

## Stage 7：Semantic Draft

1. 输出 1-3 句自然语言。
2. 第一句定义文书类型。
3. 第二句补典型信号。
4. 第三句只在必要时写近邻边界。

## 禁止

1. 不得输出技术生成句。
2. 不得只写“这是一个 X 文书”，没有任何边界。
3. 不得把所有 block 名字原样拼成最终 description。
4. 不得把生成产物或转换流程写成类型定义。

## 失败信号

1. 最终仍是骨架模板句。
2. 完全缺少近邻区分点。
3. 对页分类没有识别价值，只剩泛泛介绍。
