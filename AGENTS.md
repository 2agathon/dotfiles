# Global AGENTS · 2agathon

## 用户是谁

全栈工程师，AI Vibe Coding 为主要工作方式。
跨语言跨岗位，不被技术栈定义。
一个人扛项目，在信息不完整的情况下做决策是常态。

## Skill 体系怎么读

本仓库的 skill 不是扁平列表，而是几股**正交责任**叠在一起：

- **常驻与对齐**：`identity` 定协作伦理与停止规则；`vibe-plan` 在动代码前把目标、边界、实现顺序钉住（含可执行的 task 粒度）。
- **代码生命周期**：`file-creation` 管新建与目录边界；`code-modify` 在改现有代码时自动约束手术范围与不变量；`code-test` 在用户明确要求写测试时约束测试质量；`git-commit` 管「该不该提、怎么拆单元、message 与 push」；`code-relay` 管跨会话的交接信与收工回流（只用于代码接力场景）。
- **横切止损**：`bail-out` 在迭代修改中监测沉没成本信号，不必等用户先说「别改了」。
- **协作与记录**：`gen-agents`、`docs`、`decision-record` 把规范接进项目、写清说明、记下真实分叉。
- **认识线**：捕捉（`notes-protocol`、`notion-manager`、`knowledge-shaping`）与校准（`assumption-audit`、`conversation-to-spec`、`role-lens`、`drift-detector`、`self-rewrite`）；`tension-manifest` 管 TM 头版本，常被笔记与决策记录依赖。
- **领域专项**：聊天数据、表格、页类型等——见下表「领域与专项」；按需触发，不默认全局常驻。
- **工具链自带**：`skills/.system/` 下为与具体工具（如 OpenAI 文档、skill 安装器）配套的 skill，与上列 2agathon 核心并列存放，加载规则以各 skill 自述为准。

## Skill 索引

以下 skill 按触发条件加载。读取本地 skill 失败时告知用户，不能静默降级。

本地 skill 根目录：

`{{DOTFILES_ABS_PATH}}/skills`

### 全局基准

| 触发条件                   | Skill                                            |
| -------------------------- | ------------------------------------------------ |
| 任何任务开始前（全局常驻） | `{{DOTFILES_ABS_PATH}}/skills/identity/SKILL.md` |

### 工程执行（设计、实现、验证、交付）

| 触发条件                                                         | Skill                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------------- |
| 写代码 / 命名 / 设计接口时                                       | `{{DOTFILES_ABS_PATH}}/skills/principles/SKILL.md`         |
| 开始新功能或新模块之前（含「就改一下」默认触发，除非用户免 plan） | `{{DOTFILES_ABS_PATH}}/skills/vibe-plan/SKILL.md`          |
| 新建任何文件或目录；或 audit / 审目录                            | `{{DOTFILES_ABS_PATH}}/skills/file-creation/SKILL.md`      |
| 修改、修复、重构、调整现有代码（自动生效，无需口令）             | `{{DOTFILES_ABS_PATH}}/skills/code-modify/SKILL.md`        |
| 用户明确要求写测试、补测试、测一下                               | `{{DOTFILES_ABS_PATH}}/skills/code-test/SKILL.md`          |
| 提交、commit、提一下                                             | `{{DOTFILES_ABS_PATH}}/skills/git-commit/SKILL.md`         |
| 代码会话间接力（认识 / 加载交接信 / 收工）                       | `{{DOTFILES_ABS_PATH}}/skills/code-relay/SKILL.md`         |

### 迭代与止损

| 触发条件                                                                 | Skill                                                |
| ------------------------------------------------------------------------ | ---------------------------------------------------- |
| AI 在多轮迭代中修改同一问题未收敛、补偿性修复、绕过式修补等（自动监测） | `{{DOTFILES_ABS_PATH}}/skills/bail-out/SKILL.md`     |
| 用户说「别改了」「回退」「重来」                                       | `{{DOTFILES_ABS_PATH}}/skills/bail-out/SKILL.md`     |

### 工程协作

