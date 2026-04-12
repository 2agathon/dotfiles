# dotfiles · 2agathon

我的 AI Vibe Coding 工程规范体系。
换工具不换规范，换项目不换工作方式。

## 体系结构（速览）

规范按责任拆开，而不是按「文档类型」堆砌：

- **对齐与设计**：`identity`（常驻）、`vibe-plan`（写代码前的技术对齐与 task 粒度）。
- **代码生命周期**：`file-creation` → `code-modify` → `code-test`（按需）→ `git-commit`；跨会话用 `code-relay`。
- **迭代止损**：`bail-out` 在多轮修改中自动监测是否陷入沉没成本。
- **项目与记录**：`gen-agents`、`docs`、`decision-record`。
- **认识**：捕捉（`notes-protocol`、`notion-manager`、`knowledge-shaping`）与校准（`assumption-audit`、`conversation-to-spec`、`role-lens`、`drift-detector`、`self-rewrite`）；`tension-manifest` 负责 TM 头与版本链。
- **专项**：聊天管线（`chat-parser` / `chat-render`）、表格（`xlsx`）、页类型（`page-type-spec-generator`）。
- **工具链目录**：`skills/.system/` 存放与外部工具文档或安装器相关的 skill，与核心规范同仓维护但不参与安装。

完整触发表与路径约定见根目录 **`AGENTS.md`**。每个 skill 的触发词、决策点、控制方式见 **[`SKILLS-REFERENCE.md`](SKILLS-REFERENCE.md)**。

## 包含什么

### 全局基准

| 文件              | 用途                             |
| ----------------- | -------------------------------- |
| `AGENTS.md`       | 全局规范入口，所有工具启动时读取 |
| `skills/identity` | 协作约定、标注体系、全局行为基准 |

### 工程执行（设计 → 实现 → 验证 → 交付）

| 文件                  | 用途                                               |
| --------------------- | -------------------------------------------------- |
| `skills/principles`   | 跨语言工程原则                                     |
| `skills/vibe-plan`    | 新功能 / 模糊任务开始前的技术对齐与实现顺序        |
| `skills/file-creation`| 新建文件与目录的边界与命名自检                     |
| `skills/code-modify`  | 修改现有代码时的范围与不变量约束（改代码时默认生效） |
| `skills/code-test`    | 用户要求写测试时的质量约束                         |
| `skills/git-commit`   | 是否该提交、逻辑单元、message 与 push              |
| `skills/code-relay`   | 代码会话间交接信与收工回流                         |

### 迭代与止损

| 文件              | 用途                                       |
| ----------------- | ------------------------------------------ |
| `skills/bail-out` | 迭代修改中的止损信号与用户显式喊停         |

### 工程协作

| 文件                     | 用途                                             |
| ------------------------ | ------------------------------------------------ |
| `skills/gen-agents`      | 生成项目 AGENTS.md，并将所选 skill 带入项目      |
| `skills/docs`            | 说明性文档：README、接口文档、技术文档、维护文档 |
| `skills/decision-record` | 记录决策分叉：为什么选了这个而不是别的           |

### 认识捕捉

| 文件                       | 用途                                   |
| -------------------------- | -------------------------------------- |
| `skills/notes-protocol`    | 记笔记、整理认识、捕捉对话中的理解变化 |
| `skills/notion-manager`    | 管理 Notion 工作区                     |
| `skills/knowledge-shaping` | 把原始材料塑形为稳定的知识对象         |
| `skills/tension-manifest`  | TM 头版本与演化链（多 skill 依赖）     |

### 认识校准

| 文件                          | 用途                                 |
| ----------------------------- | ------------------------------------ |
| `skills/assumption-audit`     | 审计隐含前提、识别前提污染           |
| `skills/conversation-to-spec` | 把对话中的共识构造成可执行规格       |
| `skills/drift-detector`       | 检测系统演化中未被显式承认的边界变化 |
| `skills/role-lens`            | 识别主导透镜，引入挑战透镜暴露盲点   |
| `skills/self-rewrite`         | 旧自我叙述失效时生成可重入的改写记录 |

### 领域与专项

| 文件                             | 用途                         |
| -------------------------------- | ---------------------------- |
| `skills/chat-parser`             | 聊天导出 → 标准数据对象入口  |
| `skills/chat-render`             | 基于 parser 输出做可视化等   |
| `skills/xlsx`                    | 电子表格为主要输入或输出     |
| `skills/page-type-spec-generator`| 从业务 xlsx 生成页类型配置   |

### 工具链（`.system`）

| 路径                    | 用途（摘要）           |
| ----------------------- | ---------------------- |
| `skills/.system/openai-docs`   | OpenAI 官方文档与选型辅助 |
| `skills/.system/skill-creator` | 编写 skill 的指南         |
| `skills/.system/skill-installer` | 从列表或仓库安装 skill   |

### 基础设施

| 文件            | 用途                                    |
| --------------- | --------------------------------------- |
| `install.py`    | 跨平台安装脚本（Python 3）              |
| `targets.json`  | 安装目标配置（工具名称、路径、文件名）  |

## 安装

需要 Python 3.8+。首次运行会自动安装 `rich` 库。

```bash
git clone <your-private-dotfiles-repo> ~/dotfiles
python ~/dotfiles/install.py
```

交互模式会引导选择操作和目标。也可以用命令行参数：

```bash
python install.py                              # 交互模式
python install.py --dry-run                    # 预演，不真正修改
python install.py --uninstall                  # 卸载
python install.py --force                      # 覆盖已存在的非受管内容（先备份）
python install.py --target "Claude Code"       # 只安装指定目标
```

安装器会将每个 skill 逐个链接到各工具的 skills 目录下，不覆盖工具原有的 skill。`AGENTS.md` 直接复制到目标位置。

## 更新

```bash
cd ~/dotfiles && git pull && python install.py
```

已正确链接的 skill 和内容未变的 AGENTS.md 会自动跳过。

## 演进

规范不是一次性的，见 `EVOLUTION.md` 了解什么时候更新、更新什么、以及各 skill 出问题时应改哪份文件。
