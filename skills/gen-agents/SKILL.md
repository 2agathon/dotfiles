---
name: gen-agents
description: Use when starting a new project, when no AGENTS.md exists in the project root, or when the user asks to generate project-level rules. Guides the generation of a project-specific AGENTS.md based on project context.
---

## 这个 skill 做什么

根据项目特性生成 AGENTS.md 的项目层内容（Layer 2）。
只写这个项目独有的上下文和约定，不重复全局规范（identity + principles）。

## 触发判断

以下情况主动提示用户是否需要生成：
- 项目根目录没有 AGENTS.md
- 用户说"新项目"、"从零开始"、"刚克隆"

## 信息收集

**我需要什么信息**
- 项目名称、业务域、技术栈、项目阶段、我的角色、语言约定、特殊约束

**信息从哪里来**
- 你提供 → 你了解项目，直接填写
- 读文件 → 提供 pom.xml / package.json / README / tree 输出，从文件推断技术栈、业务域、目录结构，推断内容用 [INFERRED] 标注
- 从对话提取 → 你描述了项目背景，从描述里提取关键信息

**信息缺口怎么处理**
- 只缺项目阶段 → 必须问，这个影响生成意图声明还是现状描述
- 其余缺失 → 用 [OPEN QUESTION] 占位，生成骨架，边做边补
- 完全不了解项目 → 直接进模式 B，生成待填充骨架

## 生成前必须确认

在生成之前，先问清楚以下信息。信息不足时只问最影响方向的一个问题，其余用 [ASSUMPTION] 标注：

- 项目名称
- 业务域
- 技术栈（可留空）
- 项目阶段：空项目 / 存量迭代 / 遗留接手 / Vibe Coding 起点
- 我的角色：唯一开发者 / 主导者 / 团队成员 / 外包
- 语言约定：注释、日志、表注释、错误码、commit message 用什么语言
- 特殊约束（可留空）
- 已有 AGENTS.md（可留空，有则补全缺失部分）

## 生成规则

1. 只写项目独有的上下文和约定，不重复全局规范
2. 每个约定说明 why，不只是 what
3. 无法确定的内容用 [OPEN QUESTION: 具体问题] 标注
4. 推断的内容用 [ASSUMPTION: 推断内容] 标注
5. 输出纯 Markdown，直接可用

## 三种模式

**模式 A：我了解项目**
正常填写所有字段，生成完整的项目层规范。

**模式 B：我不了解项目 / 没时间描述**
只填项目名和阶段，生成带 [OPEN QUESTION] 的骨架，边做边补。

**模式 C：有文件让我读**
用户提供 pom.xml / package.json / README / tree 输出，
从文件推断技术栈和业务域，推断内容用 [INFERRED] 标注。

## 输出放哪里

生成完成后提示用户：
> 复制到项目根目录的 AGENTS.md。
> [OPEN QUESTION] 和 [INFERRED] 是待确认项，边做项目边填。