# 表头规范化规则

## 目标

把 xlsx 原始表头映射为后续阶段可稳定使用的规范字段名。

本阶段只负责表头层面的规范化，不负责内容语义生成。

## 输入

1. `workbook.raw.json`
2. `run-manifest.json`

## 输出

1. `workbook.normalized.json` 中的 `header_mapping`
2. `normalization-report.md` 中的表头修复摘要

## 总规则

1. 必须保留原始表头名。
2. 必须保留规范化后的表头名。
3. 必须记录每一项修复。
4. 不得在本阶段根据字段内容倒推新表头。

## 规范字段名集合

当前允许的规范字段名：

1. `namespace`
2. `category_id`
3. `category_name`
4. `category_description`
5. `type_id`
6. `type_name`
7. `Block`
8. `Block id`
9. `Block description`
10. `tag名称`
11. `Block role`
12. `tag编码`
13. `tag定义`
14. `tag anchor binding`
15. `触发模式`
16. `正例`
17. `反例`
18. `必须`
19. `块摘要构造和输出组装`
20. `采集和转化规范`
21. `缺项处理`
22. `冲突处理`
23. `情景`
24. `情景id`
25. `阶段`
26. `阶段id`
27. `动作`
28. `动作id`

其中：

1. `必须` 允许保留为历史字段。
2. `必须` 只用于解析层保留与识别，不得新增到后续生成输入。

如果新增字段进入工作流，应先扩充本集合，再继续使用。

## 表头映射规则

### 1. 精确命中

如果原始表头与规范字段名完全一致，直接映射。

### 2. 已知别名修复

以下别名允许自动修复：

1. `namespce` -> `namespace`
2. `Bolck role` -> `Block role`

### 3. 去空白修复

允许：

1. 去掉首尾空白
2. 统一连续空白

### 4. 轻微标点差异修复

仅允许修复不会改变字段身份的差异。

### 5. 未命中字段

如果原始表头无法映射到规范字段名：

1. 必须保留原始表头
2. 必须记录为未识别表头
3. 不得静默吞掉

## `header_mapping` 最小结构

```json
{
  "header_mapping": {
    "namespce": "namespace",
    "Bolck role": "Block role"
  }
}
```

## 修复记录要求

每次自动修复表头时，必须记录：

1. 原始表头
2. 规范表头
3. 修复类型

推荐修复类型：

1. `exact_match`
2. `known_alias`
3. `trim_whitespace`
4. `normalize_spacing`
5. `normalize_punctuation`
6. `unrecognized_header`

## 禁止

1. 不得在本阶段因为某列内容像某字段，就直接改表头
2. 不得在未记录修复痕迹时静默修表头
3. 不得把多个原始表头合并成一个规范字段而不记录

## 失败信号

以下情况说明本阶段未完成：

1. 规范化后的行数据无法回溯原始表头
2. 表头被自动改写但没有修复记录
3. 未识别表头被静默丢弃
4. 同一个原始表头在同一次运行中被映射成多个规范字段
