---
name: project-structure
description: Use when creating new files or directories, when starting a new module, or when working inside an existing codebase. Ensures directory structure reflects business boundaries, not just technical layers. Apply before generating any file path or package name.
---

## 这个 skill 做什么

在生成任何文件路径或目录之前，先对齐结构和命名约定。
目录结构是业务地图，不是技术分层的刻板复制。

判断标准：陌生人打开项目，30秒内能说出这个项目的业务地图。

## 触发判断

以下情况触发：
- 生成任何新文件之前
- 用户说"新建一个模块"、"加一个服务"、"创建这个功能的目录"
- 发现现有文件放错了层或域

## 信息收集

**我需要什么信息**
- 业务域是什么、文件属于哪一层、文件的职责是什么

**信息从哪里来**
- 你提供 → 你描述要做什么，直接从描述里提取
- 读代码 → 提供现有目录结构，推断业务域划分和层次约定
- 从对话提取 → 已经讨论过业务域和模块划分，从对话里提取

**信息缺口怎么处理**
- 信息已经在对话里 → 直接提取，不重复问
- 业务域不明确 → 必须问，域决定顶层目录
- 层次不明确 → 按标准结构推断（api/domain/infra），用 [ASSUMPTION] 标注
- 在已有项目里 → 先读懂现有结构意图，再决定放哪里
- 完全新项目 → 先生成顶层目录骨架，确认后再生成文件

## 标准结构

项目由多个业务子模块组成，每个模块自包含：
```
src/
├── {domain}/               # 业务域，小写单数
│   ├── api/                # 对外接口层：Controller、DTO、Request、Response
│   ├── domain/             # 领域层：Service、Entity、Validator、规则
│   ├── infra/              # 基础设施层：Mapper、外部SDK适配、Repository实现
│   ├── docs/               # 这个模块的文档，跟着模块走
│   │   ├── decisions/      # 决策记录：YYYY-MM-DD-[标题].md
│   │   ├── api.md          # 接口文档
│   │   └── architecture.md # 架构说明（复杂模块才需要）
│   └── {Domain}Module.java # 模块入口，声明这个域对外暴露什么
└── shared/                 # 跨域共享，谨慎放东西
    ├── exception/
    ├── config/
    └── util/
```

**为什么文档跟着模块走，不集中放在根目录 docs/ 里：**
文档和代码的生命周期一致。模块改了文档跟着改，不会找不到，也不会忘记更新。集中放的文档最终都会和代码脱节。

## 命名规则

目录：业务名词，小写，单数。claim 不是 claims，policy 不是 policies。
文件：业务名词 + 技术角色。ClaimValidator、PolicyRepository、UnderwritingService。
禁止：Manager、Handler、Helper、Processor——这些词没有边界，什么都能塞。

## 生成文件前必须确认

在生成任何文件之前，先问：
1. 这个文件属于哪个业务域？
2. 它在这个域里是哪一层（api / domain / infra / docs）？
3. 它的职责是什么，一句话说清楚？

三个问题答不上来，说明边界还没想清楚，不要生成。

## 已有模块下改

**新增文件：按规范放，不按现有风格放。**
现有文件全在 service/ 里不代表新文件也要放那里。
新文件按域放，加注释说明为什么这样放。

**修改文件：就地改，不顺手重构。**
改一个方法不等于重构整个文件。
没有明确授权，不动修改范围之外的任何代码。

**发现放错的文件：标注，不立刻移动。**
在注释或 OPEN QUESTION 里记录，等合适时机统一处理。
移动文件有成本，不要因为"顺手"就移。

## 注意

- 没有确认业务域就不生成文件路径
- 顺手重构修改范围之外的代码
- 照抄现有错误风格生成新文件
- 用 shared/ 作为"不知道放哪里"的垃圾桶
- 文档集中放根目录——应该跟着模块走