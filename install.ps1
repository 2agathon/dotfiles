$DOTFILES = Split-Path -Parent $MyInvocation.MyCommand.Path
$SKILLS = "$DOTFILES\skills"
$AGENTS = "$DOTFILES\AGENTS.md"

function Link-Skills {
    param($dst, $skillName = "skills")
    $target = "$dst\$skillName"
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    if (Test-Path $target) { Remove-Item $target -Recurse -Force }
    New-Item -ItemType Junction -Path $target -Target $SKILLS | Out-Null
    Write-Host "[dotfiles] linked: $target -> $SKILLS"
}

function Link-Agents {
    param($dst, $name = "AGENTS.md")
    $target = "$dst\$name"
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    if (Test-Path $target) { Remove-Item $target -Force }
    New-Item -ItemType SymbolicLink -Path $target -Target $AGENTS | Out-Null
    Write-Host "[dotfiles] linked: $target -> AGENTS.md"
}

# Claude Code
Link-Skills "$env:USERPROFILE\.claude"
Link-Agents "$env:USERPROFILE\.claude" -name "CLAUDE.md"

# Codex CLI
Link-Skills "$env:USERPROFILE\.codex"
Link-Agents "$env:USERPROFILE\.codex"

# Gemini CLI
Link-Skills "$env:USERPROFILE\.gemini"
Link-Agents "$env:USERPROFILE\.gemini"

# OpenCode（官方路径 ~/.config/opencode/skills，skill 目录名为复数）
Link-Skills "$env:USERPROFILE\.config\opencode"
Link-Agents "$env:USERPROFILE\.config\opencode"

# GLM [OPEN QUESTION: 确认 GLM 的全局配置路径后补充]
Write-Host "[dotfiles] GLM path not confirmed, skipping."

Write-Host "[dotfiles] Done."