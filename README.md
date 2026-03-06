# dotfiles · 2agathon

我的 AI Vibe Coding 工程规范体系。
换工具不换规范，换项目不换工作方式。

## 包含什么

| 文件                       | 用途                             |
| -------------------------- | -------------------------------- |
| `AGENTS.md`                | 全局规范入口，所有工具启动时读取 |
| `skills/identity`          | 我的工作方式                     |
| `skills/principles`        | 跨语言工程原则                   |
| `skills/project-structure` | 目录和文件结构约定               |
| `skills/gen-agents`        | 生成项目 AGENTS.md               |
| `skills/vibe-plan`         | 新功能开始前的技术对齐           |
| `skills/docs`              | 写文档、决策记录                 |
| `skills/_template`         | 新 skill 的模板                  |

## 安装

**Linux / macOS**
```bash
git clone https://github.com/2agathon/dotfiles.git ~/dotfiles
bash ~/dotfiles/install.sh
```

**Windows**
```powershell
git clone https://github.com/2agathon/dotfiles.git $env:USERPROFILE\dotfiles
. $env:USERPROFILE\dotfiles\install.ps1
```

## 更新

**Linux / macOS**
```bash
cd ~/dotfiles && git pull && bash install.sh
```

**Windows**
```powershell
cd $env:USERPROFILE\dotfiles; git pull; . .\install.ps1
```

## 演进

规范不是一次性的，见 `EVOLUTION.md` 了解什么时候更新、更新什么。