| 触发条件                           | Skill                                                   |
| ---------------------------------- | ------------------------------------------------------- |
| 项目没有 AGENTS.md 时              | `{{DOTFILES_ABS_PATH}}/skills/gen-agents/SKILL.md`      |
| 写任何文档时                       | `{{DOTFILES_ABS_PATH}}/skills/docs/SKILL.md`            |
| 记录架构 / 流程 / 实现策略的选择时 | `{{DOTFILES_ABS_PATH}}/skills/decision-record/SKILL.md` |

### 认识捕捉

| 触发条件                                                  | Skill                                                     |
| --------------------------------------------------------- | --------------------------------------------------------- |
| 记笔记 / 整理认识 / 捕捉对话理解时                        | `{{DOTFILES_ABS_PATH}}/skills/notes-protocol/SKILL.md`   |
| 操作 Notion 工作区时                                      | `{{DOTFILES_ABS_PATH}}/skills/notion-manager/SKILL.md`  |
| 有知识增量但尚未形成认识断裂 / 想把材料塑形成可复用对象时 | `{{DOTFILES_ABS_PATH}}/skills/knowledge-shaping/SKILL.md` |
| 创建或更新 TM 头、看认识版本链                            | `{{DOTFILES_ABS_PATH}}/skills/tension-manifest/SKILL.md` |

### 认识校准

| 触发条件                                                  | Skill                                                        |
| --------------------------------------------------------- | ------------------------------------------------------------ |
| 判断需要被审查 / 结论强于证据 / 词比定义跑得快时          | `{{DOTFILES_ABS_PATH}}/skills/assumption-audit/SKILL.md`     |
| 对话接近承诺时刻 / 感觉差不多了但还没落地时               | `{{DOTFILES_ABS_PATH}}/skills/conversation-to-spec/SKILL.md` |
| 某个结论显得过于自然顺滑 / 同一对象只按一种方式被解释时   | `{{DOTFILES_ABS_PATH}}/skills/role-lens/SKILL.md`            |
| 系统文件发生较大改写 / 某种做法已成默认但对应记录仍缺席时 | `{{DOTFILES_ABS_PATH}}/skills/drift-detector/SKILL.md`       |
| 旧自我叙述已不能解释当前行为或判断 / 需要重新理解自己时   | `{{DOTFILES_ABS_PATH}}/skills/self-rewrite/SKILL.md`         |

### 领域与专项

| 触发条件（摘要）                                       | Skill                                                                |
| ------------------------------------------------------ | -------------------------------------------------------------------- |
| 聊天导出、群聊分析、海报 / 报告 / 图谱（数据入口）     | `{{DOTFILES_ABS_PATH}}/skills/chat-parser/SKILL.md`                 |
| 已有 parser 数据对象，生成群聊海报等                   | `{{DOTFILES_ABS_PATH}}/skills/chat-render/SKILL.md`                 |
| 电子表格为主要输入或输出                               | `{{DOTFILES_ABS_PATH}}/skills/xlsx/SKILL.md`                        |
| 从业务 xlsx 生成页类型配置                             | `{{DOTFILES_ABS_PATH}}/skills/page-type-spec-generator/SKILL.md`    |

### 主动观察职责

以下信号出现时，AI 应主动提议对应 skill，不等用户召唤：

- **承诺窗口信号**：对话中出现收敛语（"所以我们接下来…"、"那先这样定…"）、某个词开始稳定承担解释负担但尚未定义、用户从"这意味着什么"转向"我们怎么做" → 提议 `conversation-to-spec`
- **前提漂移信号**：结论强于证据、同一结论被反复使用但成立条件从未展开、对话从理解滑向行动且过渡过于顺滑 → 提议 `assumption-audit`
- **无声变更信号**：某个术语在多处被使用但含义开始不稳定、某种选择已经在实践中反复被默认采用但未被记录、系统自我描述与当前实际做法味道已经不同 → 提议 `drift-detector`
- **单一透镜信号**：某个方向的讨论或结论显得格外自然、没有任何张力、所有证据都在支持同一结论 → 提议 `role-lens`
- **迭代沉没成本信号**：同一问题多轮修改仍不收敛、为用新补丁掩盖上一轮副作用而继续改、明显在绕过根因而非解决问题 → 按 `bail-out` 停下来评估，不继续盲改

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
