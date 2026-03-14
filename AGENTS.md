# Global AGENTS · 2agathon

## 用户是谁

全栈工程师，AI Vibe Coding 为主要工作方式。
跨语言跨岗位，不被技术栈定义。
一个人扛项目，在信息不完整的情况下做决策是常态。

## Skill 索引

以下 skill 按触发条件加载。读取本地 skill 失败时告知用户，不能静默降级。

本地 skill 根目录：

`{{DOTFILES_ABS_PATH}}/skills`

### 全局基准

| 触发条件                   | Skill                                                   |
| -------------------------- | ------------------------------------------------------- |
| 任何任务开始前（全局常驻） | `{{DOTFILES_ABS_PATH}}/skills/identity/SKILL.md`        |

### 工程执行

| 触发条件                   | Skill                                                              |
| -------------------------- | ------------------------------------------------------------------ |
| 写代码 / 命名 / 设计接口时 | `{{DOTFILES_ABS_PATH}}/skills/principles/SKILL.md`                 |
| 生成任何文件或目录之前     | `{{DOTFILES_ABS_PATH}}/skills/project-structure/SKILL.md`          |
| 开始新功能或新模块之前     | `{{DOTFILES_ABS_PATH}}/skills/vibe-plan/SKILL.md`                  |

### 工程协作

| 触发条件                           | Skill                                                              |
| ---------------------------------- | ------------------------------------------------------------------ |
| 项目没有 AGENTS.md 时              | `{{DOTFILES_ABS_PATH}}/skills/gen-agents/SKILL.md`                 |
| 写任何文档时                       | `{{DOTFILES_ABS_PATH}}/skills/docs/SKILL.md`                       |
| 记录架构 / 流程 / 实现策略的选择时 | `{{DOTFILES_ABS_PATH}}/skills/decision-record/SKILL.md`            |

### 认识捕捉

| 触发条件                           | Skill                                                              |
| ---------------------------------- | ------------------------------------------------------------------ |
| 记笔记 / 整理认识 / 捕捉对话理解时 | `{{DOTFILES_ABS_PATH}}/skills/notes-protocol/SKILL.md`             |
| 操作 Notion 工作区时               | `{{DOTFILES_ABS_PATH}}/skills/notion-manager/SKILL.md`             |

### 认识校准

| 触发条件                                         | Skill                                                              |
| ------------------------------------------------ | ------------------------------------------------------------------ |
| 判断需要被审查 / 结论强于证据 / 词比定义跑得快时 | `{{DOTFILES_ABS_PATH}}/skills/assumption-audit/SKILL.md`           |
| 对话接近承诺时刻 / 感觉差不多了但还没落地时      | `{{DOTFILES_ABS_PATH}}/skills/conversation-to-spec/SKILL.md`       |

## 主动观察职责

以下两种信号出现时，AI 应主动提议对应 skill，不等用户召唤：

- **承诺窗口信号**：对话中出现收敛语（"所以我们接下来…"、"那先这样定…"）、某个词开始稳定承担解释负担但尚未定义、用户从"这意味着什么"转向"我们怎么做" → 提议 `conversation-to-spec`
- **前提漂移信号**：结论强于证据、同一结论被反复使用但成立条件从未展开、对话从理解滑向行动且过渡过于顺滑 → 提议 `assumption-audit`

## 项目规范

每个项目根目录有自己的 AGENTS.md，只写偏离全局规范的部分。
没有项目 AGENTS.md 时，触发 gen-agents skill。

如果项目 AGENTS.md 已经引用项目内本地 skill 副本，则项目内 skill 优先于全局 dotfiles skill。
项目级 skill 作为仓库内 source of truth；全局 dotfiles skill 仅作为 fallback。

## 本地加载规则

本文件中的 skill 路径均为本地文件系统路径，不是网络地址。

- 不再从远程 URL 获取 skill
- 不要将本地路径替换为 raw GitHub 链接
- 不要假设 `~` 一定会被正确展开
- 生成或安装本文件时，应写入已展开的绝对路径

如果某个 skill 文件不存在：

- 明确告知用户缺失的具体路径
- 不得静默跳过
- 不得偷偷改用远程副本
- 只有在不依赖该 skill 仍能安全完成任务时，才可继续