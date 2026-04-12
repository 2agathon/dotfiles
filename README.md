# dotfiles · 2agathon

我的 AI Vibe Coding 工程规范体系。
换工具不换规范，换项目不换工作方式。

## 体系结构

规范按责任拆开，而不是按「文档类型」堆砌：

- **对齐与设计**：`identity`（常驻）、`vibe-plan`（写代码前的技术对齐与 task 粒度）。
- **代码生命周期**：`file-creation` → `code-modify` → `code-test`（按需）→ `git-commit`；跨会话用 `code-relay`。
- **迭代止损**：`bail-out` 在多轮修改中自动监测是否陷入沉没成本。
- **项目与记录**：`gen-agents`、`docs`、`decision-record`。
- **认识**：捕捉（`notes-protocol`、`notion-manager`、`knowledge-shaping`）与校准（`assumption-audit`、`conversation-to-spec`、`role-lens`、`drift-detector`、`self-rewrite`）；`tension-manifest` 负责 TM 头与版本链。
- **专项**：聊天管线（`chat-parser` / `chat-render`）、表格（`xlsx`）、页类型（`page-type-spec-generator`）。

`skills/.system/` 存放与外部工具文档或安装器相关的 skill，同仓维护但不参与安装。

## 关键文件

| 文件 | 用途 |
| ---- | ---- |
| [`AGENTS.md`](AGENTS.md) | AI 行为指令：协作基准、始终生效的约束、skill 调度表 |
| [`SKILLS-REFERENCE.md`](SKILLS-REFERENCE.md) | 给人看的 skill 速查：触发词、决策点、控制方式 |
| [`EVOLUTION.md`](EVOLUTION.md) | 规范演进记录：什么时候更新、更新什么、出问题改哪里 |
| [`targets.json`](targets.json) | 安装目标配置：工具名称、路径、文件名 |

## 安装

需要 Python 3.8+。首次运行会自动安装 `rich` 库。

```bash
git clone <repo> ~/dotfiles
python ~/dotfiles/install.py
```

交互模式引导选择操作和目标。也支持命令行参数：

```bash
python install.py --dry-run                    # 预演
python install.py --uninstall                  # 卸载
python install.py --force                      # 覆盖非受管内容（先备份）
python install.py --target "Claude Code"       # 只安装指定目标
```

安装器将每个 skill 逐个链接到各工具的 skills 目录下，不覆盖工具原有的 skill。`AGENTS.md` 直接复制到目标位置。

## 更新

```bash
cd ~/dotfiles && git pull && python install.py
```

已正确链接的 skill 和内容未变的 AGENTS.md 会自动跳过。
