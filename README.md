# dotfiles · 2agathon

我的 AI Vibe Coding 工程规范体系。
换工具不换规范，换项目不换工作方式。

## 包含什么

### 全局基准

| 文件              | 用途                             |
| ----------------- | -------------------------------- |
| `AGENTS.md`       | 全局规范入口，所有工具启动时读取 |
| `skills/identity` | 协作约定、标注体系、全局行为基准 |

### 工程执行

| 文件                       | 用途                   |
| -------------------------- | ---------------------- |
| `skills/principles`        | 跨语言工程原则         |
| `skills/project-structure` | 目录和文件结构约定     |
| `skills/vibe-plan`         | 新功能开始前的技术对齐 |

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

### 认识校准

| 文件                          | 用途                                 |
| ----------------------------- | ------------------------------------ |
| `skills/assumption-audit`     | 审计隐含前提、识别前提污染           |
| `skills/conversation-to-spec` | 把对话中的共识构造成可执行规格       |
| `skills/drift-detector`       | 检测系统演化中未被显式承认的边界变化 |
| `skills/role-lens`            | 识别主导透镜，引入挑战透镜暴露盲点   |
| `skills/self-rewrite`         | 旧自我叙述失效时生成可重入的改写记录 |

### 基础设施

| 文件          | 用途                   |
| ------------- | ---------------------- |
| `install.sh`  | Linux / macOS 安装脚本 |
| `install.ps1` | Windows 安装脚本       |
| `install.cmd` | Windows 兼容启动脚本   |

## 安装

**Linux / macOS**

```bash
git clone <your-private-dotfiles-repo> ~/dotfiles
bash ~/dotfiles/install.sh
```

**Windows**

```
git clone <your-private-dotfiles-repo> $env:USERPROFILE\dotfiles
. $env:USERPROFILE\dotfiles\install.ps1
```

安装脚本会安装或更新全局 `AGENTS.md`，并将其中引用的全局 skill 路径写成当前环境中的本地绝对路径，不再依赖远程 raw URL。

## 更新

**Linux / macOS**

```
cd ~/dotfiles && git pull && bash install.sh
```

**Windows**

```
cd $env:USERPROFILE\dotfiles; git pull; . .\install.ps1
```

更新后会重新安装全局 `AGENTS.md`，并刷新其中写入的本地 skill 路径。

## 演进

规范不是一次性的，见 `EVOLUTION.md` 了解什么时候更新、更新什么。
