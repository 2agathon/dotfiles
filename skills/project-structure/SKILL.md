---
name: project-structure
description: Use when creating new files or directories, when starting a new module, or when working inside an existing codebase. Ensures directory structure reflects business boundaries, not just technical layers. Apply before generating any file path or package name.
---

## 核心原则

目录结构是业务地图，不是技术分层的刻板复制。
判断标准：陌生人打开项目，30秒内能说出这个项目的业务地图。

## 标准结构

外层按业务域，内层按技术层：
```
src/
├── {domain}/               # 业务域，小写单数
│   ├── api/                # 对外接口层：Controller、DTO、Request、Response
│   ├── domain/             # 领域层：Service、Entity、Validator、规则
│   ├── infra/              # 基础设施层：Mapper、外部SDK适配、Repository实现
│   └── {Domain}Module.java # 模块入口，声明这个域对外暴露什么
└── shared/                 # 跨域共享，谨慎放东西
    ├── exception/
    ├── config/
    └── util/
```

## 命名规则

目录：业务名词，小写，单数。claim 不是 claims，policy 不是 policies。
文件：业务名词 + 技术角色。ClaimValidator、PolicyRepository、UnderwritingService。
禁止：Manager、Handler、Helper、Processor——这些词没有边界，什么都能塞。

## 生成文件前必须确认

在生成任何文件之前，先问：
1. 这个文件属于哪个业务域？
2. 它在这个域里是哪一层（api / domain / infra）？
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

## 禁止行为

- 没有确认业务域就生成文件路径
- 顺手重构修改范围之外的代码
- 照抄现有错误风格生成新文件
- 用 shared/ 作为"不知道放哪里"的垃圾桶